# Module 08 · Optimisation de portefeuille avancée

**Objectif** : aller au-delà du portefeuille de variance minimale de ta thèse, vers les méthodes utilisées en gestion professionnelle, et savoir laquelle choisir pour un client.

**Durée** : 4 semaines · **Prérequis** : Bachelorarbeit, modules 04 et 07

## 1. Rappel : où s'arrêtait ta thèse

Tu as montré que, pour le portefeuille GMV, le problème n'est pas l'optimisation mais l'**estimation** : le shrinkage linéaire (Ledoit-Wolf, OAS) stabilise la covariance, réduit la volatilité hors échantillon de 45 % et le turnover de 87 % (fenêtre de 60 mois, 48 secteurs). Trois questions restaient ouvertes : un shrinkage plus fin, les contraintes réalistes, et les rendements espérés.

## 2. Le shrinkage non linéaire

Le shrinkage linéaire tire toutes les valeurs propres vers une même cible avec une même intensité. Le **shrinkage non linéaire** (Ledoit et Wolf, 2017 et 2020) corrige chaque valeur propre séparément, avec une formule analytique fondée sur un estimateur à noyau de la densité spectrale. Il est d'autant plus utile que n/T est grand.

`optim.cov_nonlinear_shrinkage` implémente la version analytique (2020). Sur tes 48 secteurs, il fait mieux que Ledoit-Wolf linéaire avec une fenêtre de 120 mois et un peu moins bien avec 60 mois : à vérifier dans l'exercice 1.

## 3. Les contraintes réalistes

Le GMV de ta thèse autorise les ventes à découvert. Pour un client particulier ou une microfinance, on impose en général :

- **pas de vente à découvert** : w ≥ 0 (`gmv_long_only`) ;
- **plafond par ligne** : par exemple 20 % maximum ;
- **contraintes de secteur ou de classe d'actifs**.

Les contraintes jouent elles-mêmes un rôle de shrinkage : Jagannathan et Ma (2003) montrent que la contrainte w ≥ 0 équivaut à réduire certaines covariances estimées.

## 4. Les rendements espérés : le maillon faible

Le portefeuille tangent (Sharpe maximal) a besoin des rendements espérés μ, beaucoup plus difficiles à estimer que la covariance (c'est pour cela que ta thèse s'est concentrée sur le GMV). Avec des moyennes historiques, le portefeuille tangent est extrêmement instable. Trois réponses :

1. **Ne pas utiliser μ** : GMV, parité de risque, 1/n.
2. **Black-Litterman** : partir des rendements d'équilibre implicites du marché, π = δ Σ w_marché, puis les ajuster par des vues explicites et chiffrées avec leur incertitude.
3. **Facteurs** : estimer μ à partir d'expositions à des facteurs (value, momentum, qualité), plus stables que les moyennes individuelles.

### Black-Litterman en pratique

Une vue s'écrit P μ = Q. Exemple : « la technologie fera 2 % de plus par an que l'énergie » donne une ligne de P avec +1 sur la tech et −1 sur l'énergie, et Q = 0,02. La confiance dans la vue est réglée par Ω. Sans vue, Black-Litterman redonne exactement le portefeuille de marché : c'est un point de départ raisonnable, contrairement aux moyennes historiques.

## 5. La parité de risque

Dans un portefeuille 60 % actions / 40 % obligations, les actions représentent environ 90 % du risque. La **parité de risque** (ERC) choisit les poids pour que chaque actif contribue autant à la variance :

> w_i (Σw)_i = w_j (Σw)_j pour tout i, j

Elle n'utilise que Σ (donc profite du shrinkage), ne vend pas à découvert et est très diversifiée. C'est une méthode facile à expliquer à un client.

## 6. Au-delà de la variance : la CVaR

La variance pénalise autant les hausses que les baisses et suppose des queues fines. La **CVaR à 95 %** (Expected Shortfall) est la perte moyenne dans les 5 % pires cas. C'est la mesure de risque de Bâle III/IV pour le portefeuille de négociation des banques, utile pour ton offre de scoring et de risque. La minimisation de la CVaR historique se ramène à un programme linéaire (Rockafellar et Uryasev, 2000) : `optim.min_cvar`.

## 7. Le rééquilibrage

| Règle | Avantage | Inconvénient |
| --- | --- | --- |
| Calendaire (mensuel, trimestriel) | Simple | Coûts même quand rien ne change |
| Par seuil (écart de plus de 5 points) | Moins de transactions | Surveillance continue |
| Avec pénalité de turnover | Optimal après coûts | Plus complexe |

Ta thèse mesurait déjà le turnover. Avec `cost_bps`, tu peux maintenant en mesurer le coût réel.

## 8. Quelle méthode pour quel client ?

| Situation | Méthode conseillée |
| --- | --- |
| Peu d'actifs, longue histoire | GMV long-only avec Ledoit-Wolf |
| Beaucoup d'actifs, peu d'historique | Shrinkage non linéaire, ou facteurs |
| Le client a des convictions | Black-Litterman |
| Le client veut de la simplicité et de la diversification | Parité de risque, ou 1/n |
| Le risque de perte extrême compte le plus (microfinance, trésorerie) | Min-CVaR |

## À retenir

1. Estimer bien compte plus qu'optimiser finement.
2. Les contraintes long-only stabilisent aussi le portefeuille.
3. Sans bonne estimation de μ, préfère GMV, parité de risque ou Black-Litterman.
4. Choisis la mesure de risque qui correspond à ce que le client craint vraiment.
