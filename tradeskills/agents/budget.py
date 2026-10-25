"""Agent Budget : combien investir dans chaque ligne.

- Poches swing et day : risque fixe par trade (`risk.position_size`), plafonné par
  le poids maximal d'une ligne et par le cash disponible.
- Poche long terme : poids cibles GMV Ledoit-Wolf sans vente à découvert (la thèse),
  parité de risque ou 1/n.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from .. import optim, portfolio, risk
from .config import Poche
from .courtier import CourtierPapier
from .entree_sortie import Proposition


def dimensionner(
    propositions: list[Proposition], poche: Poche, courtier: CourtierPapier, valeur: float
) -> list[tuple[Proposition, int]]:
    places = poche.max_positions - len(courtier.positions) - sum(o.quantite > 0 for o in courtier.ordres)
    cash = courtier.cash
    retenues = []
    for p in propositions:
        if places <= 0:
            break
        if p.stop >= p.prix:
            continue
        q = risk.position_size(valeur, poche.risque_par_trade, p.prix, p.stop)
        q = min(q, math.floor(poche.poids_max * valeur / p.prix), math.floor(cash / (p.prix * 1.01)))
        if q > 0:
            retenues.append((p, q))
            cash -= q * p.prix
            places -= 1
    return retenues


def poids_cibles(rendements: pd.DataFrame, poche: Poche) -> pd.Series:
    """Poids long-only qui somment à 1, chacun au plus `poids_max` (relevé à 1/n si nécessaire)."""
    n = rendements.shape[1]
    plafond = max(poche.poids_max, 1 / n)
    methode = poche.param("methode")
    if methode == "egal":
        w = np.ones(n) / n
    else:
        sigma = portfolio.cov_ledoit_wolf(rendements.to_numpy())
        if methode == "gmv_lw":
            w = optim.gmv_long_only(sigma, plafond)
        elif methode == "parite_risque":
            w = optim.risk_parity(sigma)
        else:
            raise ValueError(f"Méthode inconnue : {methode}")
        w = _plafonner(w, plafond)
    return pd.Series(w, index=rendements.columns)


def _plafonner(w: np.ndarray, plafond: float) -> np.ndarray:
    """Ramène chaque poids sous le plafond et redistribue l'excédent aux autres, au prorata."""
    w = np.clip(w, 0, None) / np.clip(w, 0, None).sum()
    for _ in range(len(w)):
        trop = w > plafond + 1e-12
        if not trop.any():
            break
        excedent = (w[trop] - plafond).sum()
        w[trop] = plafond
        libres = w < plafond - 1e-12
        w[libres] += excedent * w[libres] / w[libres].sum()
    return w
