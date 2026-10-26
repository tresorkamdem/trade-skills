::: {.partie pnum="Partie II"}
# Tes agents {#partie2}

Comment fonctionne ton équipe d'agents : qui fait quoi, dans quel ordre, avec quelles règles, et comment lire ce qu'ils te disent chaque soir. Tout est tiré du code de `tradeskills/agents/`.
:::

# L'équipe et son chef d'orchestre {#equipe data-num="Partie II"}

## 1. L'idée

Une équipe d'agents, inspirée des « 11 agents » qui veulent remplacer un terminal Bloomberg, mais construite sur le code de ton dépôt et organisée en **poches**. Chaque poche a son capital, son style et ses règles, et elle est suivie séparément, comme les compartiments d'un fonds.

Un « agent » ici n'est pas une intelligence artificielle : c'est un module Python qui a **un seul rôle**, des règles écrites, et qui ne peut pas improviser. C'est voulu : un agent qui suit ses règles n'a aucun des biais du module 05.

| Agent | Fichier | Rôle | Réutilise le module |
| --- | --- | --- | --- |
| Données | `marche.py` | Télécharge les cours, les accumule dans un cache, contrôle leur qualité | |
| Scanner | `scanner.py` | Calcule les indicateurs et classe les candidats par momentum | 03 |
| Entrée | `entree_sortie.py` | Signal d'achat, stop, objectif | 03 |
| Sortie | `entree_sortie.py` | Stop suiveur, sortie Donchian, fermeture de fin de séance | 03 |
| Budget | `budget.py` | Taille à risque fixe ; poids GMV Ledoit-Wolf, parité de risque ou 1/n | 04, 08 |
| Risque | `risque.py` | Refuse les entrées si risque total, corrélation ou baisse trop forts ; VaR, CVaR | 04, 08 |
| Courtier papier | `courtier.py` | Exécute à l'ouverture suivante avec frais et glissement, gère gaps, stops et objectifs | 01 |
| Signaux | `signaux.py` | Traduit les alertes TradingView en propositions | 06 |
| Time Machine | `time_machine.py` | Backtest d'une poche, comparaison à 1/n, IC du Sharpe | 07 |
| Journal | `journal_de_bord.py` | Enregistre chaque trade clos et fait le bilan en R | 05 |
| Alertes | `alertes.py` | Messages Telegram | 06 |
| Tableau de bord, instantané | `tableau.py`, `instantane.py` | Page HTML et envoi vers SESHAT | 09 |
| Chef d'orchestre | `orchestre.py`, `moteur.py` | Fait travailler les agents dans l'ordre, sauvegarde l'état, écrit le rapport | |

## 2. Le passage d'une barre

Le **moteur** fait avancer une poche barre par barre (un jour pour swing, long terme et TradingView ; 5 minutes pour day). À chaque barre t, l'ordre est toujours le même :

<div class="flux">
<div class="b o">1 · Courtier<small>exécute à l'ouverture de t les ordres décidés en t−1, puis vérifie stops et objectifs</small></div><div class="f">→</div>
<div class="b">2 · Sortie<small>remonte les stops suiveurs, décide les sorties</small></div><div class="f">→</div>
<div class="b">3 · Scanner<small>filtre et classe les candidats</small></div>
</div>
<div class="flux">
<div class="b">4 · Entrée<small>signal, stop, objectif</small></div><div class="f">→</div>
<div class="b v">5 · Budget<small>quantité</small></div><div class="f">→</div>
<div class="b r">6 · Risque<small>accepte ou refuse</small></div><div class="f">→</div>
<div class="b o">7 · Courtier<small>ordre pour l'ouverture de t+1</small></div>
</div>

Deux variantes : la poche **long terme** remplace les étapes 2 à 6 par un **rééquilibrage** le premier jour de bourse de chaque mois ; la poche **TradingView** remplace Scanner et Entrée par les **alertes reçues** depuis la barre précédente.

::: cle
**Une décision prise à la clôture de t n'est exécutée qu'à l'ouverture de t+1.** C'est la règle qui interdit tout regard vers le futur (module 07). Un test automatique vérifie qu'aucun agent n'utilise une information postérieure à la barre où il décide.
:::

## 3. Le même moteur pour le backtest et pour le papier

C'est la propriété la plus importante de ton système :

- la **Time Machine** fait tourner le moteur sur tout l'historique (5 ans de cours journaliers, 60 jours et plus en 5 minutes) ;
- le **passage du soir** reprend l'état sauvegardé de chaque poche et fait tourner **le même moteur** sur les seules barres nouvelles.

Un test vérifie que les deux donnent exactement le même résultat. Ce qui marche en backtest est donc exactement ce qui tourne en papier ; si les résultats papier s'écartent du backtest, ce n'est pas le code, c'est le marché.

