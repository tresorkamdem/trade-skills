"""Solutions du module 12 (exercices 4 à 8)."""
import numpy as np

ONCE_G = 31.1035

# 4
g1, g2 = 4_000 / 1.16 / ONCE_G, 4_000 / 1.05 / ONCE_G
print(f"4. 4GLD ≈ {g1:.2f} € ; avec EUR/USD à 1,05 : {g2:.2f} €, soit {g2 / g1 - 1:+.1%} sans que l'or bouge en dollars")

# 5
capital, prix = 10_000, 110.0
for atr in (1.60, 3.20):
    stop = prix - 2.5 * atr
    n = int(capital * 0.01 // (prix - stop))
    print(f"5. ATR {atr:.2f} € : stop {stop:.2f} €, {n} titres, {n * prix:,.0f} € investis, risque {n * (prix - stop):.0f} €")
print("   ATR doublé : position deux fois plus petite, même risque en euros.")

# 6
or1 = capital * 0.99 ** 10
martingale = capital - 10 * (2 ** 10 - 1)
print(f"6. Or-1 : {or1:,.0f} € ({or1 / capital - 1:.1%}). Martingale : {martingale:,.0f} € "
      f"(10e mise : {10 * 2 ** 9:,} €, pertes cumulées {10 * (2 ** 10 - 1):,} €) : compte vidé.")


# 7
def proba_serie(n_trades: int, longueur: int, p_perte: float) -> float:
    """Probabilité d'au moins une série de `longueur` pertes consécutives (programmation dynamique)."""
    etat = np.zeros(longueur)  # etat[k] = proba d'avoir k pertes en cours, sans série fatale jusqu'ici
    etat[0] = 1.0
    for _ in range(n_trades):
        nouveau = np.zeros(longueur)
        nouveau[0] = etat.sum() * (1 - p_perte)
        nouveau[1:] = etat[:-1] * p_perte
        etat = nouveau
    return 1 - etat.sum()


for n in (1_000, 3_000):
    print(f"7. {n} trades, 60 % de gains : {proba_serie(n, 10, 0.4):.1%} de risque d'au moins 10 pertes de suite")
print("   La martingale ne se demande pas si elle sera ruinée, mais quand.")

# 8
marge, levier = 1_000, 20
expo = marge * levier
for baisse in (0.05, 0.13):
    print(f"8. CFD {levier}:1, exposition {expo:,} € : or −{baisse:.0%} → perte {expo * baisse:,.0f} € "
          f"({expo * baisse / marge:.0%} de la marge) ; 4GLD sans levier → perte {marge * baisse:,.0f} €")
print(f"   Après −45 %, il faut +{1 / 0.55 - 1:.0%} pour revenir au plus haut.")
