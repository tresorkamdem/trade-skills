"""Instantané JSON de l'état des poches, pour le tableau de bord et pour SESHAT.

`construire` rassemble en un seul dictionnaire (format `VERSION`) ce qu'écrivent les autres
commandes dans `<dossier>` : états et journaux des poches, backtest, alertes TradingView,
contrôle des données. `publier` l'envoie à SESHAT (le backoffice de MAÀT Analytics) par la
fonction Supabase `trading_ingest`, avec le jeton robot du compte : aucune clé de service.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .. import optim, portfolio
from . import budget, risque, signaux
from .config import Config, Poche

VERSION = 1
JOURS_COURBE = 750  # environ trois ans de points journaliers par poche


def construire(config: Config, dossier: str | Path, source=None) -> dict:
    dossier = Path(dossier)
    etats = {p.nom: _lire_json(dossier / "etat" / f"{p.nom}.json") for p in config.poches}
    backtest = _lire_json(dossier / "rapports" / "backtest.json") or {}
    donnees = _lire_json(dossier / "rapports" / "donnees.json") or []
    historiques = {}
    if source is not None:
        for p in config.poches:
            if p.style != "day":
                try:
                    historiques[p.nom] = source.historique(p.univers, p.style)
                except FileNotFoundError:
                    historiques[p.nom] = {}
    return {
        "version": VERSION,
        "genere": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "monnaie": "EUR",
        "poches": [_poche(p, etats.get(p.nom), historiques.get(p.nom)) for p in config.poches],
        "positions": [x for p in config.poches for x in _positions(p, etats.get(p.nom))],
        "ordres": [x for p in config.poches for x in _ordres(p, etats.get(p.nom))],
        "allocation": [a for p in config.poches if p.style == "long_terme"
                       and (a := allocation(p, historiques.get(p.nom), etats.get(p.nom))) is not None],
        "backtests": [_backtest(b) for b in backtest.get("poches", [])],
        "backtest_source": backtest.get("source"),
        "trades": _trades(config, dossier),
        "signaux": [x for p in config.poches if p.style == "signaux" for x in _signaux(p)],
        "donnees": donnees,
    }


def ecrire(instantane: dict, chemin: str | Path) -> Path:
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(instantane, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    return chemin


def publier(instantane: dict, url: str | None = None, cle: str | None = None, jeton: str | None = None) -> str:
    """Envoie l'instantané à SESHAT. Variables : SESHAT_SUPABASE_URL, SESHAT_SUPABASE_ANON_KEY, SESHAT_ROBOT_TOKEN.

    Renvoie l'identifiant du rapport créé dans SESHAT."""
    url = (url or os.environ.get("SESHAT_SUPABASE_URL", "")).strip().rstrip("/")
    # l'URL copiée depuis Supabase se termine parfois par /rest/v1 : on ne garde que la racine
    url = url.removesuffix("/rest/v1").rstrip("/")
    cle, jeton = (cle or os.environ.get("SESHAT_SUPABASE_ANON_KEY", "")).strip(), (jeton or os.environ.get("SESHAT_ROBOT_TOKEN", "")).strip()
    if not (url and cle and jeton):
        raise RuntimeError("SESHAT_SUPABASE_URL, SESHAT_SUPABASE_ANON_KEY et SESHAT_ROBOT_TOKEN sont nécessaires")
    corps = json.dumps({"p_token": jeton, "p_payload": instantane}, ensure_ascii=False, allow_nan=False).encode()
    req = urllib.request.Request(
        f"{url}/rest/v1/rpc/trading_ingest",
        data=corps,
        headers={"content-type": "application/json", "apikey": cle, "authorization": f"Bearer {cle}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode() or "null")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"SESHAT a refusé l'envoi ({e.code}) : {_explication(e.code)}\n"
                           f"Adresse appelée : {url}/rest/v1/rpc/trading_ingest\n"
                           f"Réponse de Supabase : {e.read().decode(errors='replace')[:500]}") from None


def _explication(code: int) -> str:
    return {
        401: "clé SESHAT_SUPABASE_ANON_KEY refusée (prendre la clé anon « eyJ… » du projet)",
        403: "jeton SESHAT_ROBOT_TOKEN inconnu (le recopier depuis Radar → Automatique)",
        404: "fonction trading_ingest introuvable : migration 12 non exécutée, ou mauvais projet dans SESHAT_SUPABASE_URL",
    }.get(code, "voir la réponse ci-dessous")


# --- morceaux -----------------------------------------------------------------------------------

def valeur(etat: dict) -> float:
    c, prix = etat["courtier"], etat["dernier_prix"]
    return c["cash"] + sum(p["quantite"] * prix.get(s, p["prix_entree"]) for s, p in c["positions"].items())


def _poche(p: Poche, etat: dict | None, historique: dict | None) -> dict:
    base = {"nom": p.nom, "style": p.style, "capital": p.capital, "univers": p.univers}
    if not etat:
        return {**base, "lancee": False, "valeur": p.capital, "courbe": []}
    v = valeur(etat)
    s = pd.Series([x for _, x in etat["historique"]], index=pd.to_datetime([d for d, _ in etat["historique"]]), dtype=float)
    s = s.groupby(s.index.normalize()).last().tail(JOURS_COURBE)
    out = {
        **base,
        "lancee": True,
        "valeur": _r(v),
        "plus_haut": _r(etat["plus_haut"]),
        "derniere_barre": etat["derniere_date"],
        "cash": _r(etat["courtier"]["cash"]),
        "coupe_circuit": etat.get("coupe_circuit") is not None,
        "courbe": [[f"{t:%Y-%m-%d}", _r(x)] for t, x in s.items()],
    }
    if historique:
        from .courtier import CourtierPapier
        closes = pd.DataFrame({k: df["close"] for k, df in historique.items()}).sort_index().ffill()
        tab = risque.tableau(CourtierPapier.depuis_dict(etat["courtier"]), etat["dernier_prix"],
                             closes.pct_change().iloc[1:].tail(252))
        out["risque"] = {k: _r(x, 4) for k, x in tab.items() if k != "valeur"}
    return out


def _positions(p: Poche, etat: dict | None) -> list[dict]:
    if not etat:
        return []
    v, prix = valeur(etat), etat["dernier_prix"]
    out = []
    for s, pos in etat["courtier"]["positions"].items():
        der = prix.get(s, pos["prix_entree"])
        out.append({
            "poche": p.nom, "symbole": s, "quantite": pos["quantite"], "entree": _r(pos["prix_entree"], 4),
            "date_entree": pos["date_entree"][:10], "dernier": _r(der, 4),
            "stop": None if pos["stop"] is None else _r(pos["stop"], 4),
            "pnl": _r((der - pos["prix_entree"]) * pos["quantite"]), "poids": _r(pos["quantite"] * der / v, 4),
            "setup": pos.get("setup") or "",
        })
    return out


def _ordres(p: Poche, etat: dict | None) -> list[dict]:
    if not etat:
        return []
    return [{"poche": p.nom, "symbole": o["symbole"], "quantite": o["quantite"], "motif": o["motif"]}
            for o in etat["courtier"]["ordres"]]


def allocation(p: Poche, historique: dict | None, etat: dict | None) -> dict | None:
    """Poids actuels de la poche face à GMV Ledoit-Wolf, parité de risque et 1/n,
    avec la volatilité attendue et la plus grosse part du risque de chacun."""
    if not historique:
        return None
    closes = pd.DataFrame({s: df["close"] for s, df in historique.items()}).sort_index().ffill()
    R = closes.pct_change().iloc[1:].tail(p.param("fenetre")).dropna(axis=1)
    if len(R) < 30 or R.shape[1] < 2:
        return None
    sigma = portfolio.cov_ledoit_wolf(R.to_numpy())
    methodes = {}
    for nom, m in [("gmv_lw", "gmv_lw"), ("parite_risque", "parite_risque"), ("egal", "egal")]:
        q = Poche(p.nom, "long_terme", p.capital, list(R.columns), poids_max=p.poids_max, params={"methode": m})
        methodes[nom] = budget.poids_cibles(R, q)
    if etat:
        prix, pos = etat["dernier_prix"], etat["courtier"]["positions"]
        montants = pd.Series({s: pos[s]["quantite"] * prix.get(s, 0.0) for s in pos}, dtype=float)
        methodes = {"actuel": (montants / valeur(etat)).reindex(R.columns).fillna(0.0), **methodes}

    def mesures(w: pd.Series) -> dict:
        x = w.to_numpy()
        if x.sum() <= 0:
            return {"vol": 0.0, "part_risque_max": 0.0}
        return {"vol": _r(float(np.sqrt(x @ sigma @ x * 252)), 4),
                "part_risque_max": _r(float(optim.risk_contributions(x, sigma).max()), 4)}

    return {
        "poche": p.nom,
        "lignes": list(R.columns),
        "fenetre": len(R),
        "poids_max": p.poids_max,
        "methodes": [{"nom": n, "poids": [_r(float(w[s]), 4) for s in R.columns], **mesures(w)} for n, w in methodes.items()],
    }


def _backtest(b: dict) -> dict:
    """Courbes réduites à un point par semaine : assez pour un graphique, léger à envoyer."""
    def hebdo(points):
        if not points:
            return []
        s = pd.Series([v for _, v in points], index=pd.to_datetime([d for d, _ in points]))
        s = s.resample("W-FRI").last().dropna()
        return [[f"{t:%Y-%m-%d}", _r(v)] for t, v in s.items()]

    return {**{k: v for k, v in b.items() if k not in ("courbe", "reference")},
            "courbe": hebdo(b.get("courbe")), "reference": hebdo(b.get("reference"))}


def _trades(config: Config, dossier: Path, n: int = 50) -> list[dict]:
    morceaux = []
    for p in config.poches:
        chemin = dossier / "etat" / f"journal_{p.nom}.csv"
        if chemin.exists():
            df = pd.read_csv(chemin)
            df.insert(0, "poche", p.nom)
            morceaux.append(df)
    if not morceaux:
        return []
    df = pd.concat(morceaux).sort_values("date_sortie").tail(n).iloc[::-1]
    out = []
    for t in df.itertuples():
        r = (t.sortie - t.entree) / (t.entree - t.stop) if t.entree != t.stop else 0.0
        out.append({"poche": t.poche, "symbole": t.actif, "date": str(t.date)[:10], "date_sortie": str(t.date_sortie)[:16],
                    "entree": _r(t.entree, 4), "sortie": _r(t.sortie, 4), "quantite": int(t.quantite),
                    "r": _r(r, 3), "pnl": _r((t.sortie - t.entree) * t.quantite - t.frais), "setup": str(t.setup),
                    "motif": str(t.note)})
    return out


def _signaux(p: Poche, n: int = 30) -> list[dict]:
    df = signaux.pour_poche(signaux.de_la_poche(p), p.nom)
    return [{"poche": p.nom, "recu": f"{a.recu:%Y-%m-%dT%H:%M}Z", "type": a.type, "symbole": a.symbole,
             "prix": _r(a.prix, 4), "stop": _r(a.stop, 4), "strategie": a.strategie, "hors_univers": a.symbole not in p.univers}
            for a in df.tail(n).iloc[::-1].itertuples()]


def _r(x, n: int = 2):
    """Arrondi JSON : None pour les valeurs manquantes ou infinies."""
    if x is None:
        return None
    x = float(x)
    return round(x, n) if np.isfinite(x) else None


def _lire_json(chemin: Path):
    return json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else None
