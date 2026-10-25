"""Solutions du module 07."""
import numpy as np

from tradeskills import data, indicators as ind, metrics, portfolio, signals, validation

df = data.synthetic_ohlcv(n_days=3_000, seed=7)
close = df["close"]


def run(fast, slow):
    sig = (ind.sma(close, fast) > ind.sma(close, slow)).astype(int)
    return signals.backtest_signal(close, sig)


grid = {"fast": range(5, 55, 5), "slow": range(60, 220, 20)}

# 1
results = {(f, s): run(f, s) for f in grid["fast"] for s in grid["slow"]}
sharpes = {k: validation.sharpe_per_period(v) for k, v in results.items()}
best = max(sharpes, key=sharpes.get)
print(f"1. Meilleur in-sample {best} : Sharpe annualisé {sharpes[best] * np.sqrt(252):.2f}")
oos, params = validation.walk_forward(run, grid, close.index, train=756, test=252)
print(f"   Walk-forward : Sharpe {metrics.sharpe(oos, periods=252):.2f} ; paramètres choisis :")
print(params.to_string(index=False))

# 2
bh = close.pct_change().dropna()
lo, hi = validation.bootstrap_sharpe_ci(bh)
print(f"2. Sharpe achat-conservation {metrics.sharpe(bh, periods=252):.2f}, IC 95 % [{lo:.2f} ; {hi:.2f}]")

# 3
R = data.load_french_csv("data/10_Industry_Portfolios.csv", start=196901)
r_lw, _ = portfolio.rolling_backtest(R, 60, portfolio.cov_ledoit_wolf)
r_eq, _ = portfolio.rolling_backtest(R, 60, None)
r_emp, _ = portfolio.rolling_backtest(R, 60, portfolio.cov_empirical)
for nom, a, b in [("Ledoit-Wolf vs 1/n", r_lw, r_eq), ("Empirique vs Ledoit-Wolf", r_emp, r_lw)]:
    z, p = validation.sharpe_diff_test(a, b)
    print(f"3. {nom:<26} z = {z:+.2f}, p = {p:.3f}")

# 4
vals = np.array(list(sharpes.values()))
dsr = validation.deflated_sharpe(results[best], n_trials=len(vals), sharpe_variance=vals.var(ddof=1))
print(f"4. Deflated Sharpe du meilleur réglage : {dsr:.2f} (sur {len(vals)} essais)")

# 5
cheat = (close.pct_change() > 0).astype(int).shift(-1).fillna(0)  # connaît le rendement de demain
print(f"5. Stratégie qui triche : Sharpe {metrics.sharpe(signals.backtest_signal(close, cheat), periods=252):.1f}")
