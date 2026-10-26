::: {.partie pnum="Partie III"}
# Tes robots et leur calibrage {#partie3}

Tes « robots », ce sont tes poches : chacune applique ses règles toute seule, chaque soir. Cette partie liste tous leurs réglages, montre où les changer depuis ton Mac, comment tester un changement en papier avant de l'adopter, et ce qui est prévu pour le robot or.
:::

# Le fichier de réglages {#reglages data-num="Partie III"}

## 1. Où sont les réglages

Tous les réglages de toutes les poches tiennent dans **un seul fichier JSON** :

| Fichier | Rôle |
| --- | --- |
| `agents/config.exemple.json` | Les réglages actuels, fournis avec le dépôt. **Ne le modifie pas** : c'est ta référence |
| `agents/config.json` | **Tes** réglages. Il n'existe pas encore. Dès qu'il existe, le passage du soir l'utilise à la place de l'exemple |
| `tradeskills/agents/config.py` | Les valeurs par défaut de chaque réglage (quand le JSON ne le précise pas) et la vérification des noms |

Le workflow choisit tout seul : `agents/config.json` s'il existe, sinon `agents/config.exemple.json`. Pour revenir aux réglages d'origine, il suffit donc de supprimer `agents/config.json`.

## 2. La structure du fichier

```json
{
  "poches": [
    {
      "nom": "swing",
      "style": "swing",
      "capital": 10000,
      "univers": ["SXR8.DE", "EUNL.DE", "AAPL", "SAP.DE"],
      "risque_par_trade": 0.01,
      "max_positions": 5,
      "poids_max": 0.25,
      "params": {"entree": 20, "sortie": 10}
    }
  ]
}
```

Chaque poche a des **réglages communs** (au premier niveau) et des **paramètres de style** (dans `params`). Un réglage absent prend sa valeur par défaut.

::: attention
**Les quatre erreurs de JSON les plus fréquentes** : (1) une virgule oubliée entre deux lignes, ou une virgule en trop après le dernier élément ; (2) une virgule décimale au lieu d'un point (`0,01` au lieu de `0.01`) ; (3) des guillemets typographiques « ” » au lieu de guillemets droits `"` (le Mac les remplace parfois dans Notes ou Pages : écris le JSON dans VS Code ou directement sur GitHub) ; (4) un pourcentage écrit `1` au lieu de `0.01`. Un nom de paramètre inconnu (faute de frappe) arrête le passage avec le message « Paramètres inconnus pour swing : [...] » : c'est voulu, pour qu'aucune faute ne passe inaperçue.
:::

# Tous les réglages {#tous-reglages data-num="Partie III"}

## 3. Réglages communs à toutes les poches

| Réglage | Défaut | Ce qu'il fait | Plage raisonnable | Si tu exagères |
| --- | --- | --- | --- | --- |
| `nom` | | Nom de la poche ; nomme aussi son fichier d'état `suivi/etat/<nom>.json` | Court, sans espace | Changer le nom = nouvelle poche qui repart de zéro |
| `style` | | `swing`, `day`, `long_terme` ou `signaux` | | |
| `capital` | | Capital fictif de départ | Ce que tu investiras vraiment un jour | Sans effet sur une poche déjà démarrée (voir section 7) |
| `univers` | | Codes Yahoo des actifs autorisés | 4 à 15 lignes liquides | Trop de lignes corrélées : l'agent Risque refusera beaucoup |
| `risque_par_trade` | 0,01 | Part du capital perdue si le stop est touché | 0,0025 à 0,01 | Au-delà de 0,02 : baisses de −25 % à −50 % (module 04) |
| `max_positions` | 5 | Positions ouvertes simultanément | 3 à 8 | Trop haut : capital dispersé ; trop bas : signaux perdus |
| `poids_max` | 0,25 | Part maximale du capital dans une ligne | 0,15 à 0,4 | Trop haut : une seule ligne peut faire −10 % de la poche en un gap |
| `risque_total_max` | 0,06 | Somme des risques ouverts (distance au stop) | 0,03 à 0,08 | Au-delà de 0,10 : une mauvaise journée corrélée fait très mal |
| `drawdown_max` | 0,15 | Coupe-circuit : plus d'entrées au-delà de cette baisse | 0,05 (day) à 0,20 | Trop serré : la poche s'arrête à chaque série normale |
| `pause_jours` | 10 | Durée du coupe-circuit, en jours calendaires | 5 à 30 | Trop long : la poche rate les reprises |
| `correlation_max` | 0,8 | Refuse une ligne trop corrélée à une position tenue | 0,7 à 0,9 | À 0,95 : presque plus de protection ; à 0,6 : presque tout est refusé |
| `cout_bps` | 5 | Frais par ordre, en points de base (0,05 %) | Les frais réels de ton futur courtier | Trop bas : backtest trop beau |
| `glissement_bps` | 2 | Écart défavorable au prix d'exécution | 2 à 10 (plus pour les petites valeurs) | Trop bas : backtest trop beau |

