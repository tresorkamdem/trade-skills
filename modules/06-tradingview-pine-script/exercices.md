# Module 06 · Exercices

1. **Premier indicateur.** Écris un indicateur qui trace la MM50 et la MM200 et colore le fond en vert quand la MM50 est au-dessus. Compare tes valeurs à `tradeskills.indicators.sma` sur un export CSV.

2. **Lire le système.** Ajoute `pine/systeme_tendance_indicateur.pine` sur un graphique journalier de SPY. Explique chaque ligne du script et pourquoi `[1]` est indispensable dans `ta.highest(high, lenEntry)[1]`.

3. **Backtest TradingView.** Ajoute `pine/systeme_tendance_strategie.pine` sur SPY, le DAX et l'EUR/USD. Note pour chacun le rendement, le drawdown maximal, le nombre de trades et le profit factor. Recommence sans commission ni slippage : quelle différence ?

4. **Sensibilité.** Fais varier l'entrée Donchian (10, 20, 55) et le stop (1,5, 2, 3 ATR). Le résultat est-il stable, ou un seul réglage marche-t-il ? (Rappel du module 03, exercice 5.)

5. **Repainting.** Remplace `ta.highest(high, lenEntry)[1]` par `ta.highest(high, lenEntry)` dans la stratégie. Que se passe-t-il, et pourquoi ?

6. **Webhook.** Lance `node/webhook.mjs` en local, puis simule une alerte :
   ```bash
   curl -X POST "http://localhost:3000/alerte?cle=$WEBHOOK_SECRET" -d '{"type":"achat","symbole":"SPY","prix":580}'
   ```
   Configure ensuite un vrai bot Telegram et une alerte TradingView.

7. **Ta propre stratégie.** Code en Pine un des setups du module 05 (par exemple le rebond sur MM50), avec stop en ATR et risque fixe. Ajoute-la dans `pine/`.
