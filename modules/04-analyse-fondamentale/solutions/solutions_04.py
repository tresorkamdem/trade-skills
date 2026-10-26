"""Solutions du module 04 (montants en millions)."""
from tradeskills.fundamentals import dcf, ratios

# 1
r = ratios(price=45, shares=200, net_income=600, equity=4_000, revenue=6_000,
           ebit=900, debt=2_500, cash=700, dividends=240)
for k, v in r.items():
    print(f"1. {k:<32}{v:>10.3f}")

# 2
print("2. Notre entreprise : PER 15, ROE 15 %, dette nette/FP 0,45, contre PER 22, ROE 9 %, 1,2.")
print("   Elle est moins chère, plus rentable et moins endettée. Il manque : croissance attendue,")
print("   qualité du cash-flow, secteur exact, historique des marges.")

# 3
v = dcf(500, 0.08, 5, 0.09, 0.02, net_debt=1_800, shares=200)
print(f"3. Valeur par action : {v:.2f} EUR (cours 45 EUR)")

# 4
print("4.      g=1%    g=2%    g=3%")
vals = []
for k in (0.08, 0.09, 0.10):
    row = [dcf(500, 0.08, 5, k, g, 1_800, 200) for g in (0.01, 0.02, 0.03)]
    vals += row
    print(f"   k={k:.0%} " + " ".join(f"{x:7.2f}" for x in row))
print(f"   Écart : de {min(vals):.2f} à {max(vals):.2f} EUR, soit un facteur {max(vals) / min(vals):.1f}")
