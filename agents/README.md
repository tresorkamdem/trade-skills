# Équipe d'agents de trading

Une équipe d'agents, inspirée des « 11 agents » qui veulent remplacer un Terminal Bloomberg, mais construite sur le code de ce dépôt et organisée en **poches** : chaque poche a son capital, son style et ses règles, et elle est suivie séparément.

| Poche | Style | Barres | Règles |
| --- | --- | --- | --- |
| `swing` | Swing trading | journalières | Cassure du plus haut de 20 jours au-dessus de la moyenne 200 jours, stop à 2 ATR qui remonte, sortie sous le plus bas de 10 jours (le système de `pine/systeme_tendance_strategie.pine`) |
| `day` | Day trading | 5 minutes | Cassure du range des 30 premières minutes au-dessus du VWAP, stop sous le range, objectif 2R, tout est fermé en fin de séance |
| `long_terme` | Allocation | journalières | Portefeuille de variance minimale Ledoit-Wolf sans vente à découvert (ta thèse), rééquilibré chaque mois |

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
| Chef d'orchestre | `orchestre.py`, `moteur.py` | Fait travailler les agents dans l'ordre, sauvegarde l'état, écrit le rapport | |

**Le backtest et le suivi quotidien utilisent le même moteur.** Le passage quotidien reprend l'état sauvegardé et avance seulement sur les barres nouvelles. Un test vérifie que le résultat est identique au backtest, et un autre qu'aucun agent ne regarde vers le futur.

Les agents Actus, Analyste (avec Claude) et Congrès sont prévus pour les étapes 3 et 4.

## Utilisation

```bash
# Backtest de toutes les poches sur des cours simulés (aucune connexion nécessaire)
python -m tradeskills.agents backtest --source simulee

# Une seule poche, sur tes exports TradingView (agents/donnees/SAP.DE.csv, AAPL_intraday.csv...)
python -m tradeskills.agents backtest --poche swing --source csv:agents/donnees

# Passage quotidien sur Yahoo Finance (pip install yfinance), après la clôture
python -m tradeskills.agents quotidien --source yahoo
```

Le passage quotidien écrit :
- `agents/etat/<poche>.json` : positions, ordres en attente, historique de la poche ;
- `agents/etat/journal_<poche>.csv` : le journal des trades, au format de `journal/modele_journal.csv` ;
- `agents/rapports/<date>.md` : le rapport du jour.

Les alertes partent sur Telegram si `TELEGRAM_BOT_TOKEN` et `TELEGRAM_CHAT_ID` sont définis (voir `node/README.md` pour créer le bot).

Copie `config.exemple.json` pour changer les capitaux, les univers ou les règles. Tous les paramètres et leurs valeurs par défaut sont dans `tradeskills/agents/config.py`.

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
