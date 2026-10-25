# Module 05 · Day trading et swing trading

**Objectif** : savoir comment travaillent les traders de court terme, choisir le style qui te correspond, et construire une routine et un journal qui produisent un track record.

**Durée** : 4 semaines de paper trading au minimum · **Prérequis** : modules 01, 03 et 04

## 1. Choisir son horizon

| Style | Durée d'un trade | Temps d'écran | Coûts relatifs | Compatible avec études ou emploi |
| --- | --- | --- | --- | --- |
| Scalping | Secondes à minutes | Toute la séance | Très élevés | Non |
| Day trading | Minutes à heures, clôturé le soir | Plusieurs heures par jour | Élevés | Difficile |
| Swing trading | 2 jours à quelques semaines | 30 à 60 min par jour | Modérés | Oui |
| Position / portefeuille | Mois à années | Quelques heures par semaine | Faibles | Oui |

**Réalité du day trading** : les études sur les comptes de particuliers (par exemple Barber, Lee, Liu et Odean sur Taïwan, ou les avertissements obligatoires des brokers de CFD en Europe, qui annoncent le plus souvent entre 70 et 85 % de comptes perdants) montrent qu'une très petite minorité gagne de façon durable. Ton profil (mathématiques, gestion de portefeuille, MAÀT) est bien plus adapté au **swing trading systématique** et à la **gestion de portefeuille**. Apprends le day trading pour comprendre la microstructure, pas comme source de revenus au départ.

## 2. Les setups de swing trading

| Setup | Contexte | Entrée | Stop | Sortie |
| --- | --- | --- | --- | --- |
| Rebond sur moyenne mobile | Tendance haussière (prix > MM200) | Bougie de retournement sur la MM20 ou MM50 | Sous le plus bas du rebond ou 1,5 ATR | Plus haut précédent ou trailing stop |
| Cassure de range | Compression de volatilité (Bollinger serrées) | Clôture au-dessus du range avec volume | Milieu ou bas du range | 2 à 3R ou trailing stop |
| Cassure Donchian | Tendance | Plus haut de 20 jours | 2 ATR | Plus bas de 10 jours |
| Retour à la moyenne | Range, pas de tendance | RSI(2) < 10 au-dessus de la MM200 | 2 ATR ou durée maximale | Clôture au-dessus de la MM5 |

## 3. Les setups de day trading

- **Opening range breakout** : on note le plus haut et le plus bas des 15 ou 30 premières minutes, on entre sur la cassure, stop de l'autre côté du range.
- **VWAP** : en tendance haussière intraday, on achète les retours sur le VWAP ; un franchissement du VWAP à la baisse invalide l'idée.
- **Gap** : un gap d'ouverture sur nouvelle (résultats) qui tient au-dessus du VWAP après 30 minutes est souvent continué.
- **Horaires** : l'ouverture (9 h 00 à 10 h 30 à Francfort, 15 h 30 à 17 h 00 heure de Berlin pour Wall Street) concentre la volatilité. Le milieu de journée est souvent sans direction.

## 4. La routine

**Avant la séance (15 à 30 minutes)**

1. Calendrier macro et publications du jour (module 02).
2. Tendance des indices et des taux.
3. Liste de surveillance de 5 à 10 titres avec niveaux clés notés à l'avance.
4. Rappel du plan de risque : risque par trade, arrêt quotidien.

**Pendant la séance**

- Ne prendre que les setups écrits dans ton plan. Pas de setup = pas de trade.
- Ordre stop placé au moment de l'entrée, jamais déplacé contre toi.

**Après la séance (10 minutes)**

- Journal rempli pour chaque trade : setup, captures d'écran, émotion, respect du plan.
- Note de discipline sur 10, indépendante du résultat.

## 5. La psychologie

Les erreurs les plus fréquentes, et leur parade :

| Biais | Symptôme | Parade |
| --- | --- | --- |
| Aversion aux pertes | Déplacer le stop, garder un perdant | Ordre stop au broker dès l'entrée |
| Prise de gains trop rapide | Couper un gagnant à +0,5R | Sortie définie à l'avance, ou partielle |
| Revenge trading | Enchaîner les trades après une perte | Arrêt quotidien à −2R, obligatoire |
| Excès de confiance | Augmenter la taille après une série gagnante | Taille fixe en % du capital |
| FOMO | Entrer en retard sur un mouvement déjà fait | Entrer seulement sur des niveaux notés avant la séance |

Juge un trade sur le **respect du processus**, pas sur son résultat. Un trade discipliné perdant est un bon trade ; un trade indiscipliné gagnant est un mauvais trade.

## 6. Le journal, base du track record

Chaque ligne de `journal/modele_journal.csv` doit être remplie. Toutes les 20 à 30 transactions :

```bash
python -m tradeskills.journal journal/mon_journal.csv
```

Regarde l'espérance en R, et surtout le **résultat par setup** : supprime les setups à espérance négative, augmente la part des meilleurs.

## 7. Du paper trading au réel

1. **Paper trading** : au moins 50 trades avec le plan, journal complet.
2. **Petit compte réel** : seulement si l'espérance est positive et la discipline au-dessus de 8/10. Risque 0,5 % par trade.
3. **Montée en taille** : par paliers, après chaque série de 50 trades à espérance positive.

## À retenir

1. Choisis un style compatible avec ta vie : pour toi, swing et portefeuille.
2. Pas de setup écrit, pas de trade.
3. La routine et le journal comptent plus que l'indicateur.
4. Juge le processus, pas le résultat d'un trade.
