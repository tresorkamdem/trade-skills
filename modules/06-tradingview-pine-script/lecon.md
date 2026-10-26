# Module 06 · TradingView et Pine Script

**Objectif** : utiliser TradingView comme poste de travail, écrire tes propres indicateurs et stratégies en Pine Script, et recevoir tes signaux sur Telegram.

**Durée** : 3 semaines · **Prérequis** : modules 02 et 03

## 1. TradingView comme poste de travail

- **Mises en page** : un onglet par unité de temps (hebdomadaire pour la tendance, journalier pour l'entrée).
- **Listes de surveillance** : une liste « portefeuille », une liste « candidats swing ».
- **Outils de dessin** : supports, résistances, l'outil « Long/Short position » qui calcule le R d'un trade avant de le prendre.
- **Replay** : rejouer le passé bougie par bougie pour s'entraîner sans biais de connaissance du futur.
- **Export** : menu du graphique → « Export chart data » donne un CSV lisible par `tradeskills.data.load_ohlcv_csv`.

## 2. Les bases de Pine Script (v6)

Pine exécute ton script **une fois par bougie**, de la plus ancienne à la plus récente. Chaque variable est une série : `close` est la clôture courante, `close[1]` celle de la bougie précédente.

```pine
//@version=6
indicator("Ma moyenne", overlay = true)
len = input.int(50, "Longueur")
mm = ta.sma(close, len)
plot(mm, color = color.orange)
```

| Notion | Exemple |
| --- | --- |
| Entrées réglables | `input.int`, `input.float`, `input.bool` |
| Fonctions techniques | `ta.sma`, `ta.ema`, `ta.rsi`, `ta.atr`, `ta.highest`, `ta.crossover` |
| Variable persistante | `var float stop = na` (gardée d'une bougie à l'autre) |
| Affichage | `plot`, `plotshape`, `hline`, `bgcolor` |
| Alertes | `alertcondition` (choisie dans la fenêtre d'alerte), `alert()` (message dynamique) |

Les fonctions de `tradeskills/indicators.py` donnent les mêmes valeurs que `ta.*` : tu peux vérifier un calcul Pine en Python.

## 3. Indicateur ou stratégie

- `indicator()` affiche des informations et des signaux.
- `strategy()` simule des ordres et produit un rapport dans le **Strategy Tester** : rendement, drawdown, nombre de trades, profit factor.

Paramètres à toujours renseigner dans une stratégie : `initial_capital`, `commission_value`, `slippage`. Sans coûts, un backtest est faux. Le fichier `pine/systeme_tendance_strategie.pine` calcule aussi la taille de position à risque fixe, comme `tradeskills.risk.position_size`.

## 4. Les pièges du backtest sur TradingView

| Piège | Explication | Parade |
| --- | --- | --- |
| Repainting | Un signal apparaît puis disparaît, car calculé sur une bougie non clôturée ou avec des données futures (`request.security` mal utilisé) | Signaux à la clôture (`barstate.isconfirmed`, `alert.freq_once_per_bar_close`), `lookahead = barmerge.lookahead_off` |
| Historique limité | Le nombre de bougies dépend de l'abonnement | Exporter et backtester en Python sur une longue histoire |
| Sur-optimisation | Régler les paramètres jusqu'à ce que la courbe soit belle | Module 07 : walk-forward et hors échantillon |
| Exécution irréaliste | Achat au plus bas de la bougie | Ordres au marché à l'ouverture suivante, slippage |

## 5. Des alertes à Telegram

1. Le script appelle `alertcondition` ou `alert()` avec un message JSON, par exemple `{"type":"achat","symbole":"SPY","prix":580.5,"stop":571.2}`.
2. L'alerte TradingView envoie ce message en **webhook** (option payante) vers ton serveur.
3. Le serveur `node/webhook.mjs` vérifie un jeton secret, enregistre l'alerte et l'envoie sur Telegram.

Le serveur est écrit sans dépendance, en Node.js pur, et testé (`npm test`). La configuration est dans `node/README.md`.

## 6. Organisation du travail

- Un script = un fichier dans `pine/`, versionné dans Git.
- Toute stratégie Pine prometteuse est **revérifiée en Python** sur une histoire plus longue et hors échantillon avant d'être tradée.

## À retenir

1. Pine tourne bougie par bougie ; `[1]` regarde en arrière.
2. Une stratégie sans coûts ni slippage ment.
3. Méfie-toi du repainting : signaux à la clôture uniquement.
4. TradingView sert à voir et à alerter ; Python sert à valider.
