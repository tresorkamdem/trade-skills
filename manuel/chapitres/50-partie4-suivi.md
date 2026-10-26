::: {.partie pnum="Partie IV"}
# Le suivi automatique {#partie4}

Chaque soir de semaine, sans que ton ordinateur soit allumé, GitHub fait travailler tes agents, puis t'envoie le résultat sur Telegram et dans SESHAT. Voici ce qui se passe, comment le lire, et quoi faire quand quelque chose casse.
:::

# Le passage du soir {#passage data-num="Partie IV"}

## 1. Quand

Le workflow `.github/workflows/quotidien.yml` démarre à **22 h 30 UTC du lundi au vendredi**, après la clôture américaine :

| Période | Heure à Berlin |
| --- | --- |
| Heure d'hiver (du dernier dimanche d'octobre au dernier dimanche de mars) | **23 h 30** |
| Heure d'été | **0 h 30** (la nuit suivante) |

GitHub ne garantit pas l'heure exacte des tâches planifiées : un retard de 10 à 30 minutes est courant, parfois davantage. Le message Telegram arrive donc en général entre 23 h 30 et minuit en hiver. Tu le lis **le lendemain matin** : c'est le premier geste de ta routine (partie V).

## 2. Les sept étapes

| Étape du workflow | Commande | Ce qu'elle fait |
| --- | --- | --- |
| 1 · Préparer | `pip install -e ".[donnees]"` | Installe le code de ton dépôt sur une machine neuve de GitHub |
| 2 · Récupérer le cache | `actions/cache/restore` | Reprend les cours déjà téléchargés les soirs précédents |
| 3 · Actualiser les cours | `agents actualiser` | Ajoute les barres nouvelles de Yahoo, contrôle la qualité, écrit `donnees.md` |
| 4 · Passage quotidien | `agents quotidien` | Fait avancer chaque poche sur les barres nouvelles, écrit le rapport du jour, **envoie Telegram** |
| 5 · Backtest et tableau | `agents backtest`, `agents tableau` | Refait la Time Machine et le tableau de bord HTML |
| 6 · Envoyer à SESHAT | `agents publier` | Envoie un instantané JSON à la section Trading de SESHAT |
| 7 · Enregistrer | `git commit` « Suivi du AAAA-MM-JJ [skip ci] » | Enregistre états, journaux et rapports dans `suivi/` |

Le tableau de bord est aussi téléchargeable dans l'onglet **Actions**, en bas de la page du passage (artefact `tableau-de-bord`).

**Lancer un passage à la main** : onglet **Actions → passage quotidien → Run workflow → Run workflow**. Utilise toujours ce bouton plutôt que « Re-run » sur un ancien passage : « Re-run » reprend l'ancienne version du code et des réglages.

## 3. Ce qui est écrit dans `suivi/`

| Fichier | Contenu |
| --- | --- |
| `suivi/etat/<poche>.json` | Positions, ordres en attente, cash, historique de valeur de la poche |
| `suivi/etat/journal_<poche>.csv` | Le journal des trades clos, format de `journal/modele_journal.csv` |
| `suivi/rapports/AAAA-MM-JJ.md` | Le rapport du jour |
| `suivi/rapports/backtest.md` et `.json` | La Time Machine de chaque poche |
| `suivi/rapports/donnees.md` | Le contrôle qualité des cours |
| `suivi/rapports/instantane.json` | Ce qui a été envoyé à SESHAT |
| `suivi/tableau.html` | Le tableau de bord |

::: attention
Le dépôt est **public** : ton suivi papier est visible de tous. C'est très bien pour une vitrine (module 10), mais ne mets jamais d'informations personnelles ni, plus tard, de positions réelles dans ce dépôt. Les jetons (Telegram, SESHAT) sont dans les **secrets** GitHub, jamais dans le code.
:::

# Lire ce que disent tes agents {#lire data-num="Partie IV"}

## 4. Le message Telegram

