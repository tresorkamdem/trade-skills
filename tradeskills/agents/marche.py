"""Sources de données des agents.

Chaque source renvoie {symbole: DataFrame OHLCV} : barres journalières pour les poches
`swing` et `long_terme`, barres intraday pour la poche `day`.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .. import data


def synthetic_intraday(
    n_days: int = 60, bars_per_day: int = 78, start_price: float = 100.0, vol: float = 0.20, seed: int | None = 0
) -> pd.DataFrame:
    """Barres de 5 minutes simulées, de 09:30 à 15:55, sans structure exploitable."""
    df = data.synthetic_ohlcv(
        n_days * bars_per_day, start_price, drift=0.07 / bars_per_day, vol=vol / np.sqrt(bars_per_day), seed=seed
    )
    days = pd.bdate_range("2024-01-02", periods=n_days)
    minutes = pd.to_timedelta(9 * 60 + 30 + 5 * np.arange(bars_per_day), unit="min")
    df.index = pd.DatetimeIndex([d + m for d in days for m in minutes], name="date")
    return df


class SourceSimulee:
    """Cours simulés : pour apprendre et tester les agents sans connexion."""

    def __init__(self, n_jours: int = 1_000, n_jours_intraday: int = 60, seed: int = 0):
        self.n_jours, self.n_jours_intraday, self.seed = n_jours, n_jours_intraday, seed

    def historique(self, symboles: list[str], style: str) -> dict[str, pd.DataFrame]:
        out = {}
        for i, s in enumerate(symboles):
            seed = self.seed + i
            if style == "day":
                out[s] = synthetic_intraday(self.n_jours_intraday, seed=seed)
            else:
                out[s] = data.synthetic_ohlcv(self.n_jours, vol=0.15 + 0.02 * i, seed=seed)
        return out


class SourceCSV:
    """Exports TradingView (ou d'un broker) : `<dossier>/<SYMBOLE>.csv` en journalier,
    `<dossier>/<SYMBOLE>_intraday.csv` pour la poche day."""

    def __init__(self, dossier: str | Path):
        self.dossier = Path(dossier)

    def historique(self, symboles: list[str], style: str) -> dict[str, pd.DataFrame]:
        suffixe = "_intraday" if style == "day" else ""
        return {s: data.load_ohlcv_csv(self.dossier / f"{s}{suffixe}.csv") for s in symboles}


class SourceYahoo:
    """Yahoo Finance via `yfinance` (pip install yfinance). Gratuit, non officiel, usage personnel
    uniquement ; l'intraday 5 minutes est limité aux 60 derniers jours."""

    def historique(self, symboles: list[str], style: str) -> dict[str, pd.DataFrame]:
        import yfinance as yf

        periode, intervalle = ("60d", "5m") if style == "day" else ("5y", "1d")
        out = {}
        for s in symboles:
            df = yf.Ticker(s).history(period=periode, interval=intervalle, auto_adjust=True)
            df.columns = [c.lower() for c in df.columns]
            df.index = pd.DatetimeIndex(df.index.tz_localize(None), name="date")
            out[s] = df[["open", "high", "low", "close", "volume"]].dropna()
        return out


def source(spec: str):
    """`simulee`, `yahoo` ou `csv:<dossier>`."""
    if spec == "simulee":
        return SourceSimulee()
    if spec == "yahoo":
        return SourceYahoo()
    if spec.startswith("csv:"):
        return SourceCSV(spec[4:])
    raise ValueError(f"Source inconnue : {spec}")
