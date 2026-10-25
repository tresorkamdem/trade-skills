"""Tableau de bord : une page HTML autonome (sans connexion ni dépendance) sur l'état des poches.

Lit ce qu'écrivent les autres commandes dans `<dossier>` :
- `etat/<poche>.json` et `etat/journal_<poche>.csv` (passage quotidien) ;
- `rapports/backtest.json` (Time Machine) ;
- le fichier d'alertes des poches `signaux`.
Avec une source de données, il ajoute l'allocation du long terme comparée à GMV Ledoit-Wolf,
parité de risque et 1/n, avec la volatilité attendue de chacune.
"""
from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from . import instantane, signaux
from .config import Config, Poche

COULEURS = ["--c1", "--c2", "--c3", "--c4", "--c5"]


def generer(config: Config, dossier: str | Path, source=None) -> Path:
    dossier = Path(dossier)
    etats = {p.nom: _lire_json(dossier / "etat" / f"{p.nom}.json") for p in config.poches}
    backtest = _lire_json(dossier / "rapports" / "backtest.json")

    corps = [_entete(config, etats)]
    if any(etats.values()):
        corps.append(_courbes_suivi(config, etats))
        corps.append(_positions(config, etats))
    else:
        corps.append('<section><p class="vide">Pas encore de passage quotidien. Lance '
                     '<code>python -m tradeskills.agents quotidien</code> pour remplir ce tableau.</p></section>')
    if source is not None:
        corps += [_allocation(p, source, etats.get(p.nom)) for p in config.poches if p.style == "long_terme"]
    if backtest:
        corps.append(_backtest(backtest))
    corps.append(_trades(config, dossier))
    corps += [_signaux(p) for p in config.poches if p.style == "signaux"]

    page = _GABARIT.replace("{{genere}}", f"{datetime.now():%d/%m/%Y %H:%M}").replace("{{corps}}", "\n".join(corps))
    chemin = dossier / "tableau.html"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(page, encoding="utf-8")
    return chemin


# --- sections ---------------------------------------------------------------------------------

def _entete(config: Config, etats: dict) -> str:
    cartes, total, initial = [], 0.0, 0.0
    for p in config.poches:
        e = etats.get(p.nom)
        valeur = _valeur(e) if e else p.capital
        total, initial = total + valeur, initial + p.capital
        baisse = valeur / e["plus_haut"] - 1 if e else 0.0
        derniere = (e or {}).get("derniere_date") or "pas encore lancée"
        cartes.append(
            f'<div class="carte"><div class="etiquette">{_e(p.nom)} · {_e(p.style)}</div>'
            f'<div class="valeur">{valeur:,.0f}</div>'
            f'<div class="{_signe(valeur / p.capital - 1)}">{valeur / p.capital - 1:+.1%}</div>'
            f'<div class="petit">baisse depuis le plus haut {baisse:.1%}<br>dernière barre {_e(str(derniere)[:16])}</div></div>'
        )
    tot = (f'<div class="carte total"><div class="etiquette">Total des poches</div><div class="valeur">{total:,.0f}</div>'
           f'<div class="{_signe(total / initial - 1)}">{total / initial - 1:+.1%}</div>'
           f'<div class="petit">capital de départ {initial:,.0f}</div></div>')
    return f'<section><div class="cartes">{tot}{"".join(cartes)}</div></section>'


def _courbes_suivi(config: Config, etats: dict) -> str:
    series = {}
    for p in config.poches:
        e = etats.get(p.nom)
        if e and e["historique"]:
            s = pd.Series([v for _, v in e["historique"]], index=pd.to_datetime([d for d, _ in e["historique"]]))
            s = s.groupby(s.index.normalize()).last()
            series[p.nom] = (s / p.capital - 1) * 100
    return _section("Performance du suivi papier (%)", _graphique(series, suffixe=" %"))


def _positions(config: Config, etats: dict) -> str:
    lignes = []
    for p in config.poches:
        e = etats.get(p.nom)
        if not e:
            continue
        prix = e["dernier_prix"]
        for s, pos in e["courtier"]["positions"].items():
            der = prix.get(s, pos["prix_entree"])
            pnl = (der - pos["prix_entree"]) * pos["quantite"]
            stop = f'{pos["stop"]:.2f}' if pos["stop"] is not None else "–"
            lignes.append(
                f"<tr><td>{_e(p.nom)}</td><td>{_e(s)}</td><td>{pos['quantite']}</td><td>{pos['prix_entree']:.2f}</td>"
                f"<td>{der:.2f}</td><td>{stop}</td><td class='{_signe(pnl)}'>{pnl:,.0f}</td>"
                f"<td>{pos['quantite'] * der / _valeur(e):.0%}</td></tr>"
            )
        for o in e["courtier"]["ordres"]:
            sens = "achat" if o["quantite"] > 0 else "vente"
            lignes.append(f"<tr class='attente'><td>{_e(p.nom)}</td><td>{_e(o['symbole'])}</td>"
                          f"<td colspan='6'>ordre en attente : {sens} {abs(o['quantite'])} ({_e(o['motif'])})</td></tr>")
    if not lignes:
        return _section("Positions", '<p class="vide">Aucune position ouverte.</p>')
    tete = "<tr><th>Poche</th><th>Ligne</th><th>Qté</th><th>Entrée</th><th>Dernier</th><th>Stop</th><th>P&amp;L</th><th>Poids</th></tr>"
    return _section("Positions", f"<div class='defile'><table>{tete}{''.join(lignes)}</table></div>")


