# Examen final : trois études de cas {#examen data-num="Fin de la partie I"}

::: objectif
Vérifier que tu sais **assembler** les modules : risque, analyse, backtest, portefeuille et reporting. Chaque cas se fait en une séance de 2 à 3 heures, sans regarder le corrigé. Tu as réussi l'examen si tu obtiens l'essentiel des trois corrigés, avec le bon raisonnement, même si tes chiffres diffèrent un peu.
:::

## Cas 1 · Un trade de swing de bout en bout

Le vendredi soir, le message Telegram de tes agents indique pour la poche swing : « 🟢 [swing] ACHAT 12 SAP.DE, stop 203,48 (demain : entree) ». Tu décides de vérifier le trade toi-même avant de le reproduire dans ton Paper Trading TradingView. Données : capital de la poche 13 164 €, risque 1 %, clôture de SAP 214,40 €, ATR(14) 5,46 €, MM200 à 195 €, plus haut des 20 jours précédents 213,10 €, résultats trimestriels de SAP dans 4 jours, risque déjà ouvert dans la poche 2,0 %, positions tenues ALV.DE et AAPL.

::: enonce
1. Les trois conditions de la règle d'entrée sont-elles remplies ?
2. Retrouve le stop et la quantité proposés par l'agent, en vérifiant les deux plafonds de l'agent Budget (poids maximal 25 %, cash disponible d'environ 7 400 €).
3. L'agent Risque acceptera-t-il le trade (risque total maximal 6 %) ?
4. Quelle information l'agent ignore-t-il, et que fais-tu dans ton Paper Trading manuel ?
5. Lundi, SAP ouvre à 209 € après une rumeur. Que fait le courtier papier ?
:::

::: solution
**1. Conditions.** Tendance : 214,40 > MM200 (195) ✓. Cassure : 214,40 > plus haut 20 jours (213,10) ✓. Stop calculable (ATR connu) ✓.

**2. Stop et taille.** Stop = 214,40 − 2 × 5,46 = **203,48 €** : c'est celui du message. Risque par titre 10,92 € ; risque autorisé 1 % × 13 164 = 131,64 € ; 131,64 / 10,92 = 12,05 → **12 titres** (arrondi à l'inférieur). Plafond de poids : 25 % × 13 164 / 214,40 = 15 titres, non limitant. Plafond de cash : 7 400 / (214,40 × 1,01) = 34 titres, non limitant. L'agent propose donc bien 12 titres, soit 2 573 € investis.

