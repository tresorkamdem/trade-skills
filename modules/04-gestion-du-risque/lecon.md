# Module 04 · Gestion du risque

**Objectif** : décider combien tu risques sur chaque trade et sur l'ensemble de ton capital, et savoir à l'avance à quoi ressembleront tes pires périodes.

**Durée** : 2 semaines · **Prérequis** : module 01

## 1. Le risque se décide avant l'entrée

Chaque trade a trois prix fixés **avant** de passer l'ordre :

- **Entrée** : où tu entres.
- **Stop** : où ton idée est invalidée. Il se place à un niveau qui a un sens sur le graphique (sous un support, à 2 ATR, etc.), jamais « là où la perte me paraît supportable ».
- **Objectif** (facultatif) : où tu prends tes gains.

La distance entrée-stop définit **1R**, l'unité de risque du trade.

## 2. Taille de position à risque fixe

On ne choisit pas la taille de la position au feeling, on la calcule :

> quantité = (capital × risque en %) / |entrée − stop|

Exemple : 10 000 EUR, risque 1 %, entrée 50, stop 48. Risque autorisé 100 EUR, risque par action 2 EUR, donc **50 actions** (2 500 EUR investis). Si le stop est plus loin, la position est plus petite : le risque reste toujours de 100 EUR.

```python
from tradeskills.risk import position_size
position_size(10_000, 0.01, 50, 48)   # 50
```

Règle de départ : **0,5 % à 1 % du capital par trade**. Les professionnels dépassent rarement 2 %.

## 3. Le R-multiple

Exprimer chaque résultat en R rend tous les trades comparables, quel que soit l'actif ou la taille :

> R = (sortie − entrée) / (entrée − stop)

Un trade qui gagne deux fois le risque initial vaut +2R. Un stop touché vaut −1R. Un trade qui perd plus de 1R signale un problème d'exécution (gap, stop déplacé) : à noter dans le journal.

## 4. L'espérance

> E = p × G − (1 − p) × P

avec p le taux de réussite, G le gain moyen et P la perte moyenne, en R.

| Taux de réussite | Gain moyen | Espérance |
| --- | --- | --- |
| 60 % | 1R | +0,20R |
| 40 % | 2R | +0,20R |
| 30 % | 2R | −0,10R |
| 30 % | 3R | +0,20R |

Un taux de réussite faible n'est pas un problème si les gains sont grands. Une espérance négative ne se corrige pas avec une taille de position, seulement avec une meilleure stratégie.

## 5. Les séries de pertes sont normales

Avec 50 % de réussite, la probabilité d'avoir au moins une série de 8 pertes d'affilée sur 200 trades dépasse 30 %. Ce n'est pas de la malchance, c'est la statistique. Avec 1 % de risque, 8 pertes font environ −7,7 % ; avec 5 %, environ −34 %.

La perte maximale (drawdown) n'est pas symétrique : après −50 %, il faut +100 % pour revenir au point de départ.

| Perte | Gain nécessaire pour revenir |
| --- | --- |
| −10 % | +11 % |
| −25 % | +33 % |
| −50 % | +100 % |
| −75 % | +300 % |

## 6. Le critère de Kelly

Kelly donne la fraction du capital qui maximise la croissance à long terme :

> f* = p − (1 − p) / b, avec b = G / P

Avec p = 50 % et b = 2, f* = 25 %. En pratique, c'est beaucoup trop : les paramètres sont estimés avec du bruit (comme la covariance dans ta thèse) et Kelly complet produit des drawdowns énormes. On utilise **un quart de Kelly au maximum**, et le plus souvent un risque fixe de 1 %. C'est le même principe que le shrinkage : accepter un léger biais pour réduire fortement la variance.

## 7. Le risque au niveau du portefeuille

- **Risque total ouvert** : la somme des risques de toutes les positions ouvertes. Limite de départ : 5 % du capital.
- **Corrélation** : trois achats sur SPY, QQQ et un ETF tech font presque un seul trade de 3R. Ta thèse a montré pourquoi la covariance compte : elle décide de la vraie diversification.
- **Règles de coupure** : par exemple, arrêt de la journée après −2R, arrêt de la semaine après −5R, révision de la stratégie après un drawdown de −10 %.

## 8. Plan de risque personnel (à remplir)

```
Capital de trading :                 ____ EUR (argent que je peux perdre)
Risque par trade :                   ____ % (0,5 à 1 %)
Risque total ouvert maximum :        ____ %
Arrêt quotidien :                    ____ R
Arrêt hebdomadaire :                 ____ R
Drawdown déclenchant une pause :     ____ %
Levier :                             aucun avant 100 trades avec espérance positive
```

## À retenir

1. La taille de position se calcule à partir du stop, jamais l'inverse.
2. Pense et mesure en R.
3. Une stratégie à espérance négative perd quoi qu'il arrive.
4. Les longues séries de pertes arrivent : ta taille de position doit leur survivre.
5. Kelly complet est trop agressif. Un risque fixe de 1 % est un bon point de départ.
