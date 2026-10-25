"""Solutions du module 09."""
import numpy as np
import pandas as pd
from scipy.optimize import brentq

from tradeskills import data, portfolio, report

# 1
R = data.load_french_csv("data/10_Industry_Portfolios.csv", start=196901)
r, _ = portfolio.rolling_backtest(R, 60, portfolio.cov_ledoit_wolf)
b, _ = portfolio.rolling_backtest(R, 60, None)
ab = report.alpha_beta(r, b)
print(f"1. alpha {ab['alpha_annuel']:.2%} (t = {ab['t_alpha']:.2f}), bêta {ab['beta']:.2f}, "
      f"TE {report.tracking_error(r, b):.2%}, IR {report.information_ratio(r, b):.2f}")

# 2
seg = ["Actions", "Obligations"]
att = report.brinson(pd.Series([0.6, 0.4], seg), pd.Series([0.5, 0.5], seg),
                     pd.Series([0.08, 0.02], seg), pd.Series([0.06, 0.03], seg))
print("2.\n", att.round(4))
print(f"   Somme {att['total'].sum():.4f} = écart {0.6 * 0.08 + 0.4 * 0.02 - (0.5 * 0.06 + 0.5 * 0.03):.4f}")

# 3
twr = np.sqrt(1.2 * 0.9) - 1
final = (10_000 * 1.2 + 20_000) * 0.9
mwr = brentq(lambda x: -10_000 - 20_000 / (1 + x) + final / (1 + x) ** 2, -0.99, 1)
print(f"3. TWR {twr:.2%} par an, MWR {mwr:.2%} par an : le client a apporté le gros de son argent juste avant la baisse")

# 4
path = report.write_report(r, b, "rapports/gmv_lw.md", title="GMV Ledoit-Wolf contre 1/n (simulé)")
print(f"4. Rapport écrit : {path}")