def _allocation(poche: Poche, source, etat: dict | None) -> str:
    """Poids actuels de la poche face aux trois méthodes, avec volatilité et contributions au risque."""
    donnees = source.historique(poche.univers, "long_terme")
    if not donnees:
        return ""
    a = instantane.allocation(poche, donnees, etat)
    if a is None:
        return _section(f"Allocation · {poche.nom}", '<p class="vide">Pas assez d\'historique.</p>')
    noms = {"actuel": "Poche actuelle", "gmv_lw": "GMV Ledoit-Wolf", "parite_risque": "Parité de risque", "egal": "1/n"}
    tete = "<tr><th>Ligne</th>" + "".join(f"<th>{_e(noms[m['nom']])}</th>" for m in a["methodes"]) + "</tr>"
    corps = [f"<tr><td>{_e(s)}</td>" + "".join(f"<td>{_barre(m['poids'][i])}</td>" for m in a["methodes"]) + "</tr>"
             for i, s in enumerate(a["lignes"])]
    corps.append("<tr class='pied'><td>Volatilité attendue</td>" + "".join(f"<td>{m['vol']:.1%}</td>" for m in a["methodes"]) + "</tr>")
    corps.append("<tr class='pied'><td>Plus grosse part du risque</td>"
                 + "".join(f"<td>{m['part_risque_max']:.0%}</td>" for m in a["methodes"]) + "</tr>")
    note = (f"<p class='petit'>Covariance Ledoit-Wolf sur les {a['fenetre']} derniers jours, poids plafonnés à {poche.poids_max:.0%}. "
            "GMV minimise la volatilité ; la parité de risque égalise la part de risque de chaque ligne ; "
            "1/n est la référence qui, dans ta thèse, restait compétitive en Sharpe.</p>")
    return _section(f"Allocation · {poche.nom}", f"<div class='defile'><table>{tete}{''.join(corps)}</table></div>{note}")


def _backtest(bt: dict) -> str:
    blocs = []
    for p in bt["poches"]:
        r = p["resume"]
        ic = p["sharpe_ic"]
        ic_txt = "–" if None in ic else f"[{ic[0]:.2f} ; {ic[1]:.2f}]"
        verdict = "non significatif" if None in ic or ic[0] <= 0 <= ic[1] else "significatif"
        esp = "–" if p["esperance_R"] is None else f"{p['esperance_R']:.2f} R"
        lignes = "".join(
            f"<tr><td>{_e(k.replace('_', ' '))}</td><td>{_fmt(k, v['poche'])}</td><td>{_fmt(k, v['reference_1/n'])}</td></tr>"
            for k, v in r.items()
        )
        series = {p["nom"]: _serie(p["courbe"]), "référence 1/n": _serie(p["reference"])}
        blocs.append(
            f"<div class='bloc'><h3>{_e(p['nom'])} <span class='petit'>{p['debut']} → {p['fin']}</span></h3>"
            f"{_graphique(series, hauteur=160)}"
            f"<table><tr><th>Mesure</th><th>Poche</th><th>Réf. 1/n</th></tr>{lignes}</table>"
            f"<p class='petit'>Sharpe IC 95 % {ic_txt} ({verdict}) · {p['trades']} trades · espérance {esp}</p></div>"
        )
    source = bt.get("source", "")
    alerte = ("<p class='alerte'>Backtest sur cours simulés : les résultats ne disent rien des règles.</p>"
              if source == "simulee" else "")
    return _section(f"Time Machine · source {_e(source)}", alerte + f"<div class='grille'>{''.join(blocs)}</div>")


