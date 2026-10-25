"""Solutions du module 05."""
import math

from scipy import stats

from tradeskills import journal

# 1
for nom, par_mois in [("Day trader", 4 * 21), ("Swing trader", 6)]:
    print(f"1. {nom:<13} {par_mois * 12:>5} allers-retours par an -> {par_mois * 12 * 0.0008:.0%} de coûts")

# 2
df = journal.load("journal/modele_journal.csv")
print("2.\n", journal.by_setup(df))
print("   rebond_mm50 est négatif, mais 2 trades ne prouvent rien : il faut des dizaines de trades par setup.")

# 3 : n tel que 0,2 / (1,5 / sqrt(n)) >= z(0,95)
z = stats.norm.ppf(0.95)
n = math.ceil((z * 1.5 / 0.2) ** 2)
print(f"3. Il faut environ {n} trades")
