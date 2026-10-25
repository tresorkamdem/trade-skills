"""Validation des backtests (module 07) : walk-forward, intervalles de confiance,
tests de différence de Sharpe et Sharpe « dégonflé » pour les tests multiples.

Les ratios de Sharpe des tests statistiques sont **par période** (non annualisés).
"""
from __future__ import annotations

from itertools import product
from typing import Callable, Iterable

import numpy as np
import pandas as pd
from scipy import stats

EULER_GAMMA = 0.5772156649


def sharpe_per_period(r: pd.Series | np.ndarray) -> float:
    r = np.asarray(r, dtype=float)
    return r.mean() / r.std(ddof=1)


def walk_forward(
    run: Callable[..., pd.Series],
    grid: dict[str, Iterable],
    index: pd.Index,
    train: int,
    test: int,
    score: Callable[[pd.Series], float] = sharpe_per_period,
) -> tuple[pd.Series, pd.DataFrame]:
    """Optimisation glissante : choisit les paramètres sur `train` périodes, les applique
    sur les `test` périodes suivantes, puis avance de `test`.

    `run(**params)` doit renvoyer la série complète des rendements de la stratégie
    (indexée comme `index`) ; seule la partie d'entraînement sert à choisir.
    Renvoie (rendements hors échantillon mis bout à bout, paramètres choisis par fenêtre).
    """
    keys = list(grid)
    combos = [dict(zip(keys, values)) for values in product(*grid.values())]
    cache = {tuple(c.values()): run(**c) for c in combos}

    oos, chosen = [], []
    for start in range(0, len(index) - train - test + 1, test):
        tr = index[start : start + train]
        te = index[start + train : start + train + test]
        best = max(combos, key=lambda c: score(cache[tuple(c.values())].loc[tr]))
        oos.append(cache[tuple(best.values())].loc[te])
        chosen.append({"debut_test": te[0], **best})
    return pd.concat(oos), pd.DataFrame(chosen)


def bootstrap_sharpe_ci(
    r: pd.Series, periods: int = 252, n: int = 5_000, block: int = 20, level: float = 0.95, seed: int | None = 0
) -> tuple[float, float]:
    """Intervalle de confiance du Sharpe annualisé par bootstrap par blocs (garde l'autocorrélation)."""
    rng = np.random.default_rng(seed)
    x = np.asarray(r, dtype=float)
    T = len(x)
    n_blocks = int(np.ceil(T / block))
    sims = np.empty(n)
    for i in range(n):
        starts = rng.integers(0, T - block + 1, n_blocks)
        sample = np.concatenate([x[s : s + block] for s in starts])[:T]
        sims[i] = sharpe_per_period(sample) * np.sqrt(periods)
    a = (1 - level) / 2
    return float(np.quantile(sims, a)), float(np.quantile(sims, 1 - a))


def sharpe_diff_test(r1: pd.Series, r2: pd.Series) -> tuple[float, float]:
    """Test de Jobson-Korkie corrigé par Memmel (2003) : H0 = Sharpe égaux.

    Hypothèse de rendements i.i.d. normaux. Ledoit et Wolf (2008) proposent une
    version robuste (HAC / bootstrap), piste ouverte de la Bachelorarbeit.
    Renvoie (statistique z, p-value bilatérale).
    """
    a, b = np.asarray(r1, float), np.asarray(r2, float)
    T = len(a)
    s1, s2 = sharpe_per_period(a), sharpe_per_period(b)
    rho = np.corrcoef(a, b)[0, 1]
    theta = (2 - 2 * rho + 0.5 * (s1**2 + s2**2 - 2 * s1 * s2 * rho**2)) / T
    if np.isclose(theta, 0):  # séries parfaitement corrélées et de même Sharpe
        return 0.0, 1.0
    z = (s1 - s2) / np.sqrt(theta)
    return float(z), float(2 * stats.norm.sf(abs(z)))


def deflated_sharpe(r: pd.Series, n_trials: int, sharpe_variance: float) -> float:
    """Deflated Sharpe Ratio (Bailey et López de Prado, 2014).

    Probabilité que le vrai Sharpe soit positif, en tenant compte du fait que la
    meilleure de `n_trials` stratégies a été retenue. `sharpe_variance` est la variance
    des Sharpe par période des essais. Proche de 1 : résultat crédible.
    """
    x = np.asarray(r, dtype=float)
    T = len(x)
    sr = sharpe_per_period(x)
    skew = stats.skew(x)
    kurt = stats.kurtosis(x, fisher=False)
    sr0 = np.sqrt(sharpe_variance) * (
        (1 - EULER_GAMMA) * stats.norm.ppf(1 - 1 / n_trials)
        + EULER_GAMMA * stats.norm.ppf(1 - 1 / (n_trials * np.e))
    )
    denom = np.sqrt(1 - skew * sr + (kurt - 1) / 4 * sr**2)
    return float(stats.norm.cdf((sr - sr0) * np.sqrt(T - 1) / denom))
