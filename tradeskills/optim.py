"""Optimisation de portefeuille avancée (module 08).

Prolonge la Bachelorarbeit : shrinkage non linéaire (piste du « Ausblick »),
contraintes sans vente à découvert, tangence, parité de risque, Black-Litterman et CVaR.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import linprog, minimize


def cov_nonlinear_shrinkage(window: np.ndarray) -> np.ndarray:
    """Shrinkage non linéaire analytique de Ledoit et Wolf (2020, Annals of Statistics).

    Chaque valeur propre est corrigée individuellement par un estimateur à noyau,
    au lieu d'être tirée uniformément vers une cible. Cas n_actifs <= n_observations.
    """
    X = window - window.mean(axis=0)
    n_obs, p = X.shape
    n = n_obs - 1  # un degré de liberté perdu par le centrage
    if p > n:
        raise ValueError("Implémenté seulement pour n_actifs <= n_observations - 1")
    sample = X.T @ X / n
    lam, u = np.linalg.eigh(sample)  # valeurs propres croissantes
    L = np.tile(lam[:, None], (1, p))
    h = n ** (-1 / 3)
    H = h * L.T
    x = (L - L.T) / H
    ftilde = (3 / 4 / np.sqrt(5)) * np.mean(np.maximum(1 - x**2 / 5, 0) / H, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        hf = (-3 / 10 / np.pi) * x + (3 / 4 / np.sqrt(5) / np.pi) * (1 - x**2 / 5) * np.log(
            np.abs((np.sqrt(5) - x) / (np.sqrt(5) + x))
        )
    edge = np.isclose(np.abs(x), np.sqrt(5))
    hf[edge] = (-3 / 10 / np.pi) * x[edge]
    Hftilde = np.mean(hf / H, axis=1)
    c = p / n
    dtilde = lam / ((np.pi * c * lam * ftilde) ** 2 + (1 - c - np.pi * c * lam * Hftilde) ** 2)
    return u @ np.diag(dtilde) @ u.T


def gmv_long_only(sigma: np.ndarray, max_weight: float = 1.0) -> np.ndarray:
    """Variance minimale sans vente à découvert, poids plafonnés à `max_weight`."""
    n = sigma.shape[0]
    res = minimize(
        lambda w: w @ sigma @ w,
        np.ones(n) / n,
        jac=lambda w: 2 * sigma @ w,
        bounds=[(0, max_weight)] * n,
        constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1}],
        method="SLSQP",
    )
    return res.x


def tangency(mu: np.ndarray, sigma: np.ndarray, rf: float = 0.0, long_only: bool = True) -> np.ndarray:
    """Portefeuille de Sharpe maximal (tangent)."""
    n = len(mu)
    if not long_only:
        x = np.linalg.solve(sigma, mu - rf)
        return x / x.sum()
    res = minimize(
        lambda w: -(w @ mu - rf) / np.sqrt(w @ sigma @ w),
        np.ones(n) / n,
        bounds=[(0, 1)] * n,
        constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1}],
        method="SLSQP",
    )
    return res.x


def risk_contributions(w: np.ndarray, sigma: np.ndarray) -> np.ndarray:
    """Part de chaque actif dans la variance du portefeuille (somme = 1)."""
    return w * (sigma @ w) / (w @ sigma @ w)


def risk_parity(sigma: np.ndarray, tol: float = 1e-10, max_iter: int = 10_000) -> np.ndarray:
    """Parité de risque (ERC) : chaque actif contribue autant au risque.

    Algorithme de point fixe sur y avec y_i (Σy)_i = 1 (Spinu, 2013), puis normalisation.
    """
    y = 1 / np.sqrt(np.diag(sigma))
    for _ in range(max_iter):
        sy = sigma @ y
        # résout y_i * (sigma_ii y_i + reste_i) = 1 pour y_i > 0
        rest = sy - np.diag(sigma) * y
        new = (-rest + np.sqrt(rest**2 + 4 * np.diag(sigma))) / (2 * np.diag(sigma))
        if np.max(np.abs(new - y)) < tol:
            y = new
            break
        y = new
    return y / y.sum()


def black_litterman(
    sigma: np.ndarray,
    w_market: np.ndarray,
    P: np.ndarray,
    Q: np.ndarray,
    delta: float = 2.5,
    tau: float = 0.05,
    omega: np.ndarray | None = None,
) -> np.ndarray:
    """Rendements espérés a posteriori de Black-Litterman.

    Point de départ : rendements d'équilibre π = δ Σ w_marché. Les vues sont P μ = Q,
    d'incertitude Ω (par défaut proportionnelle à P τΣ P').
    """
    pi = delta * sigma @ w_market
    ts = tau * sigma
    if omega is None:
        omega = np.diag(np.diag(P @ ts @ P.T))
    A = np.linalg.inv(ts) + P.T @ np.linalg.inv(omega) @ P
    b = np.linalg.solve(ts, pi) + P.T @ np.linalg.solve(omega, Q)
    return np.linalg.solve(A, b)


def cvar(returns: np.ndarray, alpha: float = 0.95) -> float:
    """CVaR historique (Expected Shortfall) : perte moyenne dans les (1 − alpha) pires cas."""
    r = np.sort(np.asarray(returns))
    k = max(1, int(np.floor(len(r) * (1 - alpha))))
    return float(-r[:k].mean())


def min_cvar(scenarios: np.ndarray, alpha: float = 0.95) -> np.ndarray:
    """Portefeuille long-only qui minimise la CVaR historique (Rockafellar et Uryasev, 2000).

    Programme linéaire en (w, VaR, u) : min VaR + 1/((1-α)T) Σ u_t, u_t >= -r_t·w - VaR, u_t >= 0.
    """
    T, n = scenarios.shape
    c = np.concatenate([np.zeros(n), [1.0], np.full(T, 1 / ((1 - alpha) * T))])
    A_ub = np.hstack([-scenarios, -np.ones((T, 1)), -np.eye(T)])
    b_ub = np.zeros(T)
    A_eq = np.concatenate([np.ones(n), [0.0], np.zeros(T)])[None, :]
    bounds = [(0, 1)] * n + [(None, None)] + [(0, None)] * T
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=[1.0], bounds=bounds, method="highs")
    return res.x[:n]
