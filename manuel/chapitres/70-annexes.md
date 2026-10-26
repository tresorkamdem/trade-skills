::: {.partie pnum="Annexes"}
# Annexes {#annexes}

Le glossaire en trois langues, les formules à connaître par cœur, les modèles à remplir et les commandes utiles.
:::

# Glossaire français, allemand, anglais {#glossaire data-num="Annexe A"}

| Français | Deutsch | English | En une phrase |
| --- | --- | --- | --- |
| Action | Aktie | Share, stock | Part du capital d'une entreprise |
| Allocation d'actifs | Vermögensaufteilung | Asset allocation | Répartition du capital entre classes d'actifs |
| Analyse fondamentale | Fundamentalanalyse | Fundamental analysis | Valoriser une entreprise à partir de ses comptes |
| Analyse technique | Technische Analyse, Chartanalyse | Technical analysis | Décider à partir des prix et volumes passés |
| Bilan | Bilanz | Balance sheet | Ce que l'entreprise possède et doit |
| Carnet d'ordres | Orderbuch | Order book | Liste des ordres en attente à chaque prix |
| Compte de résultat | Gewinn- und Verlustrechnung | Income statement | Revenus, charges et bénéfice d'une période |
| Coupe-circuit | Notbremse | Kill switch, circuit breaker | Arrêt des entrées après une baisse donnée |
| Courtier | Broker, Depotbank | Broker | Intermédiaire qui exécute tes ordres |
| Covariance | Kovarianz | Covariance | Mesure de la variation conjointe de deux actifs |
| Dividende | Dividende | Dividend | Part du bénéfice versée aux actionnaires |
| Espérance | Erwartungswert | Expectancy | Gain moyen par trade, en R |
| Fonds propres | Eigenkapital | Equity | Capital appartenant aux actionnaires |
| Frais | Gebühren, Ordergebühr | Fees, commission | Coût prélevé par le courtier |
| Glissement | Slippage | Slippage | Écart entre prix attendu et prix obtenu |
| Impôt sur les gains | Abgeltungsteuer | Capital gains tax | 25 % + Soli en Allemagne |
| Levier | Hebel | Leverage | Exposition supérieure au capital |
| Liquidité | Liquidität | Liquidity | Facilité à acheter ou vendre sans bouger le prix |
| Moyenne mobile | Gleitender Durchschnitt | Moving average | Moyenne des n dernières clôtures |
| Obligation | Anleihe | Bond | Titre de dette |
| Ordre à cours limité | Limit-Order | Limit order | Exécution à ton prix ou mieux |
| Ordre au marché | Market-Order, Bestens-Order | Market order | Exécution immédiate, prix incertain |
| Ordre stop | Stop-Loss-Order | Stop order | Devient un ordre au marché au seuil |
| Perte maximale | Maximaler Drawdown | Maximum drawdown | Pire baisse depuis un plus haut |
| Plan d'épargne | Sparplan | Savings plan | Achat automatique chaque mois |
| Portefeuille | Portfolio, Depot | Portfolio | Ensemble des positions |
| Poche | Teilportfolio, Topf | Sleeve, pocket | Partie du capital avec ses propres règles |
| Rééquilibrage | Rebalancing, Umschichtung | Rebalancing | Retour aux poids cibles |
| Rendement | Rendite | Return | Gain en pourcentage |
| Risque de change | Währungsrisiko | Currency risk | Risque lié au taux de change |
| Spread | Geld-Brief-Spanne | Bid-ask spread | Écart entre achat et vente |
| Taille de position | Positionsgröße | Position size | Nombre de titres achetés |
| Tendance | Trend | Trend | Direction de fond du prix |
| Valeur d'entreprise | Unternehmenswert | Enterprise value | Capitalisation + dette nette |
| Volatilité | Volatilität | Volatility | Écart-type annualisé des rendements |

# Les formules à connaître {#formules data-num="Annexe B"}

| Notion | Formule | Module |
| --- | --- | --- |
| Spread | ask − bid | 01 |
| Coût annuel | allers-retours par an × coût d'un aller-retour | 01 |
| Perte avec levier L | L × baisse du sous-jacent | 01 |
| PER | capitalisation / résultat net | 02 |
| EV/EBIT | (capitalisation + dette − trésorerie) / EBIT | 02 |
| ROE | résultat net / fonds propres | 02 |
| DCF | Σ FCFₜ/(1+k)ᵗ + [FCF_N (1+g)/(k−g)] / (1+k)ᴺ | 02 |
| EMA | α × close + (1 − α) × EMA précédente, α = 2/(n+1) | 03 |
| True Range | max(haut − bas, abs(haut − clôture veille), abs(bas − clôture veille)) | 03 |
| RSI | 100 − 100 / (1 + moyenne des hausses / moyenne des baisses) | 03 |
| Taille de position | (capital × risque %) / (entrée − stop), arrondie à l'inférieur | 04 |
| R-multiple | (sortie − entrée) / (entrée − stop) | 04 |
| Espérance | p × G − (1 − p) × P | 04 |
| Kelly | p − (1 − p) / b, b = G / P | 04 |
| Gain pour effacer une perte x | 1 / (1 − x) − 1 | 04 |
| Trades pour prouver E | n ≥ (z × σ / E)² | 05 |
| Erreur type du Sharpe annualisé | ≈ 1 / √(années) | 07 |
| GMV | Σ⁻¹ 1 / (1ᵀ Σ⁻¹ 1) | 08 |
| Shrinkage linéaire | δ F + (1 − δ) S | 08 |
| Parité de risque | wᵢ (Σw)ᵢ égaux pour tous les i | 08 |
| Black-Litterman (équilibre) | π = δ Σ w_marché | 08 |
| Sharpe | (r − r_f) / σ | 09 |
| Information ratio | surperformance annualisée / tracking error | 09 |
| TWR | Π (1 + rₜ)^(1/années) − 1 | 09 |
| FCFA → € | montant / 655,957 | 11 |
| 4GLD | (XAU/USD ÷ EUR/USD) ÷ 31,1035 | 12 |

