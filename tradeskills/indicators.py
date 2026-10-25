"""Indicateurs techniques classiques, calculés comme sur TradingView.

Toutes les fonctions prennent des `pd.Series` (ou un DataFrame OHLCV) et ne
regardent que le passé : la valeur à la date t n'utilise que les données <= t.
"""
from __future__ import annotations

import pandas as pd


def sma(close: pd.Series, n: int) -> pd.Series:
    """Moyenne mobile simple."""
    return close.rolling(n).mean()


def ema(close: pd.Series, n: int) -> pd.Series:
    """Moyenne mobile exponentielle (alpha = 2 / (n + 1), comme ta.ema de Pine)."""
    return close.ewm(span=n, adjust=False).mean()


def rma(x: pd.Series, n: int) -> pd.Series:
    """Moyenne de Wilder (alpha = 1 / n), utilisée par le RSI et l'ATR."""
    return x.ewm(alpha=1 / n, adjust=False).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    """Relative Strength Index de Wilder, entre 0 et 100."""
    delta = close.diff()
    gain = rma(delta.clip(lower=0), n)
    loss = rma(-delta.clip(upper=0), n)
    return 100 - 100 / (1 + gain / loss)


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    line = ema(close, fast) - ema(close, slow)
    sig = ema(line, signal)
    return pd.DataFrame({"macd": line, "signal": sig, "histogramme": line - sig})


def true_range(df: pd.DataFrame) -> pd.Series:
    prev = df["close"].shift()
    return pd.concat([df["high"] - df["low"], (df["high"] - prev).abs(), (df["low"] - prev).abs()], axis=1).max(axis=1)


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    """Average True Range : amplitude moyenne, utile pour placer un stop."""
    return rma(true_range(df), n)


def bollinger(close: pd.Series, n: int = 20, k: float = 2.0) -> pd.DataFrame:
    mid = sma(close, n)
    sd = close.rolling(n).std(ddof=0)
    return pd.DataFrame({"milieu": mid, "haut": mid + k * sd, "bas": mid - k * sd})


def vwap(df: pd.DataFrame) -> pd.Series:
    """VWAP cumulé par jour calendaire (pour des données intraday)."""
    typical = (df["high"] + df["low"] + df["close"]) / 3
    pv = typical * df["volume"]
    day = df.index.normalize()
    return pv.groupby(day).cumsum() / df["volume"].groupby(day).cumsum()


def donchian(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Plus haut et plus bas des n dernières bougies (sans la bougie courante)."""
    return pd.DataFrame({
        "haut": df["high"].rolling(n).max().shift(),
        "bas": df["low"].rolling(n).min().shift(),
    })
