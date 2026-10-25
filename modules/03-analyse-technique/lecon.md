# Module 03 · Analyse technique

**Objectif** : lire un graphique, connaître les indicateurs courants, savoir ce qu'ils calculent vraiment, et surtout **tester** s'ils apportent quelque chose plutôt que d'y croire.

**Durée** : 3 semaines · **Prérequis** : modules 01 et 04

## 1. Ce qu'est (et n'est pas) l'analyse technique

L'analyse technique étudie les prix et les volumes passés pour décider quand entrer et sortir. Elle ne prédit pas l'avenir. Au mieux, elle repère des situations où la probabilité ou le rapport gain/risque est un peu en ta faveur. Ton avantage de mathématicien : tu peux **vérifier statistiquement** ce que la plupart des traders acceptent sur parole.

Deux familles d'idées reviennent partout :

- **Suivi de tendance (momentum)** : ce qui monte a tendance à continuer de monter, sur des horizons de quelques mois. C'est l'un des effets les mieux documentés dans la recherche (Jegadeesh et Titman, 1993 ; Moskowitz, Ooi et Pedersen, 2012).
- **Retour à la moyenne** : sur de très courts horizons (jours), les excès ont tendance à se corriger.

## 2. Les chandeliers

Chaque bougie résume une période : ouverture, plus haut, plus bas, clôture (OHLC). Corps plein = clôture sous l'ouverture. Mèches longues = rejet d'un prix.

Figures à connaître : marteau, étoile filante, englobante haussière et baissière, doji. Seules, elles ont peu de pouvoir prédictif. Elles deviennent utiles **dans un contexte** : sur un support, dans le sens de la tendance, avec du volume.

## 3. Tendance, supports et résistances

- **Tendance haussière** : plus hauts et plus bas de plus en plus hauts. Baissière : l'inverse.
- **Support** : zone où les acheteurs sont intervenus plusieurs fois. **Résistance** : l'inverse.
- Un support cassé devient souvent une résistance.
- **Multi-horizons** : on lit la tendance sur une unité de temps plus grande (hebdomadaire) et on cherche l'entrée sur une plus petite (journalière).

## 4. Les indicateurs

| Indicateur | Calcul | Usage |
| --- | --- | --- |
| SMA / EMA | Moyenne des n dernières clôtures (l'EMA pondère davantage les plus récentes) | Direction de la tendance, supports dynamiques (MM50, MM200) |
| RSI(14) | 100 − 100 / (1 + moyenne des hausses / moyenne des baisses), lissage de Wilder | Surachat > 70, survente < 30 ; divergences |
| MACD | EMA12 − EMA26, signal = EMA9 du MACD | Changements de momentum |
| ATR(14) | Moyenne de Wilder du True Range | Volatilité, placement du stop (par exemple 2 ATR) |
| Bollinger | SMA20 ± 2 écarts-types | Compression et expansion de volatilité |
| Donchian | Plus haut / plus bas des 20 dernières bougies | Cassures (système des « Turtles ») |
| VWAP | Prix moyen pondéré par les volumes depuis l'ouverture | Référence intraday des institutionnels |

Tous sont dans `tradeskills/indicators.py`, calculés comme sur TradingView.

```python
from tradeskills import data, indicators as ind
df = data.synthetic_ohlcv()
df["rsi"] = ind.rsi(df["close"])
df["atr"] = ind.atr(df)
```

## 5. Le volume

Une cassure avec un volume nettement supérieur à la moyenne est plus crédible. Une hausse sur volume faible est fragile. Sur le forex au comptant il n'y a pas de volume centralisé : on utilise le volume des futures ou le nombre de ticks.

## 6. Tester au lieu de croire

C'est ici que ton cursus fait la différence. Pour chaque règle :

1. **Formule une hypothèse** : « Quand le RSI passe sous 30, le rendement des 5 jours suivants est positif en moyenne. »
2. **Sépare les données** : tu cherches sur une période, tu valides sur une autre (module 07).
3. **Compare à un benchmark** : achat-conservation, ou la même règle sur des dates tirées au hasard.
4. **Compte les coûts** : spread et frais à chaque changement de position (`backtest_signal(..., cost_bps=5)`).
5. **Méfie-toi des tests multiples** : si tu testes 100 réglages, environ 5 seront « significatifs » à 5 % par pur hasard.

Le simulateur `synthetic_ohlcv` produit des prix **sans aucune structure** : toute stratégie qui y semble rentable après coûts est un faux positif. C'est un excellent détecteur d'erreurs dans tes backtests.

## 7. Un système complet, pas un indicateur

Un indicateur ne suffit pas. Un système précise : le filtre de tendance, le signal d'entrée, le stop (en ATR), la taille de position (module 04), la sortie, et les conditions où on ne trade pas (annonces, faible liquidité).

Exemple de système de suivi de tendance :

- Filtre : clôture au-dessus de la MM200.
- Entrée : cassure du plus haut de 20 jours (Donchian).
- Stop initial : entrée − 2 ATR.
- Sortie : clôture sous le plus bas de 10 jours.
- Taille : 1 % de risque.

## À retenir

1. Un indicateur est une transformation des prix passés, rien de plus.
2. Le contexte (tendance, niveau, volume) compte plus que la figure.
3. Toute règle se teste sur des données qu'on n'a pas utilisées pour la trouver, et après coûts.
4. Sur des prix aléatoires, rien ne doit marcher : vérifie-le.