# Modèles à remplir {#modeles data-num="Annexe C"}

## Journal de trading

Les colonnes de `journal/modele_journal.csv`, plus trois colonnes personnelles recommandées :

| Colonne | Exemple | Remarque |
| --- | --- | --- |
| date | 2026-11-02 | Date d'entrée |
| actif | SAP.DE | Code Yahoo |
| sens | achat | |
| setup | cassure_donchian | Un nom par setup de ton plan |
| entree | 214.40 | Prix réellement obtenu |
| stop | 203.48 | Stop **initial** (sert au calcul du R) |
| sortie | 231.10 | Prix réellement obtenu |
| quantite | 12 | |
| frais | 2.60 | Tous les frais de l'aller-retour |
| note | Cassure avec volume ; résultats dans 12 jours | Contexte |
| *plan_respecte* | oui | Colonne personnelle |
| *discipline* | 9 | Sur 10, indépendante du résultat |
| *emotion* | calme | Un mot |

## Plan de risque

```
Capital de trading :                 ____ €
Risque par trade :                   ____ %
Risque total ouvert maximum :        ____ %
Positions simultanées maximum :      ____
Arrêt quotidien :                    ____ R
Arrêt hebdomadaire :                 ____ R
Baisse déclenchant une pause :       ____ %
Levier :                             aucun
Jour de la revue trimestrielle :     ____
```

## Fiche de décision du matin

```
Date :            ____        Message 📊 reçu : oui / non
Ordres prévus :   ____________________________________________
Résultats ou annonces qui les concernent (5 jours) : _______________
Décision :        suivre / réduire / ignorer       Raison : __________
Ordres et stops passés à : ____ h ____
```

# Commandes et liens utiles {#commandes data-num="Annexe D"}

## Commandes (terminal de VS Code, dans le dossier `trade-skills`)

| Commande | Effet |
| --- | --- |
| `source .venv/bin/activate` | Active l'environnement Python |
| `git pull` | Récupère la dernière version du dépôt (dont le suivi du soir) |
| `pytest` | Vérifie que tout le code fonctionne |
| `python modules/04-gestion-du-risque/solutions/solutions_04.py` | Lance les solutions d'un module |
| `python -m tradeskills.journal suivi/etat/journal_swing.csv` | Analyse le journal de la poche swing |
| `python -m tradeskills.agents actualiser --config agents/config.json` | Télécharge les cours (sur ton Mac) |
| `python -m tradeskills.agents backtest --config agents/config.json --source cache:donnees/marche --poche swing` | Time Machine d'une poche |
| `python -m tradeskills.agents backtest --source simulee` | Contrôle : sur des cours aléatoires, les poches doivent perdre |
| `python -m tradeskills.agents tableau --source cache:donnees/marche` | Tableau de bord local (`agents/tableau.html`) |
| `python manuel/construire.py` | Reconstruit ce manuel en PDF |

## Sur GitHub

| Où | Pour quoi |
| --- | --- |
| Actions → passage quotidien → Run workflow | Lancer un passage tout de suite |
| Actions → tester Telegram → Run workflow | Vérifier le bot |
| `agents/config.json` → crayon | Modifier les réglages |
| `agents/config.json` → History | Retrouver une ancienne version des réglages |
| `suivi/rapports/` | Rapports du jour, Time Machine, qualité des données |
| Settings → Secrets and variables → Actions | Jetons Telegram et SESHAT |

## Sites de référence

| Sujet | Site |
| --- | --- |
| ETF UCITS, codes, frais | justetf.com, ishares.com |
| Régulation allemande | bafin.de, ihk.de |
| Calendrier macro | TradingView (Calendrier économique) |
| Or | gold.org, xetra-gold.com |
| BRVM, BVMAC | brvm.org, amf-umoa.org, bvm-ac.com, cosumaf.org |
| Données académiques (thèse) | Bibliothèque de Kenneth French |

::: retenir
Ce manuel se reconstruit avec `python manuel/construire.py` : quand le dépôt évolue (nouvelle poche, robot Or-1, nouveaux résultats), une nouvelle édition peut être produite à partir des mêmes sources, dans le dossier `manuel/chapitres/`.
:::
