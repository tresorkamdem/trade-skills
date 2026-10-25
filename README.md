# Trade Skills

Parcours d'apprentissage complet de l'analyse financière appliquée au trading et à la gestion de portefeuille, relié à ma Bachelorarbeit en Wirtschaftsmathematik (HTW Berlin) et à mon activité MAÀT Analytics.

## Feuille de route

- [x] Moteur Python : données, métriques, backtest glissant avec coûts, gestion du risque
- [x] Journal de trading et statistiques
- [ ] [01 · Bases des marchés](modules/01-bases-des-marches/lecon.md) (leçon et exercices prêts)
- [ ] [02 · Analyse fondamentale](modules/02-analyse-fondamentale/)
- [ ] [03 · Analyse technique](modules/03-analyse-technique/)
- [ ] [04 · Gestion du risque](modules/04-gestion-du-risque/)
- [ ] [05 · Day trading et swing trading](modules/05-day-et-swing-trading/)
- [ ] [06 · TradingView et Pine Script](modules/06-tradingview-pine-script/)
- [ ] [07 · Backtesting rigoureux](modules/07-backtesting-rigoureux/)
- [ ] [08 · Optimisation de portefeuille avancée](modules/08-optimisation-de-portefeuille/)
- [ ] [09 · Performance et reporting](modules/09-performance-et-reporting/)
- [ ] [10 · Parcours pro](modules/10-parcours-pro/)

Coche un module quand tu as fait tous ses exercices.

## Structure

```
modules/      une leçon, des exercices et des solutions par module
tradeskills/  package Python réutilisable
  data.py       chargement Kenneth French et CSV OHLCV (export TradingView)
  metrics.py    rendement, volatilité, Sharpe, Sortino, drawdown, Calmar, turnover
  portfolio.py  portefeuille GMV, estimateurs empirique / Ledoit-Wolf / OAS, backtest glissant avec coûts
  risk.py       taille de position, R-multiple, Kelly, espérance
  journal.py    statistiques du journal de trading
journal/      modèle de journal de trading
pine/         scripts TradingView
node/         outils Node.js (alertes, données)
data/         données d'exemple (10 portefeuilles sectoriels de Kenneth French)
tests/        tests automatiques
```

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -e ".[dev]"
pytest                           # vérifie que tout fonctionne
```

## Exemple : la thèse, avec des coûts de transaction

```python
from tradeskills import data, portfolio

R = data.load_french_csv("data/10_Industry_Portfolios.csv", start=196901)
print(portfolio.compare(R, window=60, cost_bps=20))
```

## Liens

- Bachelorarbeit et paquet de réplication : [Portfolio-Optimization-Thesis](https://github.com/tresorkamdem/Portfolio-Optimization-Thesis)
- Les outils qui ont fait leurs preuves ici passent ensuite dans le toolkit de MAÀT Analytics (offre C1).

## Avertissement

Contenu éducatif, pas un conseil en investissement. Le trading comporte un risque de perte en capital.