::: attention
Au tout premier passage (le 26 octobre 2026), l'état n'existait pas : le moteur a donc rejoué tout l'historique pour s'initialiser. C'est pourquoi la poche swing affiche déjà 13 164 € et 227 trades. **Ces chiffres sont ceux du backtest, pas des gains réalisés en papier depuis octobre.** Le vrai suivi papier commence à la date du premier passage ; la partie IV explique comment le lire séparément.
:::

# Chaque agent, en détail {#agents-detail data-num="Partie II"}

## Données (`marche.py`)

- **Source** : Yahoo Finance via `yfinance` (gratuit, non officiel, usage personnel).
- `actualiser` télécharge **5 ans de barres journalières** et les **60 derniers jours en 5 minutes** (la limite de Yahoo pour l'intraday). Chaque passage **ajoute** les barres nouvelles au cache : l'historique intraday s'allonge de jour en jour.
- Si un téléchargement échoue, l'ancien cache est gardé.
- **Contrôle qualité** (rapport `donnees.md`) : prix manquants ou nuls, clôture hors du range haut-bas, dates en double, variation de plus de 40 % en une barre (split mal ajusté ?), trou de plus de 10 jours, dernière barre vieille de plus de 5 jours.
- **Autres sources** : `simulee` (sans connexion, pour tester), `csv:<dossier>` (tes exports, par exemple des cours de la BRVM), `cache:<dossier>` (le cache rempli par `actualiser`).

Le cache n'est pas publié dans le dépôt (public) : il reste dans le cache de GitHub Actions.

## Scanner (`scanner.py`)

Il calcule une seule fois, sur tout l'historique, les colonnes dont les autres agents ont besoin, puis filtre et classe les candidats à chaque barre :

| Style | Colonnes calculées | Filtre | Classement |
| --- | --- | --- | --- |
| swing | ATR, MM de tendance, plus haut d'entrée, plus bas de sortie, momentum 126 jours, volume moyen 20 jours | clôture > MM200 ; volume moyen ≥ `volume_min` | momentum décroissant |
| day | range d'ouverture (haut et bas des n premières barres), VWAP, ATR, rang de la barre, heure, momentum depuis l'ouverture | clôture > VWAP | momentum du jour |
| signaux | ATR | | |

Les indicateurs ne regardent que le passé : la ligne de la date t est exactement celle qu'on aurait obtenue en direct à la clôture de t.

## Entrée et Sortie (`entree_sortie.py`)

**Swing** : entrée si clôture > plus haut des 20 jours précédents **et** > MM200 ; stop = clôture − 2 ATR. Chaque jour, le stop remonte à clôture − 2 ATR s'il est plus haut que l'ancien (il ne descend jamais) ; sortie si la clôture passe sous le plus bas des 10 jours précédents.

**Day** : après les 6 premières barres de 5 minutes (30 minutes), entrée si la clôture dépasse le haut du range **et** le VWAP, avant 15 h 00 (heure de New York) ; stop au bas du range ; objectif à 2R ; tout est fermé à 15 h 50 (heure de New York, soit 21 h 50 à Berlin). Un seul trade par symbole et par séance.

## Budget (`budget.py`)

**Poches à signaux (swing, day, TradingView)** : pour chaque proposition, dans l'ordre du scanner :

> quantité = min( risque à risque fixe, poids_max × valeur / prix, cash / (prix × 1,01) )

et s'arrête quand `max_positions` est atteint.

**Poche long terme** : poids cibles sur les rendements des `fenetre` derniers jours : `gmv_lw` (GMV long-only Ledoit-Wolf), `parite_risque` ou `egal` (1/n), chaque poids plafonné à `poids_max` (relevé à 1/n s'il est trop bas pour que la somme fasse 100 %), l'excédent étant redistribué aux autres lignes.

## Risque (`risque.py`)

Avant chaque entrée, il refuse la ligne si :

1. la poche a perdu plus de `drawdown_max` depuis son plus haut (**coupe-circuit**) : aucune entrée pendant `pause_jours` jours, puis on repart du niveau atteint ;
2. le risque ouvert total dépasserait `risque_total_max` ;
3. la ligne a une corrélation de plus de `correlation_max` (sur 60 jours) avec une position déjà tenue.

Il calcule aussi, pour le rapport : exposition, risque ouvert, volatilité annuelle (covariance Ledoit-Wolf), **VaR et CVaR historiques à 1 jour et 95 %**.

## Courtier papier (`courtier.py`)

| Situation | Ce que fait le courtier |
| --- | --- |
| Ordre décidé à la clôture | Exécuté à l'**ouverture suivante**, avec `glissement_bps` défavorable et `cout_bps` de frais |
| Ouverture sous le stop d'un achat (gap défavorable) | Ordre **annulé** (« annule_gap ») |
| Ouverture plus haute que prévu | Quantité **réduite** pour ne pas dépasser le risque prévu |
| Stop touché pendant la barre | Sortie au stop, ou à l'ouverture si elle a sauté le stop |
| Stop et objectif touchés dans la même barre | On suppose le **pire** : le stop |
| Cash insuffisant | Quantité réduite, ou ordre annulé (« annule_cash ») |

Achats uniquement : pas de vente à découvert. Un courtier réel (IBKR) pourra un jour remplacer cette classe en gardant les mêmes méthodes.

## Signaux (`signaux.py`)

Il lit `node/signaux.jsonl` (une alerte TradingView par ligne), traduit le code TradingView en code Yahoo (`XETR:SXR8` → `SXR8.DE`, `NASDAQ:AAPL` → `AAPL`) et donne, pour chaque jour, les alertes reçues depuis la veille. Une alerte « achat » sans stop, ou avec un stop au-dessus du prix, reçoit un stop à 2 ATR. Une alerte « sortie » vend la position à l'ouverture suivante. Les mêmes Budget et Risque s'appliquent.

## Time Machine (`time_machine.py`)

Elle rejoue chaque poche sur tout l'historique et compare à une **référence 1/n achat-conservation** de son univers : rendement, volatilité, Sharpe, Sortino, perte maximale, Calmar ; **intervalle de confiance du Sharpe** par bootstrap par blocs ; bilan des trades en R par setup ; avertissement si l'espérance est négative.

## Journal, Alertes, Tableau de bord

- **Journal** : chaque trade clos va dans `suivi/etat/journal_<poche>.csv`, au format de `journal/modele_journal.csv`.
- **Alertes** : un message Telegram par passage, avec une ligne par poche, les exécutions de la dernière séance (🟢 achat, 🔴 vente, ⚪ ordre annulé) et les ordres prévus pour le lendemain.
- **Tableau de bord** : `suivi/tableau.html` et la section Trading de SESHAT (partie IV).

# Les quatre poches aujourd'hui {#poches-aujourdhui data-num="Partie II"}

| Poche | Style | Capital | Univers | Règles clés |
| --- | --- | --- | --- | --- |
| **swing** | swing | 10 000 € | SXR8, SXRV, EUNL, EXS1, IS3N, 4GLD, Apple, Microsoft, Nvidia, Amazon, SAP, Siemens, Allianz | Donchian 20/10, MM200, stop 2 ATR, risque 1 %, 5 positions, 25 % max par ligne |
| **day** | day | 5 000 € | Apple, Microsoft, Nvidia, AMD | Range 30 min + VWAP, objectif 2R, risque 0,5 %, 2 positions, coupe-circuit à −5 % |
| **long_terme** | long_terme | 20 000 € | EUNL, IS3N, EXS1, EUNH, 4GLD | GMV Ledoit-Wolf sur 252 jours, 40 % max par ligne, 10 pb de frais, mensuel |
| **tradingview** | signaux | 5 000 € | SXR8, SXRV, EUNL, EXS1, Apple, Microsoft, Nvidia, SAP | Tes alertes ; stop de l'alerte ou 2 ATR ; risque 1 % ; 4 positions |

![Courbes des trois poches actives depuis octobre 2021 (backtest d'initialisation, données réelles, argent fictif). Les courbes sont plates la première année : c'est le temps de chauffe des indicateurs (moyenne 200 jours, fenêtre de 252 jours).](fig/courbes_poches.svg)

## Ce que dit la Time Machine du 26 octobre 2026

| Poche | Rendement annuel | Volatilité | Sharpe [IC 95 %] | Perte max. | Trades | Espérance |
| --- | --- | --- | --- | --- | --- | --- |
| swing | 5,5 % | 7,7 % | 0,73 [−0,17 ; 1,61] | −10,9 % | 227 | +0,24R |
| *1/n de l'univers swing* | *18,8 %* | *15,8 %* | *1,17* | *−24,3 %* | | |
| day (3 mois) | −18,9 % | 3,7 % | −5,69 | −5,7 % | 77 | −0,14R |
| long terme | 7,1 % | 5,6 % | 1,24 [0,41 ; 2,15] | −7,5 % | 163 ordres | |
| *1/n de l'univers long terme* | *9,1 %* | *9,8 %* | *0,94* | *−14,4 %* | | |
| tradingview | 0 | 0 | | 0 | 0 | |

**Lecture en une phrase par poche** :

- **swing** : espérance positive, risque faible, mais rendement très inférieur à la référence ; non significatif. À améliorer, pas à abandonner.
- **day** : espérance négative sur 77 trades, coupe-circuit déclenché. En l'état, à ne jamais passer en réel.
- **long terme** : meilleur Sharpe que 1/n, mais ces chiffres sont faussés depuis novembre 2025 par une anomalie de données, corrigée depuis (partie III) : reprends les chiffres corrigés dans `suivi/rapports/backtest.md`.
- **tradingview** : vide, normal tant que le pont des alertes n'est pas branché.

::: robot
Le message du 26 octobre montrait aussi l'agent Risque au travail : SXRV refusé pour une corrélation de 0,95 avec une position tenue, EXS1 à 0,82, SXR8 à 0,86, AMZN à 0,83. Sans ces refus, la poche swing aurait pris cinq fois le même pari « actions américaines et technologie ».
:::
