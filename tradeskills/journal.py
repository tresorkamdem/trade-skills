"""Statistiques d'un journal de trading (voir `journal/modele_journal.csv`).

Usage : python -m tradeskills.journal journal/modele_journal.csv
"""
from __future__ import annotations

import sys

import pandas as pd

from .risk import expectancy, r_multiple

COLUMNS = ["date", "actif", "sens", "setup", "entree", "stop", "sortie", "quantite", "frais", "note"]


def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    missing = set(COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes : {sorted(missing)}")
    direction = df["sens"].str.lower().map({"achat": 1, "vente": -1})
    if direction.isna().any():
        raise ValueError("La colonne 'sens' doit valoir 'achat' ou 'vente'")
    df["pnl"] = direction * (df["sortie"] - df["entree"]) * df["quantite"] - df["frais"]
    df["r"] = [r_multiple(e, s, x) for e, s, x in zip(df["entree"], df["stop"], df["sortie"])]
    return df


def stats(df: pd.DataFrame) -> dict[str, float]:
    wins, losses = df[df["r"] > 0], df[df["r"] <= 0]
    win_rate = len(wins) / len(df)
    avg_win = wins["r"].mean() if len(wins) else 0.0
    avg_loss = -losses["r"].mean() if len(losses) else 0.0
    equity = df["pnl"].cumsum()
    return {
        "trades": len(df),
        "taux_de_reussite": win_rate,
        "gain_moyen_R": avg_win,
        "perte_moyenne_R": avg_loss,
        "esperance_R": expectancy(win_rate, avg_win, avg_loss) if avg_loss else df["r"].mean(),
        "pnl_total": equity.iloc[-1],
        "pire_baisse_pnl": (equity - equity.cummax()).min(),
        "profit_factor": wins["pnl"].sum() / -losses["pnl"].sum() if len(losses) else float("inf"),
    }


def by_setup(df: pd.DataFrame) -> pd.DataFrame:
    """Quel setup fonctionne vraiment ? Nombre de trades, R moyen et total par setup."""
    return df.groupby("setup")["r"].agg(trades="count", r_moyen="mean", r_total="sum").sort_values("r_total")


if __name__ == "__main__":
    journal = load(sys.argv[1])
    for k, v in stats(journal).items():
        print(f"{k:<18}{v:>12.3f}" if isinstance(v, float) else f"{k:<18}{v:>12}")
    print()
    print(by_setup(journal).to_string())
