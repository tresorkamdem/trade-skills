"""Agent Signaux : transforme les alertes TradingView en propositions pour la poche `signaux`.

`node/webhook.mjs` ajoute chaque alerte reçue à `signaux.jsonl` (une ligne JSON par alerte).
Ce module lit ce fichier, traduit le code TradingView (`XETR:SXR8`) en code Yahoo (`SXR8.DE`)
et donne, pour chaque barre journalière, les alertes reçues depuis la barre précédente.
L'alerte reçue le jour J est exécutée à l'ouverture du jour suivant, comme les autres poches.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

# Suffixe Yahoo de chaque bourse TradingView (préfixe avant les deux-points)
SUFFIXES = {
    "XETR": ".DE", "FWB": ".F", "GETTEX": ".DE", "LSE": ".L", "SIX": ".SW", "EURONEXT": ".PA",
    "MIL": ".MI", "BME": ".MC", "NASDAQ": "", "NYSE": "", "AMEX": "", "BATS": "", "CBOE": "", "ARCA": "",
}
ENTREES = {"achat", "buy", "long"}
SORTIES = {"sortie", "vente", "sell", "exit"}
COLONNES = ["recu", "date", "symbole", "type", "prix", "stop", "poche", "strategie"]


def normaliser_symbole(code: str) -> str:
    """`XETR:SXR8` → `SXR8.DE`, `NASDAQ:AAPL` → `AAPL` ; un code sans bourse est gardé tel quel."""
    code = str(code).strip().upper()
    if ":" not in code:
        return code
    bourse, ticker = code.split(":", 1)
    return ticker + SUFFIXES.get(bourse, "")


def charger(chemin: str | Path) -> pd.DataFrame:
    """Alertes du fichier JSONL, triées par heure de réception. Fichier absent : tableau vide.

    Les lignes illisibles ou sans symbole sont ignorées (le webhook enregistre tout ce qu'il reçoit)."""
    chemin = Path(chemin)
    lignes = []
    if chemin.exists():
        for brut in chemin.read_text(encoding="utf-8").splitlines():
            try:
                a = json.loads(brut)
            except json.JSONDecodeError:
                continue
            if not isinstance(a, dict) or not a.get("symbole") or not a.get("recu"):
                continue
            type_ = str(a.get("type", "")).lower()
            lignes.append({
                "recu": pd.to_datetime(a["recu"], utc=True).tz_convert(None),  # heure UTC
                "symbole": normaliser_symbole(a["symbole"]),
                "type": "achat" if type_ in ENTREES else "sortie" if type_ in SORTIES else type_,
                "prix": _nombre(a.get("prix")),
                "stop": _nombre(a.get("stop")),
                "poche": a.get("poche"),
                "strategie": a.get("strategie") or "tradingview",
            })
    df = pd.DataFrame(lignes, columns=[c for c in COLONNES if c != "date"])
    df.insert(1, "date", pd.to_datetime(df["recu"]).dt.normalize())
    return df.sort_values("recu", kind="stable").reset_index(drop=True)


def _nombre(x) -> float | None:
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return x if x == x else None


def pour_poche(signaux: pd.DataFrame, poche: str) -> pd.DataFrame:
    """Alertes destinées à cette poche : celles sans poche précisée, ou avec ce nom de poche."""
    if signaux.empty:
        return signaux
    return signaux[signaux["poche"].isna() | (signaux["poche"] == poche)]


def entre(signaux: pd.DataFrame, debut: pd.Timestamp | None, fin: pd.Timestamp) -> pd.DataFrame:
    """Alertes reçues après la barre `debut` (exclue) et jusqu'au jour de la barre `fin` (inclus).

    Sans barre précédente, on ne remonte pas plus de 5 jours."""
    if signaux.empty:
        return signaux
    fin = fin.normalize()
    debut = fin - pd.Timedelta(days=5) if debut is None else debut.normalize()
    return signaux[(signaux["date"] > debut) & (signaux["date"] <= fin)]


def de_la_poche(poche) -> pd.DataFrame | None:
    """Alertes du fichier de la poche si elle est de style `signaux`, sinon None."""
    return charger(poche.param("fichier")) if poche.style == "signaux" else None