## 4. Paramètres du style `swing` (dans `params`)

| Paramètre | Défaut | Ce qu'il fait | Plage raisonnable | Effet si tu l'augmentes |
| --- | --- | --- | --- | --- |
| `tendance` | 200 | Longueur de la moyenne mobile de filtre | 100 à 250 | Filtre plus lent : moins d'entrées, mais plus tardives dans les retournements |
| `entree` | 20 | Plus haut des n jours à casser pour entrer | 20 à 55 | Moins de trades, de meilleure qualité, entrées plus tardives |
| `sortie` | 10 | Plus bas des n jours qui fait sortir | 10 à 20 | Trades plus longs, gains plus gros, mais plus de gain rendu |
| `atr` | 14 | Période de l'ATR | 14 à 20 | Stop plus stable |
| `atr_stop` | 2,0 | Distance du stop initial **et** suiveur, en ATR | 1,5 à 3,0 | Stop plus large : moins de sorties sur le bruit, positions plus petites |
| `momentum` | 126 | Période du classement du scanner (jours) | 63 à 252 | Préférence pour les tendances longues |
| `volume_min` | 0 | Volume moyen minimal sur 20 jours | 0 ou un seuil | Exclut les lignes peu liquides |

## 5. Paramètres du style `day`

| Paramètre | Défaut | Ce qu'il fait | Plage raisonnable | Remarque |
| --- | --- | --- | --- | --- |
| `n_ouverture` | 6 | Nombre de barres de 5 min du range d'ouverture (6 = 30 min) | 3 à 12 (15 à 60 min) | Plus long : range plus large, stop plus loin, moins de faux départs |
| `atr` | 14 | Période de l'ATR intraday | 14 | |
| `objectif_R` | 2,0 | Objectif en multiples du risque | 1,5 à 3,0 | Plus haut : moins souvent atteint, mais plus gros |
| `derniere_entree` | "15:00" | Plus d'entrée après cette heure (heure de New York) | "11:00" à "15:00" | Plus tôt : on évite l'après-midi sans direction |
| `fermeture` | "15:50" | Tout est fermé à partir de cette heure (heure de New York) | "15:30" à "15:55" | |

## 6. Paramètres des styles `long_terme` et `signaux`

| Style | Paramètre | Défaut | Valeurs possibles | Remarque |
| --- | --- | --- | --- | --- |
| long_terme | `methode` | "gmv_lw" | "gmv_lw", "parite_risque", "egal" | Module 08, section 8 |
| long_terme | `fenetre` | 252 | 126 à 504 jours | Plus long : poids plus stables, réaction plus lente |
| signaux | `fichier` | "node/signaux.jsonl" | chemin | Écrit par le serveur des alertes |
| signaux | `atr`, `atr_stop` | 14, 2,0 | comme swing | Stop utilisé si l'alerte n'en donne pas |

# Changer un réglage, pas à pas {#changer data-num="Partie III"}

## 7. Ce qui se passe quand tu changes un réglage

C'est le point à bien comprendre avant de toucher à quoi que ce soit.

