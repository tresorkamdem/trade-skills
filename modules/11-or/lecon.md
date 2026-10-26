# Module 11 · L'or

**Objectif** : savoir expliquer pourquoi l'or monte ou baisse, connaître les façons de le trader depuis l'Allemagne avec leurs coûts et leurs risques, et comprendre les règles de risque du robot Or-1 avant de le construire.

**Durée** : 1 semaine · **Prérequis** : modules 01 et 02 · **Outils** : TradingView (gratuit suffit), `tradeskills.indicators`

> Les chiffres de cette leçon (frais, règles fiscales, plafonds de levier, prix historiques arrondis) peuvent changer ou être approximatifs. Vérifie chacun avant de t'en servir : xetra-gold.com, bafin.de, esma.europa.eu, gold.org (World Gold Council). Pour la fiscalité, demande à un Steuerberater.

## 1. L'or n'est pas une action

Une action te donne une part d'une entreprise qui produit des bénéfices et verse des dividendes. **L'or ne produit rien et ne verse rien.** Son prix dépend uniquement de ce que les gens sont prêts à payer pour le détenir. Conséquences pour toi :

- pas d'analyse fondamentale classique (pas de bénéfices, pas de PER) : on analyse les **causes macroéconomiques** et la **tendance du prix** ;
- détenir de l'or a un **coût d'opportunité** : l'argent placé en or ne rapporte pas d'intérêts. Quand les taux montent, ce coût augmente, et l'or devient moins attractif ;
- l'or a eu de **très longues tendances**, à la hausse comme à la baisse. C'est pour ça que le robot Or-1 est un suiveur de tendance.

**Unité** : l'or se cote en dollars par **once troy** (1 once = 31,1035 g). Le symbole international est **XAU**, donc XAU/USD = prix d'une once en dollars.

## 2. Ce qui fait bouger l'or

| Facteur | Effet habituel | Pourquoi | Où le regarder sur TradingView |
| --- | --- | --- | --- |
| **Taux d'intérêt réels** (taux moins inflation attendue) | Taux réels en hausse → or en baisse | Le coût d'opportunité de l'or augmente | `FRED:DFII10` (taux réel américain à 10 ans) |
| **Dollar américain** | Dollar en hausse → or en baisse (en dollars) | L'or devient plus cher pour le reste du monde | `TVC:DXY` |
| **Achats des banques centrales** | Achats massifs → soutien du prix | Chine, Inde, Pologne, Turquie… diversifient leurs réserves hors dollar, à un rythme très élevé depuis 2022 | Rapports trimestriels sur gold.org |
| **Peur et crises** (guerres, crise bancaire, pandémie) | Peur → or en hausse, souvent | Valeur refuge | Actualité, `TVC:VIX` |
| **Inflation** | Inflation durable → or en hausse, mais pas toujours | L'or garde son pouvoir d'achat sur des décennies, mal sur quelques années | `FRED:CPIAUCSL` |
| **Demande physique** (bijoux en Inde et en Chine, ETF) | Saisonnalité, flux d'achat | Mariages, fêtes, entrées et sorties des ETF or | gold.org |

Attention : ces relations sont **des tendances, pas des lois**. En 2022, les taux réels ont fortement monté et l'or aurait « dû » chuter ; il a seulement baissé un peu, parce que les banques centrales achetaient en masse. C'est exactement ce que tu apprendras à repérer dans les exercices.

## 3. Quelques épisodes à connaître

Prix arrondis, en dollars par once :