Un exemple : le titre et les lignes des poches sont ceux du passage du 26 octobre 2026 ; les lignes d'ordres sont des exemples pour montrer chaque cas.

```
📊 Passage du 26/10/2026 · total 51,224 (+28.1%), argent fictif
• swing : 13,164 (+31.6%)
• day : 4,760 (-4.8%)
• long_terme : 28,300 (+41.5%)
• tradingview : 5,000 (+0.0%)
🟢 [swing] ACHAT 12 SAP.DE à 191.04, stop 180.12 (entree)
🔴 [swing] VENTE 3 MSFT à 520.49 (stop)
⚪ [swing] AMZN : ordre annulé (annule_gap)
🟢 [swing] ACHAT 8 SIE.DE, stop 241.30 (demain : entree)
```

| Ligne | Comment la lire |
| --- | --- |
| 📊 titre | Valeur totale des poches, en % du capital de départ (40 000 €). **Arrive chaque soir, même sans ordre** : s'il manque, le passage n'a pas tourné |
| • une ligne par poche | Valeur et performance depuis le capital de départ de la poche |
| 🟢 ACHAT … à prix | Achat **exécuté** à l'ouverture de la dernière séance |
| 🔴 VENTE … (stop / sortie_donchian / objectif / fin_de_seance / reequilibrage) | Vente exécutée, avec sa raison |
| ⚪ ordre annulé (annule_gap / annule_cash) | Achat abandonné : ouverture sous le stop, ou pas assez de cash |
| 🟢 … (demain : entree) | Ordre **prévu** pour la prochaine ouverture, sans prix (il sera connu demain) |

::: cle
Les montants des poches affichés aujourd'hui incluent les **5 ans de backtest** qui ont servi à initialiser les poches au premier passage (partie II). Pour mesurer ton **vrai suivi papier**, retiens les valeurs du premier passage comme point de départ :

| Poche | Valeur de départ du suivi papier (26 octobre 2026) |
| --- | --- |
| swing | 13 164 € |
| day | 4 760 € |
| long_terme | 28 300 € |
| tradingview | 5 000 € |
| **Total** | **51 224 €** |

Chaque fin de mois, note dans ton journal la valeur de chaque poche et calcule sa performance **depuis ces valeurs**. C'est ce chiffre qui comptera pour décider d'un passage en réel.
:::

## 5. Le rapport du jour

