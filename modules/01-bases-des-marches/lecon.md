# Module 01 · Bases des marchés

**Objectif** : savoir exactement ce qui se passe entre le moment où tu cliques sur « acheter » et le moment où tu vois ton résultat, et ce que cela te coûte.

**Durée** : 1 à 2 semaines · **Prérequis** : aucun

## 1. Qui est en face de toi ?

Un marché met en relation des acheteurs et des vendeurs. Chaque ordre exécuté a une contrepartie : market makers, fonds, algorithmes, autres particuliers. Une conséquence importante : **en trading de court terme, ton gain est en grande partie la perte de quelqu'un d'autre**, et la plupart de tes contreparties sont mieux équipées que toi. Ton avantage doit donc venir d'ailleurs : discipline, horizon de temps, gestion du risque, méthode statistique.

## 2. Le carnet d'ordres

| Côté | Prix | Quantité |
| --- | --- | --- |
| Vente (ask) | 100,04 | 300 |
| Vente (ask) | 100,02 | 500 |
| **Spread** | | |
| Achat (bid) | 100,00 | 400 |
| Achat (bid) | 99,98 | 1 000 |

- **Bid** : meilleur prix auquel quelqu'un veut acheter. **Ask** : meilleur prix auquel quelqu'un veut vendre.
- **Spread** = ask − bid (ici 0,02). Si tu achètes au marché puis revends tout de suite, tu perds le spread.
- **Liquidité** : la quantité disponible près du meilleur prix. Si tu veux acheter 1 000 titres au marché ici, tu en obtiens 500 à 100,02 et 300 à 100,04, puis tu montes plus haut : c'est le **slippage**.

## 3. Les types d'ordres

| Ordre | Ce qu'il fait | Risque |
| --- | --- | --- |
| Au marché | Exécution immédiate au meilleur prix disponible | Prix incertain (slippage), surtout à l'ouverture et sur les titres peu liquides |
| Limite | Exécution à ton prix ou mieux | Peut ne jamais être exécuté |
| Stop (stop-loss) | Devient un ordre au marché quand le prix touche le seuil | Peut être exécuté bien plus bas en cas de gap |
| Stop-limite | Devient un ordre limite au seuil | Peut ne pas être exécuté et te laisser dans une perte |
| Trailing stop | Stop qui suit le prix à distance fixe | Sorti trop tôt si la distance est trop serrée |

Règle de base : **chaque position a un stop défini avant l'entrée**. Le module 02 explique comment le placer et comment en déduire la taille de la position.

## 4. Les classes d'actifs

| Classe | Exemples | Heures | Particularités |
| --- | --- | --- | --- |
| Actions | SAP, Apple | Heures de bourse | Résultats trimestriels, dividendes, gaps à l'ouverture |
| ETF | SPY, un ETF MSCI World | Heures de bourse | Diversification immédiate, idéal pour la gestion de portefeuille |
| Indices (CFD, futures) | DAX, S&P 500 | Presque 24 h/24 | Levier, contrats standardisés |
| Forex | EUR/USD, EUR/XAF | 24 h/24 en semaine | Levier élevé, influencé par les banques centrales. Le XAF est arrimé à l'euro |
| Crypto | BTC, ETH | 24 h/24, 7 j/7 | Très volatil, risque de plateforme |
| Matières premières | Or, pétrole | Variable | Saisonnalité, géopolitique |

## 5. Ce que coûte un trade

Coût total = **frais du broker** + **spread** + **slippage** + **financement** (positions à levier tenues la nuit) + **impôts** (en Allemagne, Abgeltungsteuer de 25 % plus Solidaritätszuschlag sur les gains, avec un Sparerpauschbetrag annuel de 1 000 EUR).

Exemple : 20 allers-retours par mois à 0,05 % de spread et 1 EUR de frais sur 2 000 EUR, soit 0,10 % par aller-retour. Cela fait 2 % par mois, **24 % par an**, avant même d'avoir gagné quoi que ce soit. C'est la même leçon que le turnover de ta thèse : plus tu fais tourner le portefeuille, plus les coûts mangent la performance.

## 6. Levier et marge

Avec un levier de 10, une baisse de 10 % efface tout ton capital. Le levier ne change pas la qualité d'une stratégie, il multiplie seulement le résultat, dans les deux sens. Pour l'instant : **pas de levier**.

## 7. Choisir un broker

Critères : régulation (BaFin ou une autorité européenne), frais réels sur ton style de trading, accès aux marchés voulus, export des transactions (pour ton journal et ta déclaration d'impôts), et un compte démo pour le paper trading.

## À retenir

1. Le spread et le slippage sont des coûts réels, invisibles sur un graphique.
2. Un ordre au marché te garantit l'exécution, pas le prix. Un ordre limite te garantit le prix, pas l'exécution.
3. Plus tu trades souvent, plus tes coûts doivent être faibles.
4. Pas de levier tant que ton journal ne montre pas une espérance positive.
