"""Solutions du module 04."""
import numpy as np

from tradeskills.risk import (expectancy, kelly_fraction, max_drawdowns, position_size,
                              r_multiple, simulate_equity)

# 1 et 2
for stop in (203, 195):
    q = position_size(8_000, 0.0075, 210, stop)
    print(f"Stop {stop} : {q} actions, {q * 210:,} EUR investis, risque {q * (210 - stop)} EUR")

# 3
for e, s, x in [(100, 95, 112), (40, 38, 37), (60, 63, 54)]:
    print(f"3. entrée {e}, stop {s}, sortie {x} : {r_multiple(e, s, x):+.1f}R")

# 4
p = 18 / 50
e = expectancy(p, 2.4, 1.0)
print(f"4. espérance {e:+.3f}R, soit {e * 80:+.2f} EUR par trade avec 80 EUR de risque")

# 5
k = kelly_fraction(p, 2.4)
print(f"5. Kelly {k:.1%}, un quart de Kelly {k / 4:.1%}, contre 1 % en risque fixe")

# 6
for risk in (0.01, 0.02, 0.05, 0.10):
    eq = simulate_equity(0.40, 2.0, risk)
    print(f"6. risque {risk:>4.0%} : capital final médian {np.median(eq[:, -1]):6.2f}x, "
          f"drawdown médian {np.median(max_drawdowns(eq)):.0%}, "
          f"pire 5 % des cas {np.percentile(max_drawdowns(eq), 5):.0%}")

# 7
rng = np.random.default_rng(1)
losses = rng.random((20_000, 200)) >= 0.5
def longest_run(row):
    best = cur = 0
    for x in row:
        cur = cur + 1 if x else 0
        best = max(best, cur)
    return best
runs = np.array([longest_run(r) for r in losses])
print(f"7. P(au moins 8 pertes d'affilée) = {(runs >= 8).mean():.0%}")
