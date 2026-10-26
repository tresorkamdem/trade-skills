::: {.partie pnum="Partie I"}
# Le cours complet {#partie1}

Les douze modules du parcours Trade Skills, développés, avec leurs exercices pratiques et des solutions guidées pas à pas : d'abord le raisonnement, puis le calcul à la main, puis la vérification en Python ou sur TradingView. Le chapitre se termine par un examen final en trois études de cas.
:::

# Bases des marchés {#m01 data-num="Module 01"}

::: objectif
Savoir exactement ce qui se passe entre le moment où tu cliques sur « acheter » et le moment où tu vois ton résultat, et ce que cela te coûte. **Durée** : 1 à 2 semaines. **Prérequis** : aucun. **Code** : `solutions_01.py`.
:::

## 1. Qui est en face de toi ?

Un marché met en relation des acheteurs et des vendeurs. Chaque ordre exécuté a une **contrepartie** : quand tu achètes 10 actions SAP, quelqu'un te les vend au même instant. Ce quelqu'un peut être :

- un **teneur de marché** (market maker), payé pour afficher en permanence un prix d'achat et un prix de vente ; il gagne la différence entre les deux ;
- un **fonds** qui exécute un gros ordre par petits morceaux, avec des algorithmes ;
- un **algorithme de haute fréquence**, qui réagit en microsecondes aux nouvelles et aux déséquilibres du carnet ;
- un **autre particulier**.

Une conséquence importante : **en trading de court terme, ton gain est en grande partie la perte de quelqu'un d'autre**, et la plupart de tes contreparties sont mieux équipées, mieux informées et plus rapides que toi. Ton avantage ne viendra donc jamais de la vitesse ni de l'information. Il ne peut venir que de quatre choses :

1. **La discipline** : respecter tes règles quand les autres paniquent ou s'emballent.
2. **L'horizon** : un fonds qui doit publier sa performance chaque mois ne peut pas toujours attendre six semaines ; toi, tu peux.
3. **La gestion du risque** : survivre aux séries de pertes, qui arrivent à tout le monde.
4. **La méthode statistique** : vérifier ce qui marche au lieu de le croire. C'est ton atout de mathématicien.

## 2. Le carnet d'ordres

Le carnet d'ordres (order book) liste tous les ordres à cours limité en attente, côté achat et côté vente.

| Côté | Prix | Quantité |
| --- | --- | --- |
| Vente (ask) | 100,04 | 300 |
| Vente (ask) | 100,02 | 500 |
| **Spread** | | |
| Achat (bid) | 100,00 | 400 |
| Achat (bid) | 99,98 | 1 000 |

