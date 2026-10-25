"""Mesures de performance et de risque d'une série de rendements."""
from __future__ import annotations

import numpy as np
import pandas as pd


def annualized_return(returns: pd.Series, periods: int = 12) -> float:
    """Rendement annualisé composé (CAGR)."""
    growth = (1 + returns).prod()
    return growth ** (periods / len(returns)) - 1


def annualized_vol(returns: pd.Series, periods: int = 12) -> float:
    return returns.std(ddof=1) * np.sqrt(periods)


def sharpe(returns: pd.Series, rf: float = 0.0, periods: int = 12) -> float:
    """Ratio de Sharpe annualisé. `rf` est le taux sans risque annuel.

    Avec rf = 0, c'est la définition utilisée dans la Bachelorarbeit
    (moyenne x 12 / volatilité annualisée).
    """
    excess = returns - rf / periods
    return excess.mean() * periods / annualized_vol(returns, periods)


def sortino(returns: pd.Series, rf: float = 0.0, periods: int = 12) -> float:
    """Comme Sharpe, mais ne pénalise que la volatilité à la baisse."""
    excess = returns - rf / periods
    downside = np.sqrt((np.minimum(excess, 0) ** 2).mean()) * np.sqrt(periods)
    return excess.mean() * periods / downside


def drawdown(returns: pd.Series) -> pd.Series:
    """Perte depuis le dernier plus haut, à chaque date (valeurs <= 0)."""
    wealth = (1 + returns).cumprod()
    return wealth / wealth.cummax() - 1


def max_drawdown(returns: pd.Series) -> float:
    return drawdown(returns).min()


def calmar(returns: pd.Series, periods: int = 12) -> float:
    """Rendement annualisé divisé par la perte maximale (en valeur absolue)."""
    return annualized_return(returns, periods) / abs(max_drawdown(returns))


def turnover(weights: pd.DataFrame) -> float:
    """Rotation moyenne par période : moitié de la somme des changements de poids."""
    return 0.5 * weights.diff().abs().sum(axis=1).iloc[1:].mean()


def summary(returns: pd.Series, rf: float = 0.0, periods: int = 12) -> dict[str, float]:
    return {
        "rendement_annuel": annualized_return(returns, periods),
        "vol_annuelle": annualized_vol(returns, periods),
        "sharpe": sharpe(returns, rf, periods),
        "sortino": sortino(returns, rf, periods),
        "max_drawdown": max_drawdown(returns),
        "calmar": calmar(returns, periods),
    }