| Période | Ce qui s'est passé | Mouvement |
| --- | --- | --- |
| 2001 → 2011 | Dollar faible, crise de 2008, taux à zéro | d'environ 270 $ à environ 1 900 $ |
| 2011 → 2015 | Reprise économique, fin annoncée des achats de la Fed | baisse d'environ 45 % |
| avril 2013 | Krach : plus de 13 % de baisse en deux séances | le genre de journée qui ruine un compte à levier |
| mars 2020 | Panique Covid : l'or baisse d'abord (tout le monde vend pour avoir du cash), puis monte à un record en août | environ − 12 %, puis + 40 % |
| 2022 | Hausse brutale des taux ; banques centrales acheteuses | baisse limitée en dollars, hausse en euros (l'euro a chuté) |
| 2024 → 2025 | Achats des banques centrales, tensions géopolitiques, baisse des taux attendue | records successifs, au-dessus de 3 000 $ en 2025 |

Retiens deux choses : l'or peut **perdre presque la moitié de sa valeur en quelques années**, et il peut **baisser au début d'une crise** avant de jouer son rôle de refuge.

## 4. Quand l'or se négocie

L'or se négocie presque 24 h sur 24 du lundi au vendredi, mais pas avec la même activité :

- **Asie** (nuit en Allemagne) : calme, sauf nouvelles chinoises ou indiennes ;
- **Londres** (à partir de 9 h, heure allemande) : le cœur du marché physique. Deux enchères de référence chaque jour, le *LBMA Gold Price* (10 h 30 et 15 h, heure de Londres) ;
- **New York** (après-midi en Allemagne) : les contrats à terme du COMEX et les chiffres économiques américains (emploi, inflation, décisions de la Fed). Le **chevauchement Londres + New York** est le moment le plus actif et le plus volatil.

Le robot Or-1 travaille **en journalier** : il regarde la clôture une fois par jour et ne réagit pas aux mouvements de l'après-midi. C'est voulu.

## 5. Comment trader l'or depuis l'Allemagne

| | ETC Xetra-Gold (4GLD) | CFD ou spot XAU/USD | Micro-future (MGC) |
| --- | --- | --- | --- |
| Ce que tu détiens | Un titre adossé à de l'or physique (environ 1 g par titre), avec droit à la livraison | Un contrat avec ton courtier sur la différence de prix | Un contrat à terme de 10 onces |
| Devise | Euro | Dollar | Dollar |
| Levier | Aucun | Jusqu'à 20:1 pour un particulier en Europe | Élevé (marge de quelques %) |
| Vente à découvert | Non (en pratique) | Oui | Oui |
| Coûts | Frais annuels d'environ 0,3 % + frais d'ordre + écart achat-vente | Écart + frais de financement chaque nuit | Commission + roulement des contrats |
| Fiscalité allemande | Gain exonéré après 12 mois de détention (jurisprudence du BFH, 2015) ; sinon imposé comme gain privé | Revenus de capitaux (Abgeltungsteuer), règles spéciales sur les pertes de dérivés | Idem CFD |
| Pour le robot Or-1 | **Oui** | Plus tard, éventuellement | Non, trop gros |

**Prix de 4GLD** : environ le prix d'un gramme d'or en euros, donc

```
prix 4GLD ≈ (XAU/USD ÷ EUR/USD) ÷ 31,1035
```

Si le dollar monte face à l'euro, l'or en euros monte même quand l'or en dollars ne bouge pas. C'est pour ça que le robot calcule ses signaux sur XAU/USD (20 ans de données propres) mais que ses gains et pertes se comptent en euros sur 4GLD.

## 6. Le levier, et pourquoi la martingale ruine

**Le levier.** Avec un levier de 20:1, une marge de 1 000 € contrôle 20 000 € d'or. Une baisse de **5 %** de l'or fait perdre 1 000 €, **toute la marge**. L'or a fait − 13 % en deux jours en 2013. Ton courtier ferme alors ta position automatiquement : la perte est réelle, même si l'or remonte le lendemain.

**La martingale.** Le robot double la taille de sa position après chaque perte, pour « se refaire » au premier gain. Sur un compte de démonstration, le résultat est magnifique : 90 % de trades gagnants, une courbe de capital qui monte tout droit. Mais :

- après **n pertes de suite**, la position vaut 2ⁿ fois la position de départ : après 10 pertes, 1 024 fois ;
- une série de 8 à 10 pertes finit toujours par arriver (une tendance forte contre le robot suffit) ;
- ce jour-là, la marge ne suffit plus, et **le compte est vidé en une fois**.

C'est le profil du robot vu sur TikTok : des captures de comptes qui passent de 1 000 € à 20 000 €, souvent en démo, promues par des affiliés payés à chaque compte ouvert chez le courtier. Tu verras au palier 3 la date exacte où une martingale aurait ruiné le compte sur les vraies données de l'or.

## 7. Les règles d'Or-1, en résumé

Tu dois pouvoir expliquer chacune avec tes mots avant le palier 2 :

| Règle | Valeur | Pourquoi |
| --- | --- | --- |
| Filtre de tendance | Clôture au-dessus de la moyenne mobile 200 jours | On n'achète pas dans une tendance baissière |
| Entrée | Clôture au-dessus du plus haut des 50 derniers jours | On entre quand la hausse se confirme |
| Stop initial | 2,5 × ATR(20) sous l'entrée | Le stop s'adapte à la nervosité du marché |
| Sortie | Clôture sous le plus bas des 20 derniers jours, ou stop suiveur à 3 × ATR(20) | On rend une partie du gain, mais on ne laisse jamais un gain devenir une grosse perte |
| Taille | 1 % du capital risqué par trade | 10 pertes de suite = environ − 10 %, pas la ruine |
| Coupe-circuit | Arrêt à − 15 % depuis le plus haut | Si le robot va plus mal que prévu, on arrête et on analyse |

**L'ATR** (Average True Range, module 03) mesure l'amplitude moyenne d'une journée. Si l'or bouge en moyenne de 30 € par jour, un stop à 5 € serait touché par le bruit ; un stop à 2,5 × 30 = 75 € laisse respirer le trade.

**La taille de position** (module 02) :

```
nombre de titres = (capital × 1 %) ÷ (prix d'entrée − stop)
```

Plus le stop est loin, plus la position est petite. Le risque en euros reste le même à chaque trade.

## 8. Validation du palier 0

Tu as terminé ce palier quand tu sais, **sans regarder la leçon** :

1. expliquer en 3 phrases pourquoi l'or a monté ou baissé sur une période que tu choisis (exercice 3) ;
2. dire pourquoi Or-1 trade 4GLD et pas un CFD à levier ;
3. calculer la taille d'une position d'Or-1 à partir du capital, du prix et de l'ATR.

Ensuite, palier 1 : les données.