![Le carnet d'ordres de la leçon : les vendeurs au-dessus, les acheteurs en dessous, le spread entre les deux.](fig/carnet.svg)

- **Bid** : le meilleur prix auquel quelqu'un veut acheter (ici 100,00). C'est le prix que tu obtiens si tu **vends** au marché.
- **Ask** : le meilleur prix auquel quelqu'un veut vendre (ici 100,02). C'est le prix que tu paies si tu **achètes** au marché.
- **Spread** = ask − bid = 0,02. Si tu achètes au marché puis revends aussitôt, tu perds le spread. C'est le premier coût invisible de chaque trade.
- **Milieu de fourchette** (mid) = (bid + ask) / 2 = 100,01. C'est le « vrai » prix de référence au même instant.
- **Liquidité** : la quantité disponible près du meilleur prix. Si tu veux acheter 1 000 titres au marché ici, tu en obtiens 500 à 100,02, puis 300 à 100,04, puis tu montes encore plus haut. Cet écart entre le prix que tu attendais et le prix moyen obtenu s'appelle le **slippage** (glissement).

::: robot
Le courtier papier de tes agents simule ce glissement : chaque exécution se fait 2 points de base (0,02 %) plus mal que l'ouverture, plus 5 points de base de frais. Ce sont les réglages `glissement_bps` et `cout_bps` de chaque poche (partie III).
:::

## 3. Les types d'ordres

| Ordre | Ce qu'il fait | Risque |
| --- | --- | --- |
| Au marché | Exécution immédiate au meilleur prix disponible | Prix incertain (slippage), surtout à l'ouverture et sur les titres peu liquides |
| Limite | Exécution à ton prix ou mieux | Peut ne jamais être exécuté |
| Stop (stop-loss) | Devient un ordre au marché quand le prix touche le seuil | Peut être exécuté bien plus bas en cas de gap |
| Stop-limite | Devient un ordre limite au seuil | Peut ne pas être exécuté et te laisser dans une perte |
| Trailing stop | Stop qui suit le prix à distance fixe | Sorti trop tôt si la distance est trop serrée |

Deux phrases à apprendre par cœur :

- un ordre **au marché** te garantit l'**exécution**, pas le **prix** ;
- un ordre **limite** te garantit le **prix**, pas l'**exécution**.

### Le gap, ennemi du stop

Un **gap** est un saut de prix entre la clôture d'une séance et l'ouverture de la suivante, en général après une nouvelle tombée la nuit (résultats, décision politique). Ton ordre stop à 47 € ne te protège pas d'une ouverture à 42 € : il devient un ordre au marché dès que le prix touche ou dépasse 47, et le premier prix disponible est 42. Le stop limite la perte **dans des conditions normales** ; il ne la garantit pas.

Règle de base : **chaque position a un stop défini avant l'entrée**. Le module 02 explique comment le placer et comment en déduire la taille de la position.

## 4. Les classes d'actifs

| Classe | Exemples | Heures (heure de Berlin) | Particularités |
| --- | --- | --- | --- |
| Actions | SAP, Allianz, Apple | Xetra 9 h 00 à 17 h 30 ; Wall Street 15 h 30 à 22 h 00 | Résultats trimestriels, dividendes, gaps à l'ouverture |
| ETF | MSCI World (EUNL), S&P 500 (SXR8) | Heures de bourse | Diversification immédiate, idéal pour la gestion de portefeuille |
| Indices (CFD, futures) | DAX, S&P 500 | Presque 24 h/24 | Levier, contrats standardisés |
| Forex | EUR/USD, EUR/XAF | 24 h/24 en semaine | Levier élevé, influencé par les banques centrales. Le XAF est arrimé à l'euro |
| Crypto | BTC, ETH | 24 h/24, 7 j/7 | Très volatil, risque de plateforme |
| Matières premières | Or (4GLD), pétrole | Variable | Saisonnalité, géopolitique (module 11 pour l'or) |

::: attention
**Les ETF américains (SPY, QQQ…) ne s'achètent pas depuis un compte allemand** : il leur manque le document d'information clé (KID, règlement PRIIPs) exigé dans l'Union européenne. Tu utiliseras leurs équivalents **UCITS** cotés sur Xetra : SXR8 pour le S&P 500, SXRV pour le Nasdaq 100, EUNL pour le MSCI World. C'est pour cela que tes poches tradent ces codes-là. Sur TradingView, tu peux bien sûr *regarder* SPY.
:::

## 5. Ce que coûte un trade

> Coût total = frais du courtier + spread + slippage + financement (positions à levier tenues la nuit) + impôts

En Allemagne, les gains sont soumis à l'**Abgeltungsteuer** de 25 %, plus le Solidaritätszuschlag (5,5 % de l'impôt), soit 26,375 %, plus l'impôt d'Église si tu y es assujetti. Chaque année, les premiers 1 000 € de revenus du capital sont exonérés (**Sparerpauschbetrag**), à condition d'avoir déposé un **Freistellungsauftrag** auprès de ton courtier allemand.

### L'exemple qui change tout

20 allers-retours par mois, avec 0,05 % de spread et 1 € de frais sur une position de 2 000 € :

- frais : 2 ordres × 1 € = 2 €, soit 0,10 % de 2 000 € ;
- spread : 0,05 % ;
- total ≈ 0,15 % par aller-retour (on arrondit à 0,10 % dans la leçon d'origine en ne comptant que les frais) ;
- 20 allers-retours × 0,10 % = **2 % par mois, 24 % par an**, avant d'avoir gagné quoi que ce soit.

![Coût annuel en fonction du nombre d'allers-retours par mois. Le swing trading vit dans la zone de gauche ; le day trading dans celle de droite.](fig/couts_frequence.svg)

C'est la même leçon que le turnover de ta thèse : **plus tu fais tourner le portefeuille, plus les coûts mangent la performance**.

## 6. Levier et marge

Le **levier** permet de contrôler une position plus grande que ton capital. Avec un levier de 10, 1 000 € contrôlent 10 000 €, et une baisse de **10 %** du marché efface **100 %** de ton capital. Le levier ne change pas la qualité d'une stratégie, il multiplie seulement le résultat, dans les deux sens, et il raccourcit le chemin vers la ruine.

La **marge** est l'argent bloqué chez le courtier pour garantir la position. Quand la perte la dépasse, le courtier te demande de remettre de l'argent (**appel de marge**) ou ferme la position automatiquement, au pire moment.

Pour l'instant : **pas de levier**. Le module 11 montre sur l'or ce qu'un levier de 20:1 aurait fait en avril 2013.

## 7. Choisir un courtier

| Critère | Question à poser | Pour toi |
| --- | --- | --- |
| Régulation | BaFin ou une autorité européenne ? | Indispensable. Fuis les courtiers offshore (Seychelles, Vanuatu…) |
| Frais réels | Combien coûte *mon* style de trading ? | Calcule un aller-retour type (exercice 2) |
| Marchés | Xetra, US, ETF UCITS, options ? | Xetra et US au minimum |
| Export | Puis-je exporter mes transactions ? | Pour le journal et la déclaration d'impôts |
| Démo | Y a-t-il un compte papier ? | IBKR propose un compte papier complet |
| Fiscalité | Le courtier prélève-t-il l'impôt allemand ? | Courtier allemand : oui. IBKR : non, tu déclares toi-même (Anlage KAP) |

Le comparatif détaillé est dans `agents/courtiers.md` : **IBKR** pour le swing et le day trading (frais bas, tous les marchés, compte papier), **Trade Republic** ou **Scalable** pour un plan d'épargne ETF long terme (Sparplan), simple et sans frais.

::: retenir
1. Le spread et le slippage sont des coûts réels, invisibles sur un graphique.
2. Un ordre au marché te garantit l'exécution, pas le prix. Un ordre limite te garantit le prix, pas l'exécution.
3. Un stop ne protège pas d'un gap.
4. Plus tu trades souvent, plus tes coûts doivent être faibles.
5. Pas de levier tant que ton journal ne montre pas une espérance positive sur au moins 100 trades.
:::

## Exercices du module 01

::: enonce
**1 · Carnet d'ordres.** Avec le carnet de la leçon, tu passes un ordre d'achat au marché de 700 titres. Quel est ton prix moyen ? Combien perds-tu par rapport au milieu de fourchette (100,01) ?
:::

::: enonce
**2 · Coût d'une stratégie.** Tu fais 3 allers-retours par jour, 20 jours par mois, avec 0,03 % de spread, 0,02 % de slippage et 1 € de frais par ordre, sur une position de 5 000 €. Quel est ton coût annuel en pourcentage de la position ? Quel rendement brut faut-il pour être à zéro ?
:::

::: enonce
**3 · Gap et stop.** Tu détiens 100 actions achetées à 50 € avec un stop à 47 €. Une mauvaise nouvelle tombe la nuit et l'action ouvre à 42 €. Combien perds-tu, et combien pensais-tu risquer ? Quel instrument aurait pu éviter cette surprise, et à quel prix ?
:::

::: enonce
**4 · Levier.** Avec 2 000 € et un levier de 5 sur le DAX, quelle baisse de l'indice efface 50 % de ton capital ? Et 100 % ?
:::

::: enonce
**5 · Ta thèse.** Dans ta Bachelorarbeit, l'estimateur empirique a un turnover mensuel de 1,907 (fenêtre de 60 mois). Avec un coût de 0,20 % par unité de rotation, combien de rendement annuel perd-il ? Et Ledoit-Wolf (turnover 0,246) ?
:::

::: enonce
**6 · Pratique.** Sur TradingView, ouvre le graphique de `XETR:EUNL` en journalier, puis en 5 minutes. Note le spread affiché dans la fenêtre d'ordre du *Paper Trading* de TradingView à trois moments : 9 h 05, 12 h 00 et 17 h 20. Passe un ordre limite, un ordre stop et un ordre au marché en Paper Trading. Note pour chacun le prix demandé et le prix obtenu dans ton journal.
:::

## Solutions pas à pas

::: solution
**Exercice 1 · Carnet d'ordres**

*Étape 1, lire le carnet côté vente* : un achat au marché « mange » les vendeurs du moins cher au plus cher. Il y a 500 titres à 100,02, puis 300 à 100,04.

*Étape 2, remplir l'ordre* : 700 titres = 500 à 100,02 + **200** à 100,04 (il reste 100 titres à 100,04 dans le carnet).

*Étape 3, prix moyen* :

```
(500 × 100,02 + 200 × 100,04) / 700 = (50 010 + 20 008) / 700 = 70 018 / 700 = 100,0257
```

*Étape 4, coût par rapport au milieu* : (100,0257 − 100,01) × 700 = 0,0157 × 700 ≈ **11,00 €**.

*Interprétation* : sur 70 000 € achetés, 11 € de coût d'exécution, soit 0,016 %. C'est peu ici parce que le titre est liquide. Sur un titre de la BVMAC (module 10), le même ordre pourrait coûter plusieurs pourcents.

*Vérification* : `python modules/01-bases-des-marches/solutions/solutions_01.py` affiche « Prix moyen 100.0257, coût vs milieu 11.00 EUR ».
:::

::: solution
**Exercice 2 · Coût d'une stratégie**

*Étape 1, coût d'un aller-retour* (un achat + une vente) :

- spread : payé une fois sur l'aller-retour (tu achètes à l'ask, tu revends au bid) : 0,03 % × 5 000 = 1,50 € ;
- slippage : à l'entrée **et** à la sortie : 2 × 0,02 % × 5 000 = 2,00 € ;
- frais : 2 ordres × 1 € = 2,00 € ;
- **total : 5,50 € par aller-retour**, soit 0,11 % de la position.

*Étape 2, nombre d'allers-retours par an* : 3 × 20 × 12 = 720.

*Étape 3, coût annuel* : 720 × 5,50 = **3 960 €**, soit **79 %** de la position de 5 000 €.

*Étape 4, conclusion* : il faut gagner 79 % brut par an juste pour être à zéro. Aucune stratégie de particulier ne fait cela durablement. Le day trading à haute fréquence n'est rentable qu'avec des coûts quasi nuls, ce qui n'est pas ton cas.
:::

::: solution
**Exercice 3 · Gap et stop**

*Étape 1, risque prévu* : (50 − 47) × 100 = **300 €**.

*Étape 2, ce qui se passe vraiment* : à l'ouverture, le premier prix est 42 €. Le stop à 47 est « traversé » ; il devient un ordre au marché, exécuté vers 42 €.

*Étape 3, perte réelle* : (50 − 42) × 100 = **800 €**, soit 2,7 fois le risque prévu, ou −2,7R (module 02).

*Étape 4, la parade* : une **option de vente (put)** de prix d'exercice 47 € te donne le droit de vendre à 47 € quoi qu'il arrive. Elle plafonne vraiment la perte, mais tu paies une **prime** à l'achat, perdue si rien ne se passe. En pratique, on accepte le risque de gap, on le réduit en évitant de garder une position la veille de résultats (module 04), et on le mesure dans le journal (une perte de plus de 1R est toujours notée avec sa cause).

::: robot
Le courtier papier de tes agents simule ce cas : « si l'ouverture saute le stop, la sortie se fait à l'ouverture, pas au stop ». Tes backtests ne sont donc pas trop optimistes sur les gaps.
:::
:::

::: solution
**Exercice 4 · Levier**

*Étape 1* : avec un levier de 5, ton exposition est 5 × 2 000 = 10 000 €.

*Étape 2* : une baisse de x % du DAX te fait perdre x % × 10 000 €, soit 5 × x % de ton capital.

*Étape 3* : perdre 50 % du capital (1 000 €) demande une baisse de 1 000 / 10 000 = **10 %**. Perdre 100 % demande **20 %**.

*Étape 4, mise en perspective* : le DAX a baissé de plus de 20 % en 2008, en 2011, en 2020 et en 2022. Avec un levier de 5, chacune de ces années aurait vidé le compte.
:::

::: solution
**Exercice 5 · Ta thèse**

*Étape 1, formule* : coût annuel = turnover mensuel × coût par unité × 12.

*Étape 2, estimateur empirique* : 1,907 × 0,002 × 12 = **4,58 % par an**.

*Étape 3, Ledoit-Wolf* : 0,246 × 0,002 × 12 = **0,59 % par an**.

*Étape 4, conclusion* : l'écart de près de 4 points par an s'ajoute à l'écart de volatilité de ta thèse. Après coûts, l'estimateur empirique est encore plus nettement battu. C'est un argument fort pour l'offre C1 de MAÀT.

*Vérification* : `portfolio.compare(R, window=60, cost_bps=20)` donne directement les rendements nets.
:::

::: solution
**Exercice 6 · Pratique** (guidé)

1. Sur TradingView, tape `EUNL` dans la recherche (ou **Cmd + K**), choisis **XETR:EUNL**.
2. En bas de l'écran, ouvre le panneau **Trading** et connecte **Paper Trading** (gratuit, compte fictif de 100 000 $).
3. Clique sur **Acheter** : la fenêtre d'ordre montre le bid et l'ask. Note le spread à 9 h 05 (juste après l'ouverture : souvent large), 12 h 00 (calme : étroit) et 17 h 20 (avant la clôture : étroit, beaucoup de volume).
4. Passe un **ordre limite** à un prix un peu sous le marché : il attend. Passe un **ordre stop** au-dessus du marché : il s'exécutera si le prix monte. Passe un **ordre au marché** : exécution immédiate.
5. Dans ton journal, note pour chacun : prix demandé, prix obtenu, écart.

*Ce que tu dois observer* : le spread est le plus large à l'ouverture, l'ordre au marché s'exécute à l'ask, l'ordre limite peut rester non exécuté toute la journée. Sur le plan gratuit, les données de certaines bourses peuvent être différées de 15 minutes : c'est sans importance pour cet exercice, mais note-le.
:::
