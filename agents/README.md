# Équipe d'agents de trading

Une équipe d'agents, inspirée des « 11 agents » qui veulent remplacer un Terminal Bloomberg, mais construite sur le code de ce dépôt et organisée en **poches** : chaque poche a son capital, son style et ses règles, et elle est suivie séparément.

| Poche | Style | Barres | Règles |
| --- | --- | --- | --- |
| `swing` | Swing trading | journalières | Cassure du plus haut de 20 jours au-dessus de la moyenne 200 jours, stop à 2 ATR qui remonte, sortie sous le plus bas de 10 jours (le système de `pine/systeme_tendance_strategie.pine`) |
| `day` | Day trading | 5 minutes | Cassure du range des 30 premières minutes au-dessus du VWAP, stop sous le range, objectif 2R, tout est fermé en fin de séance |
| `long_terme` | Allocation | journalières | Portefeuille de variance minimale Ledoit-Wolf sans vente à découvert (ta thèse), rééquilibré chaque mois |
| `tradingview` | Signaux | journalières | Tes alertes TradingView : achat à l'ouverture qui suit l'alerte, stop de l'alerte (ou 2 ATR), sortie sur alerte de sortie ou au stop ; mêmes contrôles Budget et Risque |

**Argent fictif uniquement** : le courtier est un courtier papier. Rien n'est envoyé à un vrai courtier.

## Les agents

| Agent | Fichier | Rôle | Réutilise |
| --- | --- | --- | --- |
| Scanner | `scanner.py` | Calcule les indicateurs et classe les candidats par momentum | `indicators` (module 03) |
| Entrée | `entree_sortie.py` | Signal d'achat, stop, objectif | `indicators` |
| Sortie | `entree_sortie.py` | Stop suiveur, sortie Donchian, fermeture de fin de séance | `indicators` |
| Budget | `budget.py` | Taille de position à risque fixe ; poids GMV Ledoit-Wolf, parité de risque ou 1/n | `risk` (module 04), `portfolio`, `optim` (module 08) |
| Risque | `risque.py` | Refuse les entrées si risque total, corrélation ou baisse de la poche trop forts ; VaR, CVaR, volatilité | `portfolio`, `optim` |
| Courtier | `courtier.py` | Exécute à l'ouverture suivante avec frais et glissement, gère les gaps, stops et objectifs | |
| Time Machine | `time_machine.py` | Backtest d'une poche, comparaison à 1/n, intervalle de confiance du Sharpe | `metrics`, `validation` (module 07) |
| Alertes | `alertes.py` | Messages sur Telegram, même format que `node/webhook.mjs` | |
| Journal | `journal_de_bord.py` | Enregistre chaque trade clos et fait le bilan en R | `journal` (module 05) |
| Signaux | `signaux.py` | Lit les alertes TradingView reçues par `node/webhook.mjs` et traduit `XETR:SXR8` en `SXR8.DE` | |
| Données | `marche.py` | Télécharge les cours, les accumule dans un cache local et contrôle leur qualité | `data` |
| Tableau de bord | `tableau.py` | Page HTML : poches, positions, allocation comparée, backtests, trades, alertes | `portfolio`, `optim` |
| Chef d'orchestre | `orchestre.py`, `moteur.py` | Fait travailler les agents dans l'ordre, sauvegarde l'état, écrit le rapport | |

**Le backtest et le suivi quotidien utilisent le même moteur.** Le passage quotidien reprend l'état sauvegardé et avance seulement sur les barres nouvelles. Un test vérifie que le résultat est identique au backtest, et un autre qu'aucun agent ne regarde vers le futur.

Les agents Actus, Analyste (avec Claude) et Congrès sont prévus pour les étapes 3 et 4.

## Utilisation

```bash
pip install -e ".[donnees]"      # ajoute yfinance

# 1. Données : télécharge les cours de tous les univers dans donnees/marche/ (Yahoo Finance)
python -m tradeskills.agents actualiser

# 2. Backtest de toutes les poches sur ces cours réels
python -m tradeskills.agents backtest --source cache:donnees/marche

# 3. Passage quotidien, après la clôture
python -m tradeskills.agents quotidien --source cache:donnees/marche

# 4. Tableau de bord : agents/tableau.html, à ouvrir dans le navigateur
python -m tradeskills.agents tableau --source cache:donnees/marche
```

Autres sources : `--source simulee` (cours simulés, sans connexion), `--source csv:agents/donnees` (tes exports TradingView : `SAP.DE.csv`, `AAPL_intraday.csv`...) ou `--source yahoo` (téléchargement direct, sans cache).

### Les données

