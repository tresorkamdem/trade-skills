"""Agent Risque : contrôle avant chaque entrée et tableau de bord du risque d'une poche.

Avant d'entrer, refuse une ligne si :
- la poche a perdu plus que `drawdown_max` depuis son plus haut (coupe-circuit) ;
- le risque ouvert total dépasserait `risque_total_max` du capital ;
- la ligne est trop corrélée (> `correlation_max`) à une position déjà tenue.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .. import optim, portfolio
from .config import Poche
from .courtier import CourtierPapier
from .entree_sortie import Proposition


def controler(
    candidats: list[tuple[Proposition, int]],
    poche: Poche,
    courtier: CourtierPapier,
    valeur: float,
    prix: dict[str, float],
    drawdown: float,
    rendements: pd.DataFrame | None = None,
) -> tuple[list[tuple[Proposition, int]], list[tuple[str, str]]]:
    """Renvoie (candidats acceptés, [(symbole, raison du refus)])."""
    if drawdown <= -poche.drawdown_max:
        return [], [(p.symbole, f"coupe-circuit : poche à {drawdown:.1%} de son plus haut") for p, _ in candidats]

    acceptes, refus = [], []
    ouvert = courtier.risque_ouvert(prix)
    tenus = list(courtier.positions)
    for p, q in candidats:
        risque = (p.prix - p.stop) * q
        if ouvert + risque > poche.risque_total_max * valeur:
            refus.append((p.symbole, "risque total trop élevé"))
            continue
        if rendements is not None and tenus and p.symbole in rendements:
            corr = rendements.corr()[p.symbole].reindex(tenus).max()
            if corr > poche.correlation_max:
                refus.append((p.symbole, f"corrélation {corr:.2f} avec une position tenue"))
                continue
        acceptes.append((p, q))
        ouvert += risque
        tenus.append(p.symbole)
    return acceptes, refus


def tableau(courtier: CourtierPapier, prix: dict[str, float], rendements: pd.DataFrame) -> dict[str, float]:
    """Exposition, risque ouvert, volatilité (covariance Ledoit-Wolf), VaR et CVaR historiques à 1 jour (95 %)."""
    valeur = courtier.valeur(prix)
    montants = pd.Series({s: p.quantite * prix.get(s, p.prix_entree) for s, p in courtier.positions.items()}, dtype=float)
    out = {
        "valeur": valeur,
        "exposition": montants.sum() / valeur,
        "poids_max": (montants / valeur).max() if len(montants) else 0.0,
        "risque_ouvert": courtier.risque_ouvert(prix) / valeur,
        "vol_annuelle": 0.0,
        "var_95_1j": 0.0,
        "cvar_95_1j": 0.0,
    }
    cols = [s for s in montants.index if s in rendements]
    R = rendements[cols].dropna()
    if cols and len(R) > len(cols) + 1:
        w = (montants[cols] / valeur).to_numpy()
        sigma = portfolio.cov_ledoit_wolf(R.to_numpy())
        pnl = R.to_numpy() @ w
        out["vol_annuelle"] = float(np.sqrt(w @ sigma @ w * 252))
        out["var_95_1j"] = float(-np.quantile(pnl, 0.05))
        out["cvar_95_1j"] = optim.cvar(pnl, 0.95)
    return out
