"""Backtest simple d'une stratégie à signal sur un seul actif.

Le signal (1 = acheteur, 0 = neutre, -1 = vendeur) calculé à la clôture du jour t
est appliqué au rendement du jour t + 1 : pas de regard vers le futur.
"""
from __future__ import annotations

import pandas as pd

from . import metrics


def backtest_signal(close: pd.Series, signal: pd.Series, cost_bps: float = 5.0) -> pd.Series:
    """Rendements journaliers nets de la stratégie. `cost_bps` par unité de changement de position."""
    position = signal.shift().fillna(0)
    rets = close.pct_change().fillna(0)
    costs = position.diff().abs().fillna(position.abs()) * cost_bps / 1e4
    return position * rets - costs


def report(strategy: pd.Series, close: pd.Series) -> pd.DataFrame:
    """Compare la stratégie à l'achat-conservation (buy and hold), en annualisé (252 jours)."""
    bh = close.pct_change().fillna(0)
    return pd.DataFrame({
        "strategie": metrics.summary(strategy, periods=252),
        "achat_conservation": metrics.summary(bh, periods=252),
    })
