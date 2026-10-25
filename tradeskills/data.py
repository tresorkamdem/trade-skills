"""Chargement des données de marché.

- `load_french_csv` : portefeuilles sectoriels de la Kenneth French Data Library
  (même nettoyage que dans la Bachelorarbeit, `daten_vorbereiten.py`).
- `load_ohlcv_csv` : cours OHLCV (Open, High, Low, Close, Volume), par exemple
  exportés depuis TradingView ou un broker.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def load_french_csv(path: str | Path, start: int | None = None) -> pd.DataFrame:
    """Renvoie les rendements mensuels (en décimal) du premier bloc d'un fichier French.

    L'index est un `PeriodIndex` mensuel ; seules les lignes où toutes les colonnes
    sont disponibles sont gardées. `start` (AAAAMM) coupe le début de la série.
    """
    df = pd.read_csv(path, skiprows=11)
    df = df.rename(columns={df.columns[0]: "date"})

    # Lignes mensuelles valides (AAAAMM) uniquement
    text = df["date"].astype(str).str.strip()
    df = df[text.str.match(r"^\d{6}$")].copy()
    df["date"] = df["date"].astype(int)

    # Le fichier contient plusieurs blocs (value-weighted, equal-weighted, ...) :
    # on garde le premier, qui s'arrête au premier saut de date en arrière
    jumps = np.where(np.diff(df["date"].to_numpy()) < 0)[0]
    if len(jumps) > 0:
        df = df.iloc[: jumps[0] + 1]

    cols = [c for c in df.columns if c != "date"]
    df[cols] = df[cols].apply(pd.to_numeric, errors="coerce")
    df[cols] = df[cols].replace([-99.99, -999.0], np.nan)
    df.columns = ["date"] + [c.strip() for c in cols]

    df = df.dropna()
    if start is not None:
        df = df[df["date"] >= start]

    df.index = pd.PeriodIndex(df.pop("date").astype(str), freq="M")
    return df / 100.0


def load_ohlcv_csv(path: str | Path) -> pd.DataFrame:
    """Charge un CSV OHLCV et normalise les noms de colonnes en minuscules.

    Accepte une colonne `date`, `time` ou `datetime` (export TradingView : `time`).
    """
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    date_col = next(c for c in ("date", "datetime", "time") if c in df.columns)
    dates = df.pop(date_col)
    if pd.api.types.is_numeric_dtype(dates):
        dates = pd.to_datetime(dates, unit="s")  # horodatage Unix de TradingView
    df.index = pd.DatetimeIndex(pd.to_datetime(dates), name="date")
    missing = {"open", "high", "low", "close"} - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes : {sorted(missing)}")
    return df.sort_index()


def synthetic_ohlcv(
    n_days: int = 1_000,
    start_price: float = 100.0,
    drift: float = 0.07,
    vol: float = 0.20,
    seed: int | None = 0,
) -> pd.DataFrame:
    """Cours journaliers simulés (mouvement brownien géométrique) pour s'entraîner hors ligne.

    `drift` et `vol` sont annuels. Les prix simulés n'ont, par construction, aucune
    structure exploitable : une stratégie qui « marche » dessus est un faux positif.
    C'est un bon test de tes backtests (voir module 07).
    """
    rng = np.random.default_rng(seed)
    dt = 1 / 252
    rets = rng.normal((drift - 0.5 * vol**2) * dt, vol * np.sqrt(dt), n_days)
    close = start_price * np.exp(np.cumsum(rets))
    open_ = np.concatenate([[start_price], close[:-1]]) * np.exp(rng.normal(0, vol * np.sqrt(dt) / 4, n_days))
    spread = np.abs(rng.normal(0, vol * np.sqrt(dt) / 2, n_days))
    high = np.maximum(open_, close) * (1 + spread)
    low = np.minimum(open_, close) * (1 - spread)
    volume = rng.lognormal(13, 0.4, n_days).round()
    idx = pd.bdate_range("2020-01-01", periods=n_days, name="date")
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": volume}, index=idx)
