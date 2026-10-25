"""Solutions du module 08."""
import numpy as np
import pandas as pd

from tradeskills import data, metrics, optim, portfolio

# 1
R48 = data.load_french_csv("data/48_Industry_Portfolios.csv", start=196901)
for win in (60, 120):
    row = {}
    for nom, est in [("Empirique", portfolio.cov_empirical), ("Ledoit-Wolf", portfolio.cov_ledoit_wolf),
                     ("Non linéaire", optim.cov_nonlinear_shrinkage)]:
        r, _ = portfolio.rolling_backtest(R48, win, est)
        row[nom] = f"{metrics.annualized_vol(r):.2%}"
    print(f"1. fenêtre {win} : {row}")

# 2 et 3
R = data.load_french_csv("data/10_Industry_Portfolios.csv", start=196901)
lw = portfolio.cov_ledoit_wolf
strategies = {
    "GMV ventes à découvert": lambda X: portfolio.gmv_weights(lw(X)),
    "GMV long-only": lambda X: optim.gmv_long_only(lw(X)),
    "GMV long-only max 25 %": lambda X: optim.gmv_long_only(lw(X), max_weight=0.25),
    "Parité de risque": lambda X: optim.risk_parity(lw(X)),
    "1/n": lambda X: np.ones(X.shape[1]) / X.shape[1],
}
rows = {}
for nom, fn in strategies.items():
    r, w = portfolio.rolling_strategy(R, 60, fn)
    rows[nom] = {"vol": metrics.annualized_vol(r), "sharpe": metrics.sharpe(r),
                 "max_dd": metrics.max_drawdown(r), "turnover": metrics.turnover(w)}
print("2-3.\n", pd.DataFrame(rows).T.round(3))
S = lw(R.values[-60:])
print("3. contributions au risque :", optim.risk_contributions(optim.risk_parity(S), S).round(3))

# 4 (annuel = mensuel x 12)
S12 = lw(R.values[-120:]) * 12
w_mkt = np.ones(10) / 10
cols = list(R.columns)
P = np.zeros((1, 10)); P[0, cols.index("HiTec")] = 1; P[0, cols.index("Utils")] = -1
pi = 2.5 * S12 @ w_mkt
mu_bl = optim.black_litterman(S12, w_mkt, P, np.array([0.03]))
print("4.\n", pd.DataFrame({"equilibre": pi, "a_posteriori": mu_bl,
                            "poids_tangent": optim.tangency(mu_bl, S12)}, index=cols).round(3))

# 5
X = R.values[-120:]
for nom, w in [("GMV long-only", optim.gmv_long_only(lw(X))), ("Parité de risque", optim.risk_parity(lw(X))),
               ("Min-CVaR", optim.min_cvar(X))]:
    print(f"5. {nom:<17} CVaR 95 % mensuelle = {optim.cvar(X @ w):.2%}")