**3. Risque.** Nouveau risque : 12 × 10,92 = 131 €, soit 1,0 % de la poche. Total : 2,0 + 1,0 = 3,0 % < 6 % ✓. Il reste à vérifier la corrélation sur 60 jours avec ALV.DE et AAPL : si l'une dépassait 0,8, l'agent refuserait (c'est arrivé à SXRV, corrélé à 0,95 avec une position tenue, dans le rapport du 26 octobre).

**4. Information ignorée.** Les **résultats dans 4 jours**. Les agents ne regardent que les prix. Ton plan (module 05) dit : pas de résultats pendant la durée prévue, ou position réduite. Pour un swing de plusieurs semaines, tu prends le trade à **taille réduite de moitié** (risque 0,5 %) ou tu attends le lendemain des résultats. Note la décision et sa raison dans le journal : dans 3 mois, tu sauras si cette règle humaine ajoute ou retire de la valeur.

**5. Ouverture à 209 €.** L'ordre d'achat s'exécute à l'ouverture (209 € + glissement). 209 > 203,48 : pas de gap sous le stop, l'achat a lieu. L'ouverture est plus basse que prévu : le risque par titre devient 5,52 €, la quantité reste 12 et le risque réel tombe à 66 € (la réduction automatique de quantité ne joue que si l'ouverture est **plus haute** que prévu). Le stop reste à 203,48.
:::

## Cas 2 · Une stratégie trop belle

Un ami t'envoie une capture : une stratégie Pine sur le Nasdaq 100, croisement de moyennes 17/83 avec un filtre RSI(9) > 52 et un stop à 1,7 ATR, profit factor 2,9, Sharpe 2,4 sur 4 ans, 41 trades, « testée sur TradingView sans frais ». Il veut que tu la mettes dans une poche.

::: enonce
1. Liste tous les signaux d'alerte.
2. Décris le protocole complet pour la juger, avec les outils du dépôt.
3. Que réponds-tu à ton ami si le walk-forward donne un Sharpe de 0,3 et le Sharpe dégonflé 0,40 ?
:::

::: solution
**1. Signaux d'alerte.** Paramètres « étranges » (17, 83, 9, 52, 1,7) : signature d'une recherche sur grille. 5 paramètres pour 41 trades. Pas de frais ni de glissement. 4 ans seulement (régime de marché unique). Sharpe 2,4 : exceptionnel sur données journalières. Un seul marché. Nombre d'essais inconnu.

**2. Protocole.** (a) Ajouter frais et glissement (0,05 % et 2 ticks). (b) Exporter ou télécharger 15 à 20 ans de données ; backtester en Python. (c) Grille de sensibilité autour des valeurs : les voisins (15/80, 20/90, RSI 50…) doivent aussi marcher. (d) Walk-forward 3 ans / 1 an. (e) Sharpe dégonflé avec un nombre d'essais estimé (au minimum le nombre de combinaisons plausibles). (f) Test sur `synthetic_ohlcv` : aucune performance. (g) Autres marchés (S&P 500, DAX). (h) Si tout passe, une poche papier de 3 mois.

**3. Réponse.** « La stratégie a été ajustée au passé. Hors échantillon, son Sharpe tombe à 0,3, et il n'y a que 40 % de chances que son vrai Sharpe soit positif. Elle ne vaut pas mieux qu'un ETF Nasdaq acheté et gardé, qui coûte moins cher. Je ne la mets pas en poche. »
:::

## Cas 3 · Un client de la diaspora

Une connaissance de 35 ans, ingénieure à Hambourg, originaire du Cameroun, a 30 000 € d'épargne et peut épargner 500 € par mois. Elle te demande « comment investir, y compris un peu en Afrique ». Horizon 15 ans. Elle a paniqué et tout vendu en mars 2020.

::: enonce
1. Que peux-tu légalement faire pour elle aujourd'hui, et que ne peux-tu pas faire ?
2. Dans le cadre légal, rédige les grandes lignes d'un exemple pédagogique d'allocation, avec une méthode du module 08 et une part africaine.
3. Quelles mesures de risque lui présentes-tu, et pourquoi pas le Sharpe ?
4. Quelle règle de comportement est la plus importante pour elle ?
:::

::: solution
**1. Cadre légal.** Sans statut (§34f ou Haftungsdach), tu **ne peux pas** lui recommander personnellement des produits ni gérer son argent. Tu **peux** lui expliquer des méthodes générales, lui montrer un exemple pédagogique non personnalisé, et l'orienter vers un conseiller agréé. Dis-le clairement dès le début : c'est aussi ce qui rend MAÀT crédible.

**2. Exemple pédagogique** (non personnalisé). Cœur en ETF UCITS (MSCI World, Émergents, obligations d'État zone euro, or), en **parité de risque** ou 1/n (simple, stable, facile à expliquer), plan d'épargne mensuel (Sparplan) chez un courtier allemand. Part africaine **petite et bornée** (par exemple 5 à 10 % au maximum du patrimoine), long terme, titres liquides de la BRVM ou obligations de la BVMAC via une SGI ou un PSI agréé, ordres à cours limité, rééquilibrage annuel, scénario de dévaluation de 50 % présenté à part.

**3. Mesures.** La **perte maximale** et le temps pour revenir au plus haut (« en 2008, ce portefeuille aurait perdu environ 25 % et mis 3 ans à revenir »), la **CVaR** (la perte moyenne des pires mois) et le scénario de stress FCFA. Pas le Sharpe : il ne parle pas à quelqu'un qui a paniqué en 2020, et il cache l'asymétrie des pertes.

**4. Règle de comportement.** **Ne jamais vendre dans la panique** : décider à l'avance par écrit ce qu'elle fera si le portefeuille perd 20 % (continuer le plan d'épargne, rééquilibrer). Le plan d'épargne automatique est son meilleur outil : il achète davantage quand les prix sont bas, sans qu'elle ait à décider.
:::
