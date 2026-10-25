"""Gestion du risque au niveau du trade : taille de position, R-multiple, Kelly."""
from __future__ import annotations

import math


def position_size(capital: float, risk_pct: float, entry: float, stop: float) -> int:
    """Nombre d'unités à acheter pour ne risquer que `risk_pct` du capital.

    Exemple : 10 000 EUR, 1 %, entrée 50, stop 48 -> risque 100 EUR / 2 EUR = 50 actions.
    """
    risk_per_unit = abs(entry - stop)
    if risk_per_unit == 0:
        raise ValueError("Le stop doit être différent du prix d'entrée")
    return math.floor(capital * risk_pct / risk_per_unit)


def r_multiple(entry: float, stop: float, exit_price: float) -> float:
    """Gain ou perte du trade exprimé en multiples du risque initial (1R)."""
    risk = entry - stop  # positif pour un achat, négatif pour une vente à découvert
    return (exit_price - entry) / risk


def kelly_fraction(win_rate: float, avg_win_r: float, avg_loss_r: float = 1.0) -> float:
    """Fraction de Kelly : f = p - (1 - p) / b, avec b = gain moyen / perte moyenne.

    En pratique on n'en utilise qu'une fraction (un quart ou la moitié), car
    l'estimation de p et b est bruitée.
    """
    b = avg_win_r / avg_loss_r
    return win_rate - (1 - win_rate) / b


def expectancy(win_rate: float, avg_win_r: float, avg_loss_r: float = 1.0) -> float:
    """Espérance par trade, en R."""
    return win_rate * avg_win_r - (1 - win_rate) * avg_loss_r
