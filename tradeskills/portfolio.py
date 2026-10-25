"""Portefeuille de variance minimale (GMV) et backtest glissant hors échantillon.

Généralisation du code de la Bachelorarbeit (`Repli_Tabelle2_Kennzahlen.py`) :
même logique, mais avec des estimateurs interchangeables et des coûts de
transaction explicites, deux pistes ouvertes dans le « Ausblick ».
"""
from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd
from sklearn.covariance import OAS, LedoitWolf

Estimator = Callable[[np.ndarray], np.ndarray]


def cov_empirical(window: np.ndarray) -> np.ndarray:
    return np.cov(window, rowvar=False, ddof=1)


def cov_ledoit_wolf(window: np.ndarray) -> np.ndarray:
    return LedoitWolf().fit(window).covariance_


def cov_oas(window: np.ndarray) -> np.ndarray:
    return OAS().fit(window).covariance_


ESTIMATORS: dict[str, Estimator] = {
    "Empirique": cov_empirical,
    "Ledoit-Wolf": cov_ledoit_wolf,
    "OAS": cov_oas,
}


def gmv_weights(sigma: np.ndarray) -> np.ndarray:
    """Poids du portefeuille de variance minimale (ventes à découvert permises)."""
    ones = np.ones(sigma.shape[0])
    x = np.linalg.solve(sigma, ones)
    return x / x.sum()


def rolling_backtest(
    returns: pd.DataFrame,
    window: int,
    estimator: Estimator | None,
    cost_bps: float = 0.0,
) -> tuple[pd.Series, pd.DataFrame]:
    """Réestime les poids chaque période sur les `window` dernières observations.

    `estimator=None` donne la pondération égale 1/n. `cost_bps` est le coût de
    transaction en points de base par unité de rotation ; il est déduit du rendement
    de la période où le rééquilibrage a lieu.
    Renvoie (rendements hors échantillon, poids utilisés).
    """
    R = returns.to_numpy()
    n = R.shape[1]
    weights, rets = [], []
    prev = None
    for t in range(window, len(R)):
        if estimator is None:
            w = np.ones(n) / n
        else:
            w = gmv_weights(estimator(R[t - window : t]))
        r = w @ R[t]
        if prev is not None and cost_bps:
            r -= cost_bps / 1e4 * 0.5 * np.abs(w - prev).sum()
        weights.append(w)
        rets.append(r)
        prev = w
    idx = returns.index[window:]
    return (
        pd.Series(rets, index=idx, name="rendement"),
        pd.DataFrame(weights, index=idx, columns=returns.columns),
    )


def compare(returns: pd.DataFrame, window: int, cost_bps: float = 0.0) -> pd.DataFrame:
    """Compare les trois estimateurs et 1/n, comme le tableau 6.2 de la thèse."""
    from . import metrics

    rows = {}
    for name, est in {**ESTIMATORS, "1/n": None}.items():
        r, w = rolling_backtest(returns, window, est, cost_bps)
        rows[name] = {
            "vol_annuelle": metrics.annualized_vol(r),
            "sharpe": metrics.sharpe(r),
            "max_drawdown": metrics.max_drawdown(r),
            "turnover": metrics.turnover(w),
        }
    return pd.DataFrame(rows).T
