"""Chef d'orchestre : le passage quotidien de toutes les poches.

Pour chaque poche : charge l'état sauvegardé, récupère les données, fait avancer le
moteur sur les barres nouvelles, enregistre les trades clos dans le journal, sauvegarde
l'état, puis écrit un rapport et envoie les alertes.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd

from . import alertes, journal_de_bord, risque
from .config import Config
from .moteur import Moteur


def passage(config: Config, source, dossier: str | Path = "agents", envoyer: bool = True) -> str:
    dossier = Path(dossier)
    (dossier / "etat").mkdir(parents=True, exist_ok=True)
    sections, messages, total, total_initial = [], [], 0.0, 0.0

    for poche in config.poches:
        chemin_etat = dossier / "etat" / f"{poche.nom}.json"
        etat = json.loads(chemin_etat.read_text(encoding="utf-8")) if chemin_etat.exists() else None
        m = Moteur(poche, etat)
        n_mouv, n_trades, n_refus = len(m.courtier.mouvements), len(m.courtier.trades), 0
        m.charger(source.historique(poche.univers, poche.style))
        m.executer()

        nouveaux = m.courtier.mouvements[n_mouv:]
        # Alertes : seulement la dernière séance (au premier passage, l'historique sert d'initialisation)
        derniere = str(m.derniere_date)[:10]
        recents = [x for x in nouveaux if x["date"][:10] == derniere]
        journal_de_bord.enregistrer(m.courtier.trades[n_trades:], dossier / "etat" / f"journal_{poche.nom}.csv")
        chemin_etat.write_text(json.dumps(m.etat(), indent=1, default=float), encoding="utf-8")

        messages += [alertes.formater(poche.nom, x) for x in recents]
        messages += [alertes.formater(poche.nom, {**o.__dict__, "prix": None, "motif": f"demain : {o.motif}"})
                     for o in m.courtier.ordres]
        sections.append(_section(poche, m, nouveaux, m.refus[n_refus:]))
        total += m.courtier.valeur(m.dernier_prix)
        total_initial += poche.capital

    entete = [
        f"# Rapport des agents · {date.today():%Y-%m-%d}",
        "",
        f"Valeur totale des poches : **{total:,.0f}** (capital de départ {total_initial:,.0f}, "
        f"{total / total_initial - 1:+.1%}). Argent fictif (courtier papier).",
        "",
    ]
    rapport = "\n".join(entete + sections)
    (dossier / "rapports").mkdir(parents=True, exist_ok=True)
    (dossier / "rapports" / f"{date.today():%Y-%m-%d}.md").write_text(rapport, encoding="utf-8")
    if envoyer:
        alertes.envoyer(messages)
    return rapport


def _section(poche, m: Moteur, nouveaux: list[dict], refus: list[dict]) -> str:
    c = m.courtier
    rendements = m.closes.pct_change().iloc[1:].tail(252)
    tab = risque.tableau(c, m.dernier_prix, rendements)
    lignes = [
        f"## {poche.nom} ({poche.style})",
        "",
        f"Dernière barre : {m.derniere_date}. Valeur {tab['valeur']:,.0f} · exposition {tab['exposition']:.0%} · risque ouvert {tab['risque_ouvert']:.1%} · "
        f"vol {tab['vol_annuelle']:.1%} · VaR 95 % 1 j {tab['var_95_1j']:.2%} · CVaR {tab['cvar_95_1j']:.2%} · "
        f"baisse depuis le plus haut {tab['valeur'] / m.plus_haut - 1:.1%}",
        "",
    ]
    if c.positions:
        lignes += ["| Ligne | Qté | Entrée | Dernier | Stop | P&L |", "| --- | --- | --- | --- | --- | --- |"]
        for s, p in c.positions.items():
            der = m.dernier_prix.get(s, p.prix_entree)
            stop = f"{p.stop:.2f}" if p.stop is not None else "–"
            lignes.append(f"| {s} | {p.quantite} | {p.prix_entree:.2f} | {der:.2f} | {stop} | "
                          f"{(der - p.prix_entree) * p.quantite:,.0f} |")
        lignes.append("")
    if c.ordres:
        lignes.append("Ordres pour la prochaine ouverture : " + ", ".join(
            f"{'achat' if o.quantite > 0 else 'vente'} {abs(o.quantite)} {o.symbole}" for o in c.ordres))
    if refus:
        derniers = {r["symbole"]: r["raison"] for r in refus}
        lignes.append("Derniers refus de l'agent Risque : " + ", ".join(f"{s} ({r})" for s, r in list(derniers.items())[-5:]))
    lignes.append(f"Nouvelles exécutions depuis le dernier passage : {len(nouveaux)}.")
    lignes.append("")
    return "\n".join(lignes)
