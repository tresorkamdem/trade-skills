::: {.partie pnum="Partie 0"}
# Avant de commencer {#partie0}

Comment lire ce manuel, ton poste de travail, le plan des douze prochains mois et les quelques règles qui ne changent jamais.
:::

# Comment utiliser ce manuel {#mode-emploi data-num="Introduction"}

Ce manuel est la référence écrite de ton parcours **Trade Skills**. Il accompagne le fil « Suivre le parcours de trading complet », où l'on avance module par module en interactif : là-bas tu poses tes questions et je corrige tes réponses ; ici tu retrouves tout, au calme, dans l'ordre, avec les corrigés détaillés.

Il a cinq parties :

| Partie | Contenu | Quand la lire |
| --- | --- | --- |
| **I · Le cours** | Les 12 modules du dépôt, développés, avec exercices et solutions pas à pas, puis un examen final | Pendant l'apprentissage, un module à la fois |
| **II · Tes agents** | Comment fonctionne chaque agent de ton équipe, de la donnée au message Telegram | Après les modules 02 et 03 |
| **III · Tes robots et leur calibrage** | Les poches (tes « robots »), tous leurs réglages, comment les changer et les tester en papier | Après le module 07 |
| **IV · Le suivi automatique** | Le passage du soir sur GitHub, Telegram, SESHAT, et que faire quand quelque chose casse | Dès maintenant, puis en référence |
| **V · Ta vie d'investisseur** | La routine du matin et du soir, la journée type, les revues, les check-lists, le passage à l'argent réel | Quand le parcours est fini, et chaque fois que tu doutes |

## Comment travailler un module

Chaque module suit le même plan, et il vaut la peine de respecter l'ordre :

1. **Lis la leçon une première fois** sans prendre de notes, pour avoir la vue d'ensemble.
2. **Relis-la crayon en main.** Refais chaque exemple chiffré toi-même, sans regarder le résultat.
3. **Fais les exercices sans regarder les solutions.** Un exercice raté puis corrigé t'apprend plus qu'un exercice lu.
4. **Compare avec la solution pas à pas.** Si ton résultat diffère, cherche *à quelle étape* tu t'es séparé du corrigé.
5. **Écris la fiche « À retenir » avec tes mots** dans ton journal. Si tu n'arrives pas à l'écrire, le module n'est pas fini.
6. **Coche le module** dans le `README.md` du dépôt, et dis-le dans le fil du parcours pour passer au suivant.

::: astuce
Les exercices marqués **Pratique** se font sur TradingView ou chez un courtier de démonstration. Ce sont les plus importants : savoir faire un calcul ne sert à rien si tu ne sais pas le refaire devant un vrai graphique.
:::

## Ce que tu sais déjà

Tu n'es pas un débutant comme les autres. Ta Bachelorarbeit en Wirtschaftsmathematik (HTW Berlin) sur l'optimisation de portefeuille par shrinkage de la covariance t'a déjà appris ce que la plupart des traders particuliers n'apprennent jamais :

- qu'un **backtest honnête** se fait hors échantillon, avec une fenêtre glissante ;
- qu'un **benchmark naïf** (1/n) est souvent très difficile à battre ;
- que **l'erreur d'estimation** compte plus que la finesse de l'optimisation ;
- que **le turnover coûte** : l'estimateur empirique faisait tourner le portefeuille presque 2 fois par mois, Ledoit-Wolf 0,25 fois.

Le cours s'appuie sans cesse sur ces acquis. Quand tu vois l'encadré « lien avec ta thèse », c'est que tu connais déjà l'idée sous un autre nom.

# Ton poste de travail {#poste data-num="Introduction"}

## Ce que tu as déjà en place

| Outil | État au 26 octobre 2026 | À quoi il sert |
| --- | --- | --- |
| **MacBook** | Python, Git et VS Code installés | Lire le code, lancer les solutions, modifier les réglages |
| **iPhone** | Telegram installé | Recevoir le résumé du soir et les ordres du lendemain |
| **Deux écrans** | Sur ton bureau | Graphique à gauche, journal et SESHAT à droite |
| **TradingView** | Compte gratuit *tresor_kamdem* | Graphiques, dessins, Pine Script, Strategy Tester |
| **Bot Telegram** | « Tresor Trading », secrets configurés | Les agents t'écrivent chaque soir de semaine |
| **GitHub** | Dépôt `tresorkamdem/trade-skills` | Le code, les réglages, le passage du soir automatique |
| **SESHAT** | Section Trading active | Ton tableau de bord privé et professionnel |
| **Courtier** | IBKR reporté, tout en argent fictif | Plus tard : le compte réel |

## Lancer le code du cours

Les solutions des exercices sont des fichiers Python dans le dépôt. Tu as deux façons de les lancer.

