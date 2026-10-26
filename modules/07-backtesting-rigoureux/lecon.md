# Module 07 · Backtesting rigoureux

**Objectif** : distinguer une stratégie qui a un vrai avantage d'une stratégie qui a seulement été ajustée au passé. C'est le module où ta formation de mathématicien te donne le plus d'avance.

**Durée** : 3 semaines · **Prérequis** : modules 02, 03 et 06, ta Bachelorarbeit

## 1. Ce que ta thèse t'a déjà appris

Ta Bachelorarbeit est un backtest rigoureux : données publiques et reproductibles, rolling window strictement hors échantillon, benchmark naïf (1/n), mesure du turnover, et un résultat honnête (1/n reste compétitif en Sharpe). Ce module généralise ces principes à des stratégies de trading, où le risque principal n'est plus le bruit d'estimation de la covariance, mais la **sur-optimisation**.

## 2. Les biais classiques

| Biais | Exemple | Parade |
| --- | --- | --- |
| Biais d'anticipation (look-ahead) | Utiliser la clôture du jour pour trader à l'ouverture du même jour | Décaler le signal d'une période (`signal.shift()`, déjà fait dans `backtest_signal`) |
| Biais du survivant | Tester sur les membres actuels du DAX, sans les sociétés sorties ou en faillite | Bases de données « point-in-time », ou indices plutôt qu'actions |
| Sur-optimisation | Tester 500 réglages et garder le meilleur | Walk-forward, Sharpe dégonflé, peu de paramètres |
| Coûts ignorés | Pas de spread, de frais ni de slippage | `cost_bps`, commission et slippage dans Pine |
| Snooping des données | Regarder la période de test, puis modifier la règle | Garder une période finale jamais vue, utilisée une seule fois |
| Changement de régime | Une stratégie de 2010 à 2020 (taux zéro) testée sans 2022 | Tester sur plusieurs décennies et plusieurs marchés |

## 3. In-sample, out-of-sample, walk-forward

- **In-sample** : la période sur laquelle tu choisis la règle et ses paramètres.
- **Out-of-sample** : la période sur laquelle tu la mesures, sans rien changer.
- **Walk-forward** : tu répètes l'opération en glissant dans le temps, exactement comme ton rolling window. On choisit les meilleurs paramètres sur 3 ans, on les applique l'année suivante, on avance d'un an, et on met bout à bout les années hors échantillon.

```python
from tradeskills import validation
oos, params = validation.walk_forward(run, grid, index, train=756, test=252)
```

Si la performance walk-forward est très inférieure à la performance in-sample, la stratégie est sur-optimisée.

## 4. Mesurer l'incertitude

Un Sharpe estimé sur peu de données est très incertain. Pour des rendements i.i.d., l'erreur type du Sharpe annualisé vaut environ 1 / √(nombre d'années), quelle que soit la fréquence des données (Lo, 2002). Avec 5 ans de données et un Sharpe de 0,8, l'intervalle à 95 % va d'environ −0,1 à 1,7 : on ne sait même pas si la stratégie gagne de l'argent.

- `bootstrap_sharpe_ci` : intervalle de confiance par bootstrap par blocs, qui conserve l'autocorrélation.
- `sharpe_diff_test` : test de Jobson-Korkie corrigé par Memmel. Il répond à la question laissée ouverte dans ta thèse : la différence de Sharpe entre Ledoit-Wolf et 1/n est-elle significative ? La version robuste de Ledoit et Wolf (2008) en est le prolongement naturel.

## 5. Les tests multiples et le Sharpe dégonflé

Si tu testes N stratégies sans aucun avantage, la meilleure aura quand même un Sharpe positif, d'autant plus grand que N est grand. Le **Deflated Sharpe Ratio** (Bailey et López de Prado, 2014) corrige le Sharpe observé du nombre d'essais, de l'asymétrie et de l'épaisseur des queues. Il donne la probabilité que le vrai Sharpe soit positif. En dessous de 0,95, le résultat n'est pas crédible.

**Note tous tes essais** dans un fichier, y compris les ratés. Le nombre d'essais est une donnée du backtest.

## 6. Le test de la série aléatoire

Avant de croire un backtest, fais-le tourner sur `synthetic_ohlcv`, qui n'a aucune structure. Si la stratégie y gagne de l'argent après coûts, ton code a un biais (souvent un regard vers le futur).

## 7. Check-list avant de trader une stratégie

1. Hypothèse économique claire : pourquoi cela marcherait-il, et qui perd en face ?
2. Peu de paramètres (3 ou 4 au maximum) et résultats stables autour des valeurs choisies.
3. Coûts réalistes inclus.
4. Walk-forward positif sur au moins 10 ans, et sur plusieurs marchés.
5. Sharpe dégonflé supérieur à 0,95 compte tenu de tous les essais.
6. Testé sur données aléatoires sans gain.
7. Période finale jamais vue, testée une fois, résultat cohérent.
8. Puis paper trading (module 05) : les résultats réels doivent ressembler au backtest.

## À retenir

1. Un backtest prouve surtout ce que tu as cherché à prouver : sois ton propre contradicteur.
2. Le walk-forward est le rolling window de ta thèse appliqué aux paramètres d'une stratégie.
3. Compte tes essais et dégonfle ton Sharpe.
4. Une stratégie qui gagne sur des prix aléatoires révèle un bug.
