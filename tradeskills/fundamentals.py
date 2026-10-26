"""Ratios financiers et valorisation simple (module 04)."""
from __future__ import annotations


def ratios(
    price: float,
    shares: float,
    net_income: float,
    equity: float,
    revenue: float,
    ebit: float,
    debt: float,
    cash: float,
    dividends: float = 0.0,
) -> dict[str, float]:
    """Ratios de base à partir des chiffres d'un rapport annuel (mêmes unités partout)."""
    market_cap = price * shares
    ev = market_cap + debt - cash
    return {
        "capitalisation": market_cap,
        "valeur_entreprise": ev,
        "PER": market_cap / net_income,
        "price_to_book": market_cap / equity,
        "EV_EBIT": ev / ebit,
        "marge_operationnelle": ebit / revenue,
        "marge_nette": net_income / revenue,
        "ROE": net_income / equity,
        "dette_nette_sur_fonds_propres": (debt - cash) / equity,
        "rendement_dividende": dividends / market_cap,
    }


def dcf(
    fcf: float,
    growth: float,
    years: int,
    discount: float,
    terminal_growth: float,
    net_debt: float = 0.0,
    shares: float = 1.0,
) -> float:
    """Valeur par action d'un modèle DCF à deux phases.

    `fcf` : flux de trésorerie disponible de l'année écoulée. Croissance `growth`
    pendant `years` ans, puis valeur terminale de Gordon-Shapiro avec `terminal_growth`.
    """
    if discount <= terminal_growth:
        raise ValueError("Le taux d'actualisation doit dépasser la croissance terminale")
    value, cf = 0.0, fcf
    for t in range(1, years + 1):
        cf *= 1 + growth
        value += cf / (1 + discount) ** t
    terminal = cf * (1 + terminal_growth) / (discount - terminal_growth)
    value += terminal / (1 + discount) ** years
    return (value - net_debt) / shares