def _trades(config: Config, dossier: Path) -> str:
    morceaux = []
    for p in config.poches:
        chemin = dossier / "etat" / f"journal_{p.nom}.csv"
        if chemin.exists():
            df = pd.read_csv(chemin)
            df.insert(0, "poche", p.nom)
            morceaux.append(df)
    if not morceaux:
        return _section("Derniers trades clos", '<p class="vide">Aucun trade clos pour l\'instant.</p>')
    df = pd.concat(morceaux).sort_values("date_sortie").tail(15).iloc[::-1]
    lignes = []
    for t in df.itertuples():
        r = (t.sortie - t.entree) / (t.entree - t.stop) if t.entree != t.stop else 0.0
        lignes.append(f"<tr><td>{_e(t.poche)}</td><td>{_e(t.actif)}</td><td>{_e(str(t.date))}</td>"
                      f"<td>{_e(str(t.date_sortie)[:16])}</td><td>{t.entree:.2f}</td><td>{t.sortie:.2f}</td>"
                      f"<td class='{_signe(r)}'>{r:+.2f} R</td><td>{_e(t.note)}</td></tr>")
    tete = "<tr><th>Poche</th><th>Ligne</th><th>Entrée le</th><th>Sortie le</th><th>Entrée</th><th>Sortie</th><th>R</th><th>Motif</th></tr>"
    return _section("Derniers trades clos", f"<div class='defile'><table>{tete}{''.join(lignes)}</table></div>")


def _signaux(poche: Poche) -> str:
    df = signaux.pour_poche(signaux.de_la_poche(poche), poche.nom)
    if df.empty:
        return _section(f"Alertes TradingView · {poche.nom}",
                        f"<p class='vide'>Aucune alerte dans <code>{_e(poche.param('fichier'))}</code>. "
                        "Voir node/README.md pour brancher TradingView.</p>")
    lignes = []
    for a in df.tail(15).iloc[::-1].itertuples():
        hors = "" if a.symbole in poche.univers else " <span class='petit'>(hors univers)</span>"
        lignes.append(f"<tr><td>{a.recu:%d/%m %H:%M}</td><td>{_e(a.type)}</td><td>{_e(a.symbole)}{hors}</td>"
                      f"<td>{'' if a.prix is None or a.prix != a.prix else f'{a.prix:.2f}'}</td>"
                      f"<td>{'' if a.stop is None or a.stop != a.stop else f'{a.stop:.2f}'}</td><td>{_e(a.strategie)}</td></tr>")
    tete = "<tr><th>Reçue (UTC)</th><th>Type</th><th>Ligne</th><th>Prix</th><th>Stop</th><th>Stratégie</th></tr>"
    return _section(f"Alertes TradingView · {poche.nom}", f"<div class='defile'><table>{tete}{''.join(lignes)}</table></div>")


# --- outils -----------------------------------------------------------------------------------

def _graphique(series: dict[str, pd.Series], hauteur: int = 220, suffixe: str = "") -> str:
    """Courbes en SVG inline, une couleur par série, légende en texte."""
    series = {k: v.dropna() for k, v in series.items() if len(v.dropna()) > 1}
    if not series:
        return '<p class="vide">Pas encore assez de points pour une courbe.</p>'
    largeur, marge = 640, 44
    debut = min(s.index[0] for s in series.values())
    fin = max(s.index[-1] for s in series.values())
    bas = min(s.min() for s in series.values())
    haut = max(s.max() for s in series.values())
    if haut == bas:
        haut, bas = haut + 1, bas - 1
    duree = max((fin - debut).total_seconds(), 1)

    def x(t):
        return marge + (largeur - marge - 8) * (t - debut).total_seconds() / duree

    def y(v):
        return 8 + (hauteur - 30) * (haut - v) / (haut - bas)

    traits = []
    for i, (nom, s) in enumerate(series.items()):
        points = " ".join(f"{x(t):.1f},{y(v):.1f}" for t, v in s.items())
        traits.append(f'<polyline points="{points}" fill="none" stroke="var({COULEURS[i % len(COULEURS)]})" '
                      f'stroke-width="2" vector-effect="non-scaling-stroke"><title>{_e(nom)}</title></polyline>')
    zero = f'<line x1="{marge}" x2="{largeur - 8}" y1="{y(0):.1f}" y2="{y(0):.1f}" class="zero"/>' if bas < 0 < haut else ""
    axes = (f'<text x="{marge - 6}" y="{y(haut) + 4:.1f}" text-anchor="end">{haut:,.0f}{suffixe}</text>'
            f'<text x="{marge - 6}" y="{y(bas):.1f}" text-anchor="end">{bas:,.0f}{suffixe}</text>'
            f'<text x="{marge}" y="{hauteur - 4}">{debut:%d/%m/%Y}</text>'
            f'<text x="{largeur - 8}" y="{hauteur - 4}" text-anchor="end">{fin:%d/%m/%Y}</text>')
    legende = "".join(f'<span><i style="background:var({COULEURS[i % len(COULEURS)]})"></i>{_e(n)}</span>'
                      for i, n in enumerate(series))
    return (f'<svg viewBox="0 0 {largeur} {hauteur}" class="graphique" role="img">{zero}{"".join(traits)}{axes}</svg>'
            f'<div class="legende">{legende}</div>')


