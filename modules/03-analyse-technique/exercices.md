# Module 03 · Exercices

Solutions : `python modules/03-analyse-technique/solutions/solutions_03.py`

1. **Calculs à la main.** Clôtures : 10, 11, 12, 11, 13. Calcule la SMA(3) des trois derniers jours, puis l'EMA(3) en partant de 10 (alpha = 0,5). Vérifie avec `indicators.sma` et `indicators.ema`.

2. **RSI.** Sur `synthetic_ohlcv(seed=1)`, calcule le RSI(14). Combien de jours est-il sous 30 ? Au-dessus de 70 ?

3. **Test d'hypothèse.** Sur la même série, compare le rendement moyen des 5 jours qui suivent un RSI < 30 au rendement moyen de 5 jours sur tout l'échantillon. Fais un test t de Welch. Que conclus-tu, sachant que la série est aléatoire ?

4. **Croisement de moyennes.** Backteste « acheteur quand la MM20 est au-dessus de la MM100, neutre sinon » avec 5 points de base de coûts. Compare à l'achat-conservation avec `signals.report`.

5. **Tests multiples.** Teste toutes les combinaisons de moyennes rapides (5 à 50, pas de 5) et lentes (60 à 200, pas de 20) sur 20 séries aléatoires différentes. Quelle part des stratégies bat l'achat-conservation en Sharpe ? Qu'est-ce que cela dit d'un « meilleur réglage » trouvé sur une seule série ?

6. **Stop en ATR.** Sur la série, quelle est la distance moyenne d'un stop à 2 ATR en pourcentage du prix ? Avec 10 000 EUR et 1 % de risque, quelle taille de position cela donne-t-il en moyenne ?

7. **Pratique sur TradingView.** Sur un graphique journalier de SPY et de l'EUR/USD, trace la MM50, la MM200, le RSI et l'ATR. Identifie la tendance hebdomadaire, deux supports et deux résistances. Exporte les données (menu « Export chart data ») et charge-les avec `data.load_ohlcv_csv`.
