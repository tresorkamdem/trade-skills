# Module 11 · Exercices

Solutions : `python modules/11-bourses-africaines/solutions/solutions_11.py`

1. **Parité.** Tu investis 3 000 EUR à la BRVM. Combien de FCFA reçois-tu ? Une action cotée 15 000 FCFA verse un dividende net de 1 100 FCFA : quel est son rendement en dividende, et combien d'euros reçois-tu pour 13 actions ?

2. **Dévaluation.** Ton portefeuille BRVM vaut 10 000 EUR et a une volatilité de 12 %. Calcule la VaR paramétrique à 99 % sur un an, puis la perte en euros si le FCFA était dévalué de 50 % comme en 1994. Qu'en conclus-tu sur les mesures de risque habituelles ?

3. **Cours figés.** À partir d'un marché simulé et d'un titre qui le suit (bêta 1), fabrique avec `afrique.cotations_figees` une version qui ne s'échange qu'un jour sur trois. Compare le bêta journalier habituel, le bêta de Dimson (1 et 5 retards) et le bêta sur rendements hebdomadaires.

4. **Liquidité.** Calcule `afrique.liquidite` pour le titre liquide et le titre figé de l'exercice 3. Avec une position de 5 millions de FCFA et la valeur moyenne échangée, combien de séances faut-il pour sortir si tu ne veux pas dépasser 20 % du volume de chaque séance ?

5. **Diversification trompeuse.** Simule cinq titres qui suivent le même marché, dont trois peu liquides. Compare la corrélation moyenne en journalier et en hebdomadaire, puis les poids GMV Ledoit-Wolf calculés dans les deux cas. Quels titres l'optimisation journalière surpondère-t-elle, et pourquoi est-ce un piège ?

6. **Coûts.** Avec un coût de 1,5 % par ordre (hypothèse à remplacer par la grille de ta SGI), quel rendement annuel perds-tu en rééquilibrant chaque mois un portefeuille dont le turnover est de 20 % par rééquilibrage ? Et une fois par an ?

7. **Données réelles.** Télécharge depuis brvm.org un an de cours de Sonatel et d'Orange Côte d'Ivoire, enregistre-les au format CSV et calcule leur liquidité, leurs jours à la limite de variation et leur corrélation hebdomadaire.

8. **Note pour MAÀT.** En une page : quels titres de la BRVM et quelles obligations de la BVMAC proposerais-tu d'étudier pour un client de la diaspora, avec quels contrôles de liquidité et quelle part maximale de son patrimoine ?
