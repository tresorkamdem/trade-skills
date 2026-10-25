# Module 02 · Analyse fondamentale

**Objectif** : comprendre ce que vaut une entreprise, lire ses comptes, suivre le contexte macroéconomique, et savoir quand l'information fondamentale compte pour un trader.

**Durée** : 3 semaines · **Prérequis** : module 01

## 1. Pourquoi un trader s'y intéresse

- **Gestion de portefeuille** (ton objectif principal) : l'horizon est de plusieurs mois ou années, la valeur fondamentale finit par compter.
- **Swing trading** : les publications de résultats, les décisions des banques centrales et les chiffres macro provoquent les plus gros mouvements. Il faut savoir quand ils tombent.
- **Day trading** : on ne valorise pas, mais on évite de trader à l'aveugle au moment d'une annonce.

## 2. Les trois états financiers

| État | Question | Lignes clés |
| --- | --- | --- |
| Compte de résultat | L'entreprise gagne-t-elle de l'argent ? | Chiffre d'affaires, EBIT (résultat opérationnel), résultat net |
| Bilan | Que possède-t-elle et que doit-elle ? | Actifs, dettes, fonds propres, trésorerie |
| Tableau des flux de trésorerie | Le bénéfice se transforme-t-il en cash ? | Flux opérationnel, investissements (capex), flux disponible (FCF) |

Un bénéfice élevé avec un flux de trésorerie faible est un signal d'alerte.

## 3. Les ratios essentiels

| Ratio | Formule | Lecture |
| --- | --- | --- |
| PER | Capitalisation / résultat net | Combien d'années de bénéfices paie-t-on ? À comparer au secteur |
| EV/EBIT | (Capitalisation + dette − trésorerie) / EBIT | Comme le PER, mais neutre vis-à-vis de l'endettement |
| Price-to-book | Capitalisation / fonds propres | Utile pour les banques et assurances |
| Marge opérationnelle | EBIT / chiffre d'affaires | Pouvoir de prix, efficacité |
| ROE | Résultat net / fonds propres | Rentabilité pour l'actionnaire (à lire avec l'endettement) |
| Dette nette / fonds propres | (Dette − trésorerie) / fonds propres | Solidité financière |
| Rendement du dividende | Dividendes / capitalisation | Revenu ; attention aux dividendes non couverts par le FCF |

Un ratio seul ne dit rien. On le compare **dans le temps** (l'entreprise s'améliore-t-elle ?) et **aux concurrents**.

## 4. Valoriser : le DCF

La valeur d'une entreprise est la somme actualisée de ses flux de trésorerie futurs :

> V = Σ FCFₜ / (1 + k)ᵗ + valeur terminale / (1 + k)ᴺ, avec valeur terminale = FCF_N × (1 + g) / (k − g)

- k : coût du capital (souvent 8 à 10 % pour une action de pays développé, plus pour un marché émergent comme la zone CEMAC).
- g : croissance perpétuelle, jamais au-dessus de la croissance nominale de l'économie (2 à 3 %).

Le DCF est **très sensible** à k et g : fais toujours une table de sensibilité. C'est le même problème que dans ta thèse avec le vecteur des rendements espérés : de petites erreurs d'estimation donnent de gros écarts de résultat.

```python
from tradeskills.fundamentals import dcf
dcf(fcf=500, growth=0.08, years=5, discount=0.09, terminal_growth=0.02, net_debt=1_000, shares=100)
```

## 5. Les facteurs

La recherche (Fama et French, la même bibliothèque de données que ta thèse) a identifié des caractéristiques associées aux rendements sur le long terme : **marché**, **taille**, **value** (ratios bas), **rentabilité**, **investissement**, et **momentum**. Une grande partie de la gestion quantitative de portefeuille consiste à s'exposer à ces facteurs de façon contrôlée. Tu les retrouveras au module 08.

## 6. La macroéconomie

| Indicateur | Effet typique |
| --- | --- |
| Taux directeurs (BCE, Fed, BEAC pour la zone CEMAC) | Hausse = pression sur les actions de croissance et les obligations, soutien de la devise |
| Inflation (CPI, HICP) | Surprise à la hausse = anticipation de hausses de taux |
| Emploi (NFP aux États-Unis, 1er vendredi du mois) | Grosse volatilité sur l'USD et les indices |
| PMI | Indicateur avancé de l'activité |
| PIB | Confirme plutôt qu'il n'annonce |

Ce qui fait bouger le prix, c'est **l'écart avec le consensus**, pas le chiffre lui-même. Utilise un calendrier économique (Investing.com, Forex Factory, TradingView) chaque lundi.

## 7. Routine fondamentale du trader

- Chaque lundi : calendrier macro de la semaine et dates de publication de résultats des titres suivis.
- Avant un swing trade sur une action : pas de publication de résultats pendant la durée prévue, ou position réduite.
- Chaque trimestre, pour le portefeuille long terme : mise à jour des ratios et de la thèse d'investissement de chaque ligne.

## À retenir

1. Le cash compte plus que le bénéfice comptable.
2. Un ratio se compare au passé et aux concurrents.
3. Un DCF sans table de sensibilité est une illusion de précision.
4. Les marchés réagissent aux surprises, pas aux chiffres.
