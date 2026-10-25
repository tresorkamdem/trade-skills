"""Solutions du module 03."""
import numpy as np
import pandas as pd
from scipy import stats

from tradeskills import data, indicators as ind, metrics, signals

# 1
c = pd.Series([10, 11, 12, 11, 13], dtype=float)
print("1. SMA(3) :", ind.sma(c, 3).round(3).tolist())
print("   EMA(3) :", ind.ema(c, 3).round(3).tolist())

# 2
df = data.synthetic_ohlcv(seed=1)
r = ind.rsi(df["close"])
print(f"2. RSI < 30 : {(r < 30).sum()} jours, RSI > 70 : {(r > 70).sum()} jours")

# 3
fwd = df["close"].shift(-5) / df["close"] - 1
after = fwd[r < 30].dropna()
t, p = stats.ttest_ind(after, fwd.dropna(), equal_var=False)
print(f"3. après RSI<30 : {after.mean():.3%} sur {len(after)} cas, moyenne générale {fwd.mean():.3%}, p = {p:.2f}")
print("   Série aléatoire : toute différence est du bruit, même si p était < 5 %.")

# 4
sig = (ind.sma(df["close"], 20) > ind.sma(df["close"], 100)).astype(int)
print("4.\n", signals.report(signals.backtest_signal(df["close"], sig), df["close"]).round(3))

# 5
wins = total = 0
for seed in range(20):
    d = data.synthetic_ohlcv(seed=100 + seed)
    bh = metrics.sharpe(d["close"].pct_change().dropna(), periods=252)
    for f in range(5, 55, 5):
        for s in range(60, 220, 20):
            sg = (ind.sma(d["close"], f) > ind.sma(d["close"], s)).astype(int)
            st = signals.backtest_signal(d["close"], sg)
            wins += metrics.sharpe(st, periods=252) > bh
            total += 1
print(f"5. {wins}/{total} = {wins / total:.0%} des réglages battent l'achat-conservation sur des prix aléatoires")

# 6
a = ind.atr(df)
dist = (2 * a / df["close"]).mean()
size = (10_000 * 0.01 / (2 * a)).mean()
print(f"6. stop à 2 ATR = {dist:.2%} du prix en moyenne, soit environ {size:.0f} unités")
