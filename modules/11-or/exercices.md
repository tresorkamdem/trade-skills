# Module 11 · Exercices

Solutions des exercices 4 à 8 : `python modules/11-or/solutions/solutions_11.py`. Les exercices 1 à 3 se font sur TradingView : écris tes réponses dans ton journal, on les relira ensemble.

## Sur TradingView (graphique journalier)

1. **Or et taux réels.** Ouvre `OANDA:XAUUSD`, puis ajoute `FRED:DFII10` (taux réel américain à 10 ans) dans un panneau en dessous. Regarde 2019 à 2023. Sur quelle période l'or et le taux réel vont-ils en sens inverse, comme le dit la leçon ? Sur quelle période la relation ne marche plus ? Propose une explication (indice : section 2 de la leçon).

2. **L'or en euros.** Sur le même graphique, ajoute `XETR:4GLD` en comparaison (bouton « + » à côté du symbole, échelle en pourcentage). Pour 2022, compare la performance de XAU/USD et de 4GLD. Laquelle a le mieux fait, et pourquoi ? Ajoute `FX:EURUSD` pour vérifier ton explication.

3. **Trois épisodes en trois phrases.** Avec l'outil « Plage de dates », mesure le mouvement de l'or sur : avril 2013, février à août 2020, et l'année 2024. Pour chacun, écris trois phrases : ce qui s'est passé, quel facteur de la section 2 l'explique, et ce qu'un robot à levier 20:1 aurait subi. C'est le critère de validation du palier 0.

## Calculs

4. **Prix au gramme.** L'or vaut 4 000 $ l'once et l'euro vaut 1,16 $. Quel est le prix théorique d'un titre 4GLD ? Si l'euro tombe à 1,05 $ et que l'or ne bouge pas en dollars, de combien de pourcents gagne un détenteur de 4GLD ?

5. **Taille de position d'Or-1.** Capital fictif 10 000 €, 4GLD à 110 €, ATR(20) de 1,60 €. Calcule le stop initial, le nombre de titres et le montant investi. Refais le calcul si l'ATR double (marché deux fois plus nerveux). Que remarques-tu ?

6. **Dix pertes de suite.** Compare deux robots qui perdent 10 trades de suite en partant de 10 000 € : Or-1 (1 % du capital risqué à chaque trade) et une martingale qui risque 10 € au premier trade et double après chaque perte. Combien reste-t-il à chacun ?

7. **Probabilité de la série fatale.** Un robot gagne 60 % de ses trades. Quelle est la probabilité d'au moins une série de 10 pertes consécutives sur 1 000 trades ? Et sur 3 000 trades (environ un an pour un robot qui trade toute la journée) ? Conclus sur la martingale.

8. **Levier et krach.** Avec un CFD à levier 20:1 et une marge de 1 000 €, quelle exposition contrôles-tu ? Combien perds-tu si l'or baisse de 5 %, puis de 13 % comme en avril 2013 ? Même question pour 1 000 € investis dans 4GLD sans levier. Enfin, l'or a perdu environ 45 % entre 2011 et 2015 : quelle hausse fallait-il ensuite pour revenir au plus haut ?
