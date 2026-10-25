# Trade Skills

Parcours d'apprentissage complet de l'analyse financière appliquée au trading et à la gestion de portefeuille, relié à ma Bachelorarbeit en Wirtschaftsmathematik (HTW Berlin) et à mon activité MAÀT Analytics.

## Feuille de route

Coche un module quand tu as fait tous ses exercices.

| | Module | Durée | Outils | Lien avec tes projets |
| --- | --- | --- | --- | --- |
| [ ] | [01 · Bases des marchés](modules/01-bases-des-marches/lecon.md) | 1 à 2 sem. | | Coût du turnover de la thèse |
| [ ] | [02 · Analyse fondamentale](modules/02-analyse-fondamentale/lecon.md) | 3 sem. | `fundamentals` | Paquet A6 de MAÀT |
| [ ] | [03 · Analyse technique](modules/03-analyse-technique/lecon.md) | 3 sem. | `indicators`, `signals` | Tests statistiques |
| [ ] | [04 · Gestion du risque](modules/04-gestion-du-risque/lecon.md) | 2 sem. | `risk` | Prolonge la thèse au niveau du trade |
| [ ] | [05 · Day et swing trading](modules/05-day-et-swing-trading/lecon.md) | 4 sem. | `journal` | Source du track record |
| [ ] | [06 · TradingView et Pine Script](modules/06-tradingview-pine-script/lecon.md) | 3 sem. | `pine/`, `node/` | Alertes Telegram (comme SESHAT) |
| [ ] | [07 · Backtesting rigoureux](modules/07-backtesting-rigoureux/lecon.md) | 3 sem. | `validation` | Test de Sharpe du « Ausblick » |
| [ ] | [08 · Optimisation de portefeuille avancée](modules/08-optimisation-de-portefeuille/lecon.md) | 4 sem. | `optim` | Shrinkage non linéaire ; offre C1 v2 |
| [ ] | [09 · Performance et reporting](modules/09-performance-et-reporting/lecon.md) | 2 sem. | `report` | Paquet « reporting » de MAÀT |
| [ ] | [10 · Parcours pro](modules/10-parcours-pro/lecon.md) | 12 à 24 mois | | Plan de développement de MAÀT |

Ordre conseillé : 01 → 04 → 03 → 02 → 05 → 06 → 07 → 08 → 09, et le 10 en parallèle dès le début. Chaque module a une leçon, des exercices et des solutions exécutables.

## Structure

```
modules/        une leçon, des exercices et des solutions par module
tradeskills/    package Python réutilisable
  data.py         Kenneth French, CSV OHLCV (export TradingView), cours simulés
  metrics.py      rendement, volatilité, Sharpe, Sortino, drawdown, Calmar, turnover
  indicators.py   SMA, EMA, RSI, MACD, ATR, Bollinger, Donchian, VWAP
  signals.py      backtest d'une stratégie à signal sur un actif
  risk.py         taille de position, R-multiple, Kelly, espérance, Monte-Carlo
  journal.py      statistiques du journal de trading
  fundamentals.py ratios financiers, DCF
  portfolio.py    GMV, estimateurs empirique / Ledoit-Wolf / OAS, backtest glissant avec coûts
  validation.py   walk-forward, bootstrap, test de Sharpe, Deflated Sharpe
  optim.py        shrinkage non linéaire, long-only, tangent, parité de risque, Black-Litterman, CVaR
  report.py       alpha, bêta, information ratio, Brinson, rapport client
  agents/         équipe d'agents de trading par poches (voir agents/README.md)
agents/         configuration, documentation et comparatif des courtiers pour les agents
journal/        modèle de journal de trading
pine/           scripts TradingView (indicateur, stratégie, RSI)
node/           serveur d'alertes TradingView vers Telegram
data/           10, 30 et 48 portefeuilles sectoriels de Kenneth French
tests/          tests automatiques (Python et Node.js)
```

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -e ".[dev]"
pytest                           # vérifie que tout fonctionne
cd node && npm test              # outils Node.js
```

## Exemple : la thèse, avec des coûts de transaction

```python
from tradeskills import data, portfolio

R = data.load_french_csv("data/10_Industry_Portfolios.csv", start=196901)
print(portfolio.compare(R, window=60, cost_bps=20))
```

## Équipe d'agents

`tradeskills.agents` fait travailler une équipe d'agents (Scanner, Entrée, Sortie, Budget, Risque, Courtier papier, Time Machine, Alertes, Journal) sur plusieurs poches séparées : swing, day trading et long terme. Le backtest et le suivi quotidien utilisent le même moteur.

```bash
python -m tradeskills.agents backtest --source simulee
```

Détails dans [agents/README.md](agents/README.md), et [quel courtier ouvrir](agents/courtiers.md).

## Données

Aucune donnée de marché en temps réel n'est incluse. Les exercices utilisent les données de Kenneth French (fournies), des cours simulés (`data.synthetic_ohlcv`) et tes propres exports TradingView (`data.load_ohlcv_csv`).

## Liens

- Bachelorarbeit et paquet de réplication : [Portfolio-Optimization-Thesis](https://github.com/tresorkamdem/Portfolio-Optimization-Thesis)
- Les outils qui ont fait leurs preuves ici passent ensuite dans le toolkit de MAÀT Analytics (offre C1).

## Avertissement

Contenu éducatif, pas un conseil en investissement. Le trading comporte un risque de perte en capital.