def _serie(points: list) -> pd.Series:
    return pd.Series([v for _, v in points], index=pd.to_datetime([d for d, _ in points]))


def _section(titre: str, contenu: str) -> str:
    return f"<section><h2>{_e(titre)}</h2>{contenu}</section>"


def _barre(w: float) -> str:
    return f"<div class='poids'><span style='width:{max(w, 0) * 100:.1f}%'></span><b>{w:.0%}</b></div>"


def _fmt(cle: str, v) -> str:
    if v is None:
        return "–"
    return f"{v:.2f}" if cle in ("sharpe", "sortino", "calmar") else f"{v:.1%}"


def _valeur(etat: dict) -> float:
    return instantane.valeur(etat)


def _signe(x: float) -> str:
    return "pos" if x > 0 else "neg" if x < 0 else ""


def _e(x) -> str:
    return html.escape(str(x))


def _lire_json(chemin: Path) -> dict | None:
    return json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else None


_GABARIT = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tableau des poches</title>
<style>
:root { --fond:#f7f7f5; --carte:#fff; --texte:#1d1d1b; --doux:#6b6b66; --trait:#e3e2dd; --pos:#1a7f4b; --neg:#c0392b;
  --c1:#2f6fd6; --c2:#d9822b; --c3:#2a9d8f; --c4:#8e5bd1; --c5:#c2456b; color-scheme: light; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --fond:#161615; --carte:#1f1f1d; --texte:#ecebe6;
  --doux:#a3a29b; --trait:#34332f; --pos:#4cc38a; --neg:#ef6b5b; --c1:#6ea0ff; --c2:#f0a35a; --c3:#4fc4b5; --c4:#b38cf0; --c5:#f07a9b; color-scheme: dark; } }
:root[data-theme="dark"] { --fond:#161615; --carte:#1f1f1d; --texte:#ecebe6; --doux:#a3a29b; --trait:#34332f; --pos:#4cc38a;
  --neg:#ef6b5b; --c1:#6ea0ff; --c2:#f0a35a; --c3:#4fc4b5; --c4:#b38cf0; --c5:#f07a9b; color-scheme: dark; }
* { box-sizing: border-box; }
body { margin:0; background:var(--fond); color:var(--texte); font:15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 1100px; margin: 0 auto; padding: 24px 16px 48px; }
h1 { font-size: 1.5rem; margin: 0 0 4px; } h2 { font-size: 1.1rem; margin: 0 0 12px; } h3 { font-size: 1rem; margin: 0 0 8px; }
section { background:var(--carte); border:1px solid var(--trait); border-radius:12px; padding:16px; margin-top:16px; }
.cartes { display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap:12px; }
.carte { border:1px solid var(--trait); border-radius:10px; padding:12px; }
.carte.total { border-color: var(--c1); }
.etiquette, .petit, .vide { color:var(--doux); font-size:.85rem; }
.valeur { font-size:1.4rem; font-weight:600; font-variant-numeric: tabular-nums; }
.pos { color:var(--pos); } .neg { color:var(--neg); }
.defile { overflow-x:auto; }
table { width:100%; border-collapse:collapse; font-variant-numeric: tabular-nums; font-size:.9rem; }
th, td { text-align:left; padding:6px 8px; border-bottom:1px solid var(--trait); white-space:nowrap; }
th { color:var(--doux); font-weight:500; }
tr.attente td { color:var(--doux); font-style:italic; } tr.pied td { font-weight:600; }
.poids { position:relative; min-width:90px; height:20px; background:var(--fond); border-radius:4px; overflow:hidden; }
.poids span { position:absolute; inset:0 auto 0 0; background:var(--c1); opacity:.35; }
.poids b { position:relative; padding-left:6px; font-weight:500; font-size:.85rem; }
.graphique { width:100%; height:auto; display:block; }
.graphique text { fill:var(--doux); font-size:11px; } .graphique .zero { stroke:var(--trait); stroke-dasharray:4 4; }
.legende { display:flex; flex-wrap:wrap; gap:12px; font-size:.85rem; color:var(--doux); margin-top:4px; }
.legende i { display:inline-block; width:10px; height:10px; border-radius:2px; margin-right:6px; }
.grille { display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap:16px; }
.alerte { background:color-mix(in srgb, var(--c2) 15%, transparent); padding:8px 12px; border-radius:8px; }
code { font-size:.85em; }
</style>
</head>
<body>
<main>
<h1>Tableau des poches</h1>
<div class="petit">Argent fictif (courtier papier) · généré le {{genere}} · ce n'est pas un conseil d'investissement</div>
{{corps}}
</main>
</body>
</html>
"""
