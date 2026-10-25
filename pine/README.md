# Scripts Pine Script (TradingView)

| Script | Type | Module |
| --- | --- | --- |
| `systeme_tendance_indicateur.pine` | Indicateur + alertes JSON | 03, 06 |
| `systeme_tendance_strategie.pine` | Stratégie backtestable, risque fixe et coûts | 04, 06, 07 |
| `rsi_divergence.pine` | RSI avec divergences haussières | 03 |

Utilisation : TradingView → Pine Editor → coller le code → « Add to chart ». Pour une stratégie, les résultats sont dans l'onglet « Strategy Tester ».

Les alertes envoient un message JSON qui peut être reçu par le serveur de `node/` puis transmis sur Telegram.
