# Module 07 · Exercices

Solutions : `python modules/07-backtesting-rigoureux/solutions/solutions_07.py`

1. **In-sample contre walk-forward.** Sur `synthetic_ohlcv(n_days=3_000, seed=7)`, cherche le meilleur croisement de moyennes (rapide 5 à 50, lente 60 à 200) sur toute la période. Puis fais un walk-forward (3 ans d'entraînement, 1 an de test). Compare les Sharpe annualisés.

2. **Intervalle de confiance.** Calcule l'intervalle de confiance à 95 % du Sharpe de l'achat-conservation de la même série avec `bootstrap_sharpe_ci`. Que dit sa largeur ?

3. **Ta thèse.** Avec `portfolio.rolling_backtest` sur les 10 secteurs (depuis 1969, fenêtre de 60 mois), teste si la différence de Sharpe entre Ledoit-Wolf et 1/n est significative avec `sharpe_diff_test`. Puis entre l'estimateur empirique et Ledoit-Wolf.

4. **Sharpe dégonflé.** Pour l'exercice 1, calcule le Deflated Sharpe Ratio de la meilleure stratégie in-sample, avec le nombre réel d'essais et la variance de leurs Sharpe. Conclusion ?

5. **Détecter un bug.** Écris volontairement une stratégie avec regard vers le futur (signal = rendement du jour même positif) et montre qu'elle gagne énormément sur des prix aléatoires.

6. **Check-list.** Applique la check-list de la section 7 à la stratégie Pine du module 06 et rédige un paragraphe de conclusion.