`actualiser` télécharge 5 ans de barres journalières et les 60 derniers jours en 5 minutes (la limite de Yahoo pour l'intraday). Chaque passage **ajoute** les barres nouvelles au cache : l'historique intraday s'allonge donc de jour en jour au-delà de 60 jours. Si un téléchargement échoue, l'ancien cache est gardé.

Le rapport `agents/rapports/donnees.md` signale ce qui fausserait un backtest : prix manquants ou nuls, clôture hors du range haut-bas, dates en double, variation de plus de 40 % en une barre (split mal ajusté ?), trou de plus de 10 jours, dernière barre vieille de plus de 5 jours.

Yahoo Finance est gratuit mais non officiel et réservé à un usage personnel : le cache `donnees/marche/` n'est pas mis dans Git.

### Ce qui est écrit

- `agents/etat/<poche>.json` : positions, ordres en attente, historique de la poche ;
- `agents/etat/journal_<poche>.csv` : le journal des trades, au format de `journal/modele_journal.csv` ;
- `agents/rapports/<date>.md` : le rapport du jour ;
- `agents/rapports/backtest.md` et `backtest.json` : la Time Machine de chaque poche ;
- `agents/tableau.html` : le tableau de bord.

Les alertes partent sur Telegram si `TELEGRAM_BOT_TOKEN` et `TELEGRAM_CHAT_ID` sont définis (voir `node/README.md` pour créer le bot).

Copie `config.exemple.json` en `config.json` pour changer les capitaux, les univers ou les règles, et passe `--config agents/config.json`. Tous les paramètres et leurs valeurs par défaut sont dans `tradeskills/agents/config.py`.

## Le tableau de bord

Une seule page HTML, sans connexion ni bibliothèque, en clair ou sombre selon ton système :

- la valeur de chaque poche et du total, la baisse depuis le plus haut ;
- la courbe de performance du suivi papier ;
- les positions ouvertes et les ordres pour la prochaine ouverture ;
- pour la poche long terme, ses poids actuels face à **GMV Ledoit-Wolf, parité de risque et 1/n**, avec la volatilité attendue et la plus grosse part du risque de chacune ;
- la Time Machine de chaque poche contre la référence 1/n, avec l'intervalle de confiance du Sharpe ;
- les derniers trades clos en R et les dernières alertes TradingView.

## Suivi automatique sur GitHub

Le workflow `.github/workflows/quotidien.yml` fait les quatre étapes chaque soir de semaine à 22 h 30 UTC, après la clôture américaine, sans que ton ordinateur soit allumé. Il enregistre états, journaux, rapports et tableau dans le dossier `suivi/` du dépôt (commit automatique), et le tableau est aussi téléchargeable dans l'onglet Actions (artefact `tableau-de-bord`).

- Pour le lancer tout de suite : onglet **Actions** → **passage quotidien** → **Run workflow**.
- Pour recevoir les alertes : ajoute `TELEGRAM_BOT_TOKEN` et `TELEGRAM_CHAT_ID` dans **Settings → Secrets and variables → Actions**.
- Il utilise `agents/config.json` s'il existe, sinon `agents/config.exemple.json`.
- Le dépôt est public : le suivi papier est donc visible de tous. Les cours Yahoo, eux, restent dans le cache d'Actions.

## La poche TradingView

1. Le serveur `node/webhook.mjs` reçoit tes alertes et ajoute chacune à `node/signaux.jsonl` (voir `node/README.md`).
2. Le message de l'alerte est du JSON : `{"type":"achat","symbole":"{{exchange}}:{{ticker}}","prix":{{close}},"stop":...,"strategie":"mon_setup"}` ; `type` vaut `achat` ou `sortie`. C'est déjà le format de `pine/systeme_tendance_indicateur.pine`.
3. Au passage suivant, la poche `tradingview` achète à l'ouverture qui suit l'alerte, si la ligne est dans son univers et que Budget et Risque l'acceptent. Sans stop dans l'alerte, le stop est à 2 ATR.
4. Une alerte peut viser une poche précise avec `"poche":"tradingview"`.

Le passage quotidien doit tourner là où arrive le fichier `signaux.jsonl` : sur ton ordinateur ou le serveur du webhook. Sur GitHub, sans ce fichier, la poche reste simplement sans trade.

**Sur des cours simulés, les poches perdent de l'argent, et c'est normal.** Ces cours n'ont aucune structure exploitable, donc une règle qui y gagnerait serait un faux positif. Pour juger une règle, il faut des données réelles, au moins 30 trades et un intervalle de confiance du Sharpe qui ne contient pas 0.

## Les univers proposés par poche

Pour un compte en Allemagne, la plupart des ETF américains (SPY, QQQ...) **ne peuvent pas être achetés** : il leur manque le document d'information (KID/PRIIPs) exigé dans l'UE. Les univers d'exemple utilisent donc des ETF UCITS cotés sur Xetra et des actions très liquides. Vérifie chaque code sur la fiche de l'émetteur (justETF, iShares) avant d'acheter.

| Poche | Univers d'exemple | Pourquoi |
| --- | --- | --- |
| swing | ETF S&P 500 (SXR8), Nasdaq 100 (SXRV), MSCI World (EUNL), DAX (EXS1), Émergents (IS3N), or (4GLD) ; actions Apple, Microsoft, Nvidia, Amazon, SAP, Siemens, Allianz | Assez de diversité pour que le scanner ait des tendances à choisir, et des titres liquides pour des spreads faibles |
| day | Apple, Microsoft, Nvidia, AMD (séance américaine) | Il faut les titres les plus liquides du marché : spreads de quelques centimes, beaucoup de volume intraday |
| long terme | MSCI World (EUNL), Émergents (IS3N), DAX (EXS1), obligations d'État zone euro (EUNH), or (4GLD) | Classes d'actifs peu corrélées : c'est là que l'estimation Ledoit-Wolf de la covariance apporte le plus |

C'est un point de départ pour apprendre, pas un conseil d'investissement. Ces listes changeront avec tes backtests.

## Avant de passer en argent réel

1. Le Time Machine sur données réelles donne au moins 30 trades et une espérance positive en R.
2. Deux à trois mois de passages quotidiens en papier donnent des résultats proches du backtest.
3. Tu commences avec une petite partie du capital et tu gardes le journal à jour.

Voir aussi [le comparatif des courtiers](courtiers.md).