| Ce que tu changes | Effet sur la Time Machine (backtest) | Effet sur le suivi papier (poche déjà démarrée) |
| --- | --- | --- |
| Une règle (`entree`, `atr_stop`, `risque_par_trade`…) | Tout l'historique est recalculé avec la nouvelle règle dès le prochain passage | La nouvelle règle s'applique **à partir de la prochaine barre** ; positions et cash sont conservés |
| L'univers | Recalculé ; les nouveaux symboles sont téléchargés au prochain passage | Les nouvelles lignes peuvent être achetées dès le lendemain |
| Le `capital` | Recalculé avec le nouveau capital | **Aucun effet** : la poche continue avec son cash et ses positions |
| Le `nom` | Nouvelle poche | **Nouvelle poche** qui repart de zéro (l'ancien état reste dans `suivi/etat/`) |

**Repartir de zéro avec une poche** : supprime ses deux fichiers d'état `suivi/etat/<nom>.json` et `suivi/etat/journal_<nom>.csv`. Au prochain passage, elle s'initialise à nouveau sur tout l'historique.

## 8. Modifier les réglages depuis GitHub, sur ton Mac

Pas besoin d'ouvrir le terminal : tout se fait dans Safari ou Chrome.

1. Va sur la page du dépôt `github.com/tresorkamdem/trade-skills`, dossier `agents`.
2. Ouvre `config.exemple.json`, clique sur l'icône **Copy raw file** (deux carrés, en haut à droite du contenu).
3. Reviens dans le dossier `agents`, bouton **Add file → Create new file**.
4. Nom du fichier : `config.json`. Colle le contenu (**Cmd + V**).
5. Modifie **une seule chose** (règle 5 des règles d'or). Exemple : dans la poche swing, ajoute `"atr_stop": 2.5` dans `params` :

```json
"params": {"atr_stop": 2.5}
```

6. En bas, **Commit changes…**, message clair (« swing : stop à 2,5 ATR »), **Commit directly to the main branch**, puis **Commit changes**.
7. Onglet **Actions → passage quotidien → Run workflow** pour voir l'effet tout de suite, ou attends le soir.
8. Note le changement dans ton **registre de calibrage** (section 10).

Pour les modifications suivantes : ouvre `agents/config.json` sur GitHub, icône **crayon** (*Edit this file*), modifie, **Commit changes**.

::: astuce
GitHub garde **tout l'historique** du fichier : bouton **History** sur la page de `config.json`. Si un changement était une mauvaise idée, tu retrouves l'ancienne version en un clic et tu la recolles. Tu peux aussi me demander dans un fil de faire le changement à ta place.
:::

## 9. Tester un réglage en papier avant de l'adopter

La méthode la plus sûre est la **poche jumelle** : tu gardes la poche d'origine intacte et tu ajoutes une copie avec le réglage modifié. Les deux tournent en parallèle chaque soir, sur les mêmes cours, avec le même moteur.

1. Dans `agents/config.json`, copie le bloc entier de la poche swing (de `{` à `}`), colle-le juste après (avec une virgule entre les deux blocs).
2. Change le `nom` de la copie : `"swing_b"`. Change **un seul** réglage, par exemple `"params": {"entree": 55}`.
3. Commit, puis **Run workflow**.
4. Ouvre `suivi/rapports/backtest.md` : la Time Machine compare désormais `swing` et `swing_b` sur 5 ans.
5. Laisse tourner les deux au moins **2 à 3 mois** en papier, puis compare le suivi papier (SESHAT, partie IV).

**Les critères pour adopter un réglage** (les mêmes que pour un passage en réel, en plus petit) :

| Critère | Seuil |
| --- | --- |
| Nombre de trades dans la Time Machine | ≥ 30, idéalement ≥ 100 |
| Espérance | > 0, et meilleure que la poche d'origine de façon nette (≥ 0,05R) |
| Perte maximale | Pas pire que la poche d'origine |
| **Robustesse** | Les réglages voisins (par exemple `entree` 40 et 70 si tu testes 55) donnent des résultats proches |
| Coûts doublés | Avec `cout_bps` et `glissement_bps` doublés, l'espérance reste positive |
| Papier | Après 2 à 3 mois, le suivi papier ressemble au backtest |

Si un seul de ces critères échoue, **garde la poche d'origine**. Supprime ensuite la jumelle de `config.json` (et ses fichiers d'état).

::: cle
Les cours de Yahoo ne passent pas depuis le serveur où j'ai écrit ce manuel, mais ils passent depuis ton Mac. Pour tester dix réglages en une soirée au lieu d'attendre dix passages, lance la Time Machine en local dans VS Code :

```bash
python -m tradeskills.agents actualiser --config agents/config.json
python -m tradeskills.agents backtest --config agents/config.json --source cache:donnees/marche --poche swing_b
```

Le premier téléchargement prend une à deux minutes ; ensuite, chaque backtest prend quelques secondes.
:::

## 10. Le registre de calibrage

Chaque essai est noté, **y compris les ratés** : c'est le nombre d'essais qui permet de dégonfler le Sharpe (module 07). Crée `journal/calibrage.md` dans le dépôt :

| Date | Poche | Changement | Trades | Espérance | Perte max. | Sharpe [IC] | Voisins stables ? | Décision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-02 | swing_b | entree 20 → 55 | | | | | | |
| 2026-11-09 | swing_c | atr_stop 2 → 2,5 | | | | | | |

**Après dix essais sur une même poche, arrête** : au-delà, tu ne trouves plus une meilleure règle, tu trouves le bruit du passé.

# Cinq recettes de calibrage {#recettes data-num="Partie III"}

## Recette 1 · Une poche plus prudente

```json
"risque_par_trade": 0.005, "risque_total_max": 0.04, "max_positions": 4, "drawdown_max": 0.10
```

Effet attendu : environ moitié moins de rendement et de perte maximale. L'espérance en R ne change pas (la règle d'entrée est la même) : la prudence ne rend pas une stratégie meilleure, elle la rend plus supportable.

