# Module 04 · Exercices

Solutions : `python modules/04-gestion-du-risque/solutions/solutions_04.py`

1. **Taille de position.** Capital 8 000 EUR, risque 0,75 %. Achat de SAP à 210 EUR, stop à 203 EUR. Combien d'actions ? Quel montant investi ?

2. **Stop large.** Même capital et même risque, mais ton stop technique est à 195 EUR. Nouvelle taille ? Qu'est-ce qui change dans le risque en euros ?

3. **R-multiples.** Calcule le R de ces trades : achat 100 / stop 95 / sortie 112 ; achat 40 / stop 38 / sortie 37 ; vente à découvert 60 / stop 63 / sortie 54.

4. **Espérance.** Sur 50 trades, tu as 18 gagnants à +2,4R en moyenne et 32 perdants à −1R. Quelle est ton espérance ? Combien gagnes-tu en moyenne par trade avec un risque de 80 EUR ?

5. **Kelly.** Avec les chiffres de l'exercice 4, calcule la fraction de Kelly, puis un quart de Kelly. Compare avec un risque fixe de 1 %.

6. **Monte-Carlo.** Avec `simulate_equity` (taux de réussite 40 %, gain moyen 2R, 200 trades), compare la médiane du capital final et le drawdown médian pour un risque de 1 %, 2 %, 5 % et 10 %. Qu'observes-tu à partir de 5 % ?

7. **Séries de pertes.** Estime par simulation la probabilité d'au moins 8 pertes d'affilée sur 200 trades avec 50 % de réussite.

8. **Plan personnel.** Remplis le plan de risque de la section 8 de la leçon et ajoute-le en tête de ton journal.