::: mac
**Dans VS Code, sur ton MacBook.** Ouvre le dossier `trade-skills` (menu *File → Open Folder*). Ouvre le terminal intégré avec **Ctrl + `** (la touche à gauche du 1 sur un clavier allemand, ou *View → Terminal*). La première fois seulement :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Ensuite, à chaque session, `source .venv/bin/activate` suffit, puis par exemple :

```bash
python modules/02-gestion-du-risque/solutions/solutions_02.py
```

Pour récupérer la dernière version du dépôt : `git pull`.
:::

**Dans le navigateur, sans rien installer** : sur la page GitHub du dépôt, bouton vert **Code → Codespaces → Create codespace on main**. Un VS Code s'ouvre dans le navigateur, avec un terminal Linux. Les mêmes commandes y marchent. Le plan gratuit de GitHub donne quelques dizaines d'heures par mois, largement assez pour les exercices.

## Organiser tes deux écrans

| Écran gauche | Écran droit |
| --- | --- |
| TradingView : un onglet hebdomadaire, un onglet journalier | Ton journal (tableur ou VS Code), SESHAT, ce manuel |
| Les dessins (supports, résistances, outil Long Position) | Les calculs : taille de position, R, check-lists |

Sur Mac, **Cmd + Tab** passe d'une application à l'autre, **Ctrl + flèches** change de bureau, et **Cmd + Maj + 4** fait une capture d'une zone (pour ton journal).

# Le plan des douze mois {#plan data-num="Introduction"}

## L'ordre des modules

Les modules sont numérotés dans l'ordre où tu les étudies : il suffit de les suivre de 01 à 11. Le risque (module 02) passe avant l'analyse, parce qu'il décide si tu survis à tes erreurs. Le module 12 (parcours pro) se lit en parallèle, du début à la fin.

| Étape | Module | Durée | Ce que tu sauras faire à la fin |
| --- | --- | --- | --- |
| 1 | 01 · Bases des marchés | 1 à 2 sem. | Lire un carnet d'ordres, chiffrer le coût d'un trade |
| 2 | 02 · Gestion du risque | 2 sem. | Calculer une taille de position, raisonner en R |
| 3 | 03 · Analyse technique | 3 sem. | Lire un graphique, tester un indicateur au lieu d'y croire |
| 4 | 04 · Analyse fondamentale | 3 sem. | Lire des comptes, faire un DCF, suivre la macro |
| 5 | 05 · Day et swing trading | 4 sem. | Écrire un plan de trading, tenir un journal |
| 6 | 06 · TradingView et Pine Script | 3 sem. | Coder un indicateur et une stratégie, créer des alertes |
| 7 | 07 · Backtesting rigoureux | 3 sem. | Distinguer un vrai avantage d'une sur-optimisation |
| 8 | 08 · Optimisation de portefeuille | 4 sem. | Choisir et défendre une méthode d'allocation |
| 9 | 09 · Performance et reporting | 2 sem. | Mesurer, expliquer et présenter une performance |
| 10 | 10 · Bourses africaines | 3 sem. | Analyser la BRVM et la BVMAC sans tomber dans leurs pièges |
| 11 | 11 · L'or | 1 sem. | Expliquer l'or et les règles du robot Or-1 |
| en continu | 12 · Parcours pro | 12 à 24 mois | Savoir comment passer à une activité avec des clients |

Cela fait environ **31 semaines de cours**, soit 7 à 8 mois à raison de 5 à 8 heures par semaine, à côté de tes études. Les mois restants servent au paper trading, à l'examen final et à la mise au point de tes robots.

## Le calendrier conseillé

| Mois | Cours | En parallèle |
| --- | --- | --- |
| 1 | Modules 01 et 02 | Le passage du soir tourne déjà : lis chaque message Telegram |
| 2 | Module 03 | Premiers dessins sur TradingView, journal d'observation (sans trades) |
| 3 | Module 04 | Calendrier macro chaque lundi |
| 4 | Module 05 | Premiers trades de démonstration, à la main, avec le journal |
| 5 | Module 06 | Ton premier script Pine ; comparaison avec la poche swing |
| 6 | Module 07 | Revue critique des backtests de tes poches |
| 7 | Module 08 | Revue de la poche long terme ; calibrage |
| 8 | Modules 09 et 10 | Premier rapport de performance de tes poches |
| 9 | Module 11 et robot Or-1 | Paliers 1 à 3 du robot or |
| 10 à 12 | Examen final, partie V | Trois mois de papier « comme en vrai » : routine complète |

## Les règles d'or

Ces règles valent pour tout le manuel. Elles ne se négocient pas, même quand une journée a l'air évidente.

::: cle
1. **Argent fictif d'abord.** Rien en réel tant que les critères chiffrés de la partie V ne sont pas remplis.
2. **Le risque se décide avant l'entrée.** Chaque position a un stop, posé au moment de l'entrée, et jamais éloigné ensuite.
3. **1 % au maximum par trade** (0,5 % pour le day trading). Pas de levier.
4. **Pas de martingale, jamais.** On ne double pas une position perdante.
5. **Un seul changement de règle à la fois, testé avant d'être appliqué.**
6. **Le journal est toujours à jour.** Un trade non noté est un trade qui ne t'apprend rien.
7. **On juge le processus, pas le résultat d'un trade.**
:::

Ces règles sont déjà programmées dans tes agents : risque par trade, coupe-circuit, refus des positions trop corrélées. La partie III te montre où les régler, et pourquoi il ne faut presque jamais les assouplir.

::: attention
Ce manuel est éducatif. Il ne contient aucun conseil personnalisé en investissement. Les chiffres réglementaires et fiscaux (Allemagne, France, zones UEMOA et CEMAC) sont donnés à titre indicatif et changent avec le temps : vérifie-les auprès des sources officielles et d'un Steuerberater avant de t'en servir.
:::