## Recette 2 · Une poche swing plus sélective (tendances longues)

```json
"params": {"entree": 55, "sortie": 20, "atr_stop": 2.5}
```

C'est le système historique des « Turtles » (système 2). Moins de trades, plus longs ; les faux départs sont moins nombreux. À tester absolument en poche jumelle, et à vérifier avec les voisins (40/15 et 70/25).

## Recette 3 · Ajouter ou retirer un ETF

1. Trouve le code Xetra sur justETF (par exemple un ETF MSCI World Small Cap) ; le code Yahoo est le code Xetra suivi de `.DE`.
2. Vérifie sur Yahoo Finance (finance.yahoo.com) que le code existe et a au moins 3 ans d'historique.
3. Ajoute-le à `univers`. Au prochain passage, le rapport `donnees.md` doit l'afficher avec ✅.
4. Pense à la corrélation : un deuxième ETF MSCI World n'apporte rien, l'agent Risque le refusera la plupart du temps.

## Recette 4 · Remettre la poche day à plat

La poche day a une espérance de −0,14R. Plutôt que de chercher le réglage miracle (sur-optimisation garantie), essaie **une idée à la fois**, chacune en poche jumelle :

| Idée | Réglage | Hypothèse |
| --- | --- | --- |
| Range plus long | `"n_ouverture": 12` (1 heure) | Moins de faux départs juste après l'ouverture |
| Entrées le matin seulement | `"derniere_entree": "11:00"` | L'après-midi américaine est sans direction |
| Objectif plus proche | `"objectif_R": 1.5` | Plus de trades gagnants |
| Coûts réalistes | `"cout_bps": 2, "glissement_bps": 5` | Ce que coûterait vraiment IBKR sur ces titres |

Si aucune des quatre ne donne une espérance positive sur au moins 100 trades, **la conclusion honnête est d'arrêter cette poche** (recette 5). C'est exactement ce que dit le module 05 sur le day trading.

## Recette 5 · Arrêter une poche

Supprime son bloc de `agents/config.json` (attention aux virgules). Ses fichiers d'état restent dans `suivi/etat/` comme archive ; tu peux les supprimer si tu veux qu'elle reparte de zéro un jour.

## Les pièges du calibrage

| Piège | Symptôme | Parade |
| --- | --- | --- |
| Sur-optimisation | Tu essaies 30 réglages et gardes le meilleur | Registre, 10 essais maximum, voisins stables |
| Changer après une perte | « Le stop était trop serré » après une série de 5 pertes | Une série de pertes est normale (module 04). On ne change qu'à date fixe (revue trimestrielle) |
| Plusieurs changements à la fois | On ne sait plus ce qui a marché | Un seul réglage par poche jumelle |
| Augmenter le risque pour « rattraper » | `risque_par_trade` à 0,03 | Interdit : c'est le premier pas vers la martingale |
| Juger sur 3 semaines | « La nouvelle version gagne plus » | 30 trades minimum, 2 à 3 mois de papier |

# Anomalie corrigée : la poche long terme {#anomalie data-num="Partie III"}

En écrivant ce manuel, j'ai vérifié chaque chiffre de tes poches. La poche long terme avait un défaut, corrigé le 26 octobre 2026 :