`suivi/rapports/AAAA-MM-JJ.md` (sur GitHub, il s'affiche joliment mis en page) donne, pour chaque poche :

- la **dernière barre** traitée (vérifie que c'est bien la dernière séance) ;
- la **valeur**, l'**exposition** (part investie), le **risque ouvert** (perte si tous les stops étaient touchés), la **volatilité**, la **VaR et la CVaR** à 1 jour, la **baisse depuis le plus haut** ;
- le tableau des **positions** (quantité, entrée, dernier cours, stop, gain ou perte) ;
- les **ordres** pour la prochaine ouverture ;
- les **derniers refus de l'agent Risque**, avec leur raison ;
- le nombre de **nouvelles exécutions**.

**Comment le lire en 2 minutes** : (1) la baisse depuis le plus haut est-elle proche du coupe-circuit ? (2) le risque ouvert est-il sous le maximum ? (3) les refus sont-ils logiques ? (4) une position a-t-elle un stop très proche du cours (sortie probable demain) ?

## 6. SESHAT, section Trading

La section **Trading** de SESHAT (le backoffice de MAÀT Analytics) affiche les mêmes informations dans une interface complète et privée : valeur des poches, courbe de performance, positions, Time Machine comparée à 1/n, derniers trades en R. Le passage du soir y envoie un instantané par la fonction Supabase `trading_ingest`, avec le jeton robot de ton compte SESHAT (secrets `SESHAT_SUPABASE_URL`, `SESHAT_SUPABASE_ANON_KEY`, `SESHAT_ROBOT_TOKEN`).

Sur ton iPhone, ajoute la page Trading de SESHAT à l'écran d'accueil (Safari → bouton Partager → **Sur l'écran d'accueil**) : elle s'ouvre alors comme une application.

## 7. Le tableau de bord HTML

`suivi/tableau.html` est une page unique, sans connexion, en clair ou sombre selon ton système : valeur de chaque poche, courbe du suivi, positions, ordres, poids de la poche long terme face au GMV Ledoit-Wolf, à la parité de risque et à 1/n, Time Machine contre 1/n, derniers trades et alertes. Pour l'ouvrir : onglet **Actions**, dernier passage, artefact **tableau-de-bord**, puis double-clic sur le fichier dézippé.

# Quand quelque chose casse {#depannage data-num="Partie IV"}

## 8. Le diagnostic en trois questions

1. **Ai-je reçu le message 📊 hier soir ?** Non → le passage n'a pas tourné, ou Telegram a échoué. Va dans **Actions**.
2. **Le dernier passage est-il vert ?** Rouge → clique dessus, puis sur l'étape rouge : le message d'erreur est en bas de son journal.
3. **La dernière barre du rapport est-elle la dernière séance ?** Non → problème de données (Yahoo).

## 9. Les pannes courantes

| Symptôme | Cause probable | Solution |
| --- | --- | --- |
| Pas de message, pas de passage dans Actions | GitHub a désactivé la tâche planifiée (après une longue inactivité du dépôt), ou retard de GitHub | Actions → passage quotidien : s'il y a un bandeau « This scheduled workflow is disabled », clique **Enable workflow**. Sinon, **Run workflow** |
| Passage vert, mais pas de message Telegram | Secrets Telegram absents ou faux | Actions → **tester Telegram** → Run workflow. S'il échoue : refais les secrets `TELEGRAM_BOT_TOKEN` et `TELEGRAM_CHAT_ID`, et envoie `/start` à ton bot |
| « Telegram a refusé le message » | Jeton révoqué, ou tu as bloqué le bot | Nouveau jeton chez @BotFather, mets à jour le secret |
| Étape « Actualiser les cours » rouge, ou ⚠️ dans `donnees.md` | Yahoo indisponible ou a changé quelque chose | L'ancien cache est gardé : attends un jour. Si ça dure plus de 3 jours, demande-moi de regarder |
| « dernière barre vieille de plus de 5 jours » | Code retiré de la cote, ou jour férié long | Vérifie le code sur Yahoo Finance ; retire-le de l'univers si besoin |
| « Paramètres inconnus pour … » ou erreur JSON | Faute dans `agents/config.json` | Corrige le fichier (partie III, section 2) ou supprime-le pour revenir à l'exemple |
| « Envoyer à SESHAT » rouge (404, 401) | Mauvaise URL Supabase ou jeton robot changé | Vérifie les trois secrets SESHAT ; le jeton se recrée dans SESHAT, Radar → Automatik |
| « Nouvelles exécutions : 0 » plusieurs jours | Jours fériés, ou aucune barre nouvelle | Normal un jour férié ; sinon, regarde `donnees.md` |
| L'étape « Enregistrer le suivi » échoue | Conflit avec un commit fait en même temps | Relance avec **Run workflow** |

## 10. Les secrets du dépôt

**Settings → Secrets and variables → Actions** :

| Secret | Sert à |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | Jeton du bot « Tresor Trading » (chez @BotFather) |
| `TELEGRAM_CHAT_ID` | Ton identifiant de conversation |
| `SESHAT_SUPABASE_URL` | L'adresse du projet Supabase de SESHAT (`https://xxxx.supabase.co`) |
| `SESHAT_SUPABASE_ANON_KEY` | Sa clé publique (anon), jamais la clé secrète |
| `SESHAT_ROBOT_TOKEN` | Le jeton robot de ton compte SESHAT |

Un secret ne se relit jamais : on le remplace (*Update*). Ne les écris nulle part ailleurs, ni dans ce manuel, ni dans un fichier du dépôt.
