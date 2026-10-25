"""Agent Journal : enregistre les trades clos et fait le bilan, avec le format de `journal/modele_journal.csv`."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .. import journal

COLONNES = journal.COLUMNS + ["date_sortie"]


def enregistrer(trades: list[dict], chemin: str | Path) -> None:
    """Ajoute les trades à la fin du journal (crée le fichier avec l'en-tête si besoin)."""
    if not trades:
        return
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(trades, columns=COLONNES).to_csv(chemin, mode="a", header=not chemin.exists(), index=False)


def bilan(trades: pd.DataFrame | list[dict]) -> str:
    """Statistiques en R, par setup, et ce qu'il faut en conclure (ou pas encore)."""
    df = pd.DataFrame(trades)
    if df.empty:
        return "Aucun trade clos pour l'instant."
    df["date"] = pd.to_datetime(df["date"])
    df = journal.prepare(df)
    st = journal.stats(df)
    lignes = [
        f"- Trades : {st['trades']}",
        f"- Taux de réussite : {st['taux_de_reussite']:.0%}",
        f"- Gain moyen : {st['gain_moyen_R']:.2f} R ; perte moyenne : {st['perte_moyenne_R']:.2f} R",
        f"- Espérance : {st['esperance_R']:.2f} R par trade",
        f"- P&L total : {st['pnl_total']:,.0f} ; profit factor : {st['profit_factor']:.2f}",
    ]
    if st["trades"] < 30:
        lignes.append("- ⚠️ Moins de 30 trades : trop tôt pour conclure quoi que ce soit.")
    elif st["esperance_R"] <= 0:
        lignes.append("- ⚠️ Espérance négative : ne pas passer en argent réel avec ces règles.")
    par_setup = journal.by_setup(df)
    lignes.append("")
    lignes.append("| Setup | Trades | R moyen | R total |")
    lignes.append("| --- | --- | --- | --- |")
    lignes += [f"| {s} | {int(r.trades)} | {r.r_moyen:.2f} | {r.r_total:.1f} |" for s, r in par_setup.iterrows()]
    return "\n".join(lignes)