- **Symptôme** : depuis le rééquilibrage du 4 novembre 2025, elle est investie à environ 99 % dans un seul ETF, les obligations d'État zone euro (EUNH), alors que `poids_max` vaut 40 %.
- **Cause** : pour estimer la covariance, le code retire tout actif qui a **un seul jour de cours manquant** dans la fenêtre de 252 jours. Les ETF de Xetra n'ont pas exactement le même nombre de barres chez Yahoo (1 273 à 1 275 selon le rapport `donnees.md`). Quand il ne reste qu'un actif, le plafond est relevé à 100 % (règle « au moins 1/n ») et tout part dans cet actif.
- **Preuve** : je l'ai reproduit sur des cours simulés : cinq actifs, un jour manquant pour quatre d'entre eux, et la poche se retrouve à 99 % dans le cinquième.
- **Conséquence** : sa Time Machine (Sharpe 1,24, chiffres de la partie II) mélangeait quatre ans de vrai GMV et un an d'obligations seules.
- **Correction** : les jours manquants sont maintenant complétés par le dernier cours connu avant de calculer les rendements (un jour sans cotation compte comme un rendement nul), au lieu d'écarter l'actif. Un test automatique (`pytest`) vérifie qu'un jour manquant ne fait plus sortir un ETF de la poche.
- **Ce que tu verras** : dès le passage du soir suivant, `suivi/rapports/backtest.md` donne la Time Machine corrigée ; remplace les chiffres long terme de la partie II par ceux-là. La poche papier, elle, se répartit à nouveau entre les cinq ETF au rééquilibrage du premier jour de cotation de novembre (2 novembre 2026). Note sa valeur ce jour-là : c'est le vrai départ de son suivi.

::: retenir
Ce genre d'anomalie est exactement ce que le module 07 apprend à chercher : un résultat trop beau ou un comportement étrange (99 % dans une ligne plafonnée à 40 %) se vérifie avant de se croire.
:::

# Le robot Or-1 {#or1 data-num="Partie III"}

Le robot or est **prévu, pas encore construit**. Seul le palier 0 (le module 12) existe. Voici le plan validé et ce que tu pourras régler.

## Les sept paliers

| Palier | Contenu | Validation |
| --- | --- | --- |
| 0 · Comprendre l'or | Module 12 | Les trois critères de la section 8 du module 12 |
| 1 · Les données | Une nouvelle poche « or » dans `tradeskills/agents`, signaux sur XAU/USD journalier (20 ans), exécution papier sur 4GLD en euros | Données propres sur 20 ans |
| 2 · Le backtest | 2005-2020 pour construire, **2021-2026 scellé**, testé une seule fois | Critères ci-dessous |
| 3 · Le contre-exemple | La martingale rejouée sur les mêmes données, avec la date de sa ruine | Tu sais l'expliquer |
| 4 · Le papier | Au moins 3 mois dans le passage du soir, avec Telegram et SESHAT | Papier proche du backtest |
| 5 · Le réel, petit | Ordres manuels sur 4GLD chez IBKR, petite taille | |
| 6 · Les devises | EUR/USD, puis USD/JPY, puis GBP/USD, risque ouvert global plafonné à 2 % | |

## Les réglages qu'Or-1 aura

Les règles du module 12 deviendront des paramètres, exactement comme la poche swing :

| Réglage prévu | Valeur de départ | À tester autour de |
| --- | --- | --- |
| Moyenne de tendance | 200 jours | 150, 250 |
| Cassure d'entrée | plus haut de 50 jours | 40, 70 |
| Stop initial | 2,5 × ATR(20) | 2,0 ; 3,0 |
| Sortie | plus bas de 20 jours, ou stop suiveur 3 × ATR(20) | 15 ; 30 jours |
| Risque par trade | 1 % | **ne pas dépasser** |
| Coupe-circuit | −15 % | |
| Capital fictif | 10 000 € | |

## Les critères pour passer en réel (palier 5)

| Critère | Seuil |
| --- | --- |
| Profit factor sur la période scellée 2021-2026 | ≥ 1,3 |
| Perte maximale | < 20 % **et** inférieure à celle de l'or acheté et gardé |
| Sharpe | ≥ 0,5 |
| Nombre de trades sur 20 ans | ≥ 30 |
| Robustesse | Les réglages voisins marchent aussi ; les coûts doublés aussi |
| Papier | Au moins 3 mois, cohérents avec le backtest |

Il n'y aura ni levier, ni vente à découvert, ni martingale, ni moyenne à la baisse, à aucun palier.
