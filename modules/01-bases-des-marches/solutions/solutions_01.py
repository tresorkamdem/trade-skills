"""Solutions chiffrées du module 01."""

# 1. Carnet d'ordres : 500 à 100,02 puis 200 à 100,04
prix_moyen = (500 * 100.02 + 200 * 100.04) / 700
print(f"1. Prix moyen {prix_moyen:.4f}, coût vs milieu {(prix_moyen - 100.01) * 700:.2f} EUR")

# 2. Coût annuel : par aller-retour, spread + 2 x slippage (entrée et sortie) + 2 ordres de 1 EUR
position = 5_000
par_aller_retour = position * (0.0003 + 2 * 0.0002) + 2 * 1.0
annuel = par_aller_retour * 3 * 20 * 12
print(f"2. {par_aller_retour:.2f} EUR par aller-retour, {annuel:,.0f} EUR par an = {annuel / position:.0%} de la position")

# 3. Gap : stop exécuté à l'ouverture
perte_reelle = (50 - 42) * 100
perte_prevue = (50 - 47) * 100
print(f"3. Perte réelle {perte_reelle} EUR au lieu de {perte_prevue} EUR prévus. "
      "Un put (option de vente) à 47 aurait plafonné la perte, contre le paiement d'une prime.")

# 4. Levier 5 : la perte en capital vaut 5 x la baisse de l'indice
print(f"4. -50 % du capital pour une baisse de {0.5 / 5:.0%}, -100 % pour {1 / 5:.0%}")

# 5. Thèse : coût annuel = turnover mensuel x coût par unité x 12
for nom, to in [("Empirique", 1.907), ("Ledoit-Wolf", 0.246)]:
    print(f"5. {nom:<12} perd {to * 0.002 * 12:.2%} par an")
