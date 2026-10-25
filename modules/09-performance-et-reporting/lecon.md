# Module 09 · Mesure de performance et reporting

**Objectif** : mesurer une performance comme un professionnel, l'expliquer (d'où vient-elle ?), et la présenter à un client de façon claire et honnête.

**Durée** : 2 semaines · **Prérequis** : modules 04, 07 et 08

## 1. Les mesures absolues

| Mesure | Formule | Question |
| --- | --- | --- |
| Rendement annualisé (CAGR) | (valeur finale / valeur initiale)^(1/années) − 1 | Combien ai-je gagné par an ? |
| Volatilité | Écart-type × √périodes | Quelle amplitude des variations ? |
| Sharpe | (rendement − taux sans risque) / volatilité | Rendement par unité de risque total |
| Sortino | Même chose avec la volatilité à la baisse | Rendement par unité de risque « mauvais » |
| Perte maximale | Pire baisse depuis un plus haut | Quelle est la pire expérience vécue ? |
| Calmar | Rendement annualisé / perte maximale | Rendement par unité de pire perte |

Pour un client, la **perte maximale** et la durée pour revenir au plus haut parlent bien plus que le Sharpe.

## 2. Les mesures relatives

Un gestionnaire est jugé par rapport à une **référence** (benchmark) choisie à l'avance : MSCI World, un indice 60/40, ou 1/n comme dans ta thèse.

- **Bêta** : sensibilité au marché. Un bêta de 0,7 signifie que le portefeuille bouge en moyenne de 0,7 % quand la référence bouge de 1 %.
- **Alpha** : rendement non expliqué par le bêta (régression CAPM). Avec sa t-stat : un alpha avec t < 2 n'est pas distinguable de zéro.
- **Tracking error** : volatilité de l'écart avec la référence.
- **Information ratio** : surperformance annualisée / tracking error. Au-dessus de 0,5 de façon durable, c'est très bon.

## 3. L'attribution de performance

D'où vient la surperformance ? L'attribution de **Brinson-Fachler** la découpe par segment (secteur, classe d'actifs) :

- **Allocation** : avoir surpondéré les segments qui ont fait mieux que la référence.
- **Sélection** : avoir choisi, dans chaque segment, des titres meilleurs que ceux de la référence.
- **Interaction** : la combinaison des deux.

La somme des trois effets est exactement l'écart de performance. C'est ce qu'un comité d'investissement ou un client institutionnel demande.

Pour une stratégie quantitative, on fait aussi une **attribution factorielle** : régression sur les facteurs de Fama-French (même bibliothèque que ta thèse). Si l'alpha disparaît une fois les facteurs ajoutés, la stratégie n'est qu'une exposition à ces facteurs, ce qu'on peut obtenir moins cher avec des ETF.

## 4. Les normes GIPS

Les **Global Investment Performance Standards** (CFA Institute) encadrent la présentation des performances : composites incluant tous les portefeuilles comparables (pas seulement les meilleurs), rendements pondérés dans le temps, frais clairement indiqués, historique d'au moins 5 ans (ou depuis la création). Même sans conformité officielle, suivre leurs principes rend ton track record crédible.

**Rendement pondéré dans le temps (TWR) contre pondéré par l'argent (MWR)** : le TWR neutralise les apports et retraits du client et mesure le travail du gérant. Le MWR (TRI) mesure l'expérience du client. Un rapport sérieux indique les deux.

## 5. Le rapport client

Structure type, sur une ou deux pages :

1. Synthèse : valeur, rendement de la période, depuis le début, comparaison à la référence.
2. Graphique de la valeur et du drawdown.
3. Tableau des mesures absolues et relatives.
4. Tableau des rendements mensuels.
5. Allocation actuelle et changements de la période.
6. Commentaire : ce qui a marché, ce qui n'a pas marché, ce qui change.
7. Avertissement : « Les performances passées ne préjugent pas des performances futures. »

`report.write_report` produit les points 2 à 4 et 7 en Markdown, avec le graphique.

## 6. L'honnêteté

- Toujours la même référence, choisie avant.
- Montrer les mauvaises périodes autant que les bonnes.
- Performances nettes de frais.
- Pas de backtest présenté comme une performance réelle. Un backtest doit être marqué « simulé ».

## À retenir

1. Le Sharpe ne suffit pas : montre la perte maximale.
2. Mesure par rapport à une référence fixée à l'avance.
3. Explique d'où vient la performance (allocation, sélection, facteurs).
4. Un track record crédible suit les principes GIPS.
