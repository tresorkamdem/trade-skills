# Outils Node.js : alertes TradingView vers Telegram

`webhook.mjs` est un petit serveur sans dépendance qui reçoit les alertes de TradingView et les envoie sur Telegram. Chaque alerte est aussi enregistrée dans `alertes.log`, et chaque alerte avec un symbole est ajoutée à `signaux.jsonl`, que la poche `tradingview` des agents Python trade en papier (voir [agents/README.md](../agents/README.md#la-poche-tradingview)).

## Mise en place

1. Crée un bot Telegram avec **@BotFather** et note son jeton. Envoie un message au bot, puis récupère ton `chat_id` via `https://api.telegram.org/bot<jeton>/getUpdates`.
2. Lance le serveur :
   ```bash
   cd node
   WEBHOOK_SECRET=un-long-jeton-aleatoire TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... npm start
   ```
3. Rends-le accessible depuis Internet (TradingView n'accepte que les ports 80 et 443) : un petit serveur, un service comme Render ou Railway, ou un tunnel (`cloudflared`, `ngrok`) pour tester.
4. Dans TradingView, crée une alerte sur `systeme_tendance_indicateur.pine`, coche **Webhook URL** et mets `https://<ton-hôte>/alerte?cle=<WEBHOOK_SECRET>`.
5. Pour une alerte que tu écris toi-même, mets ce message (JSON) :
   ```json
   {"type":"achat","symbole":"{{exchange}}:{{ticker}}","prix":{{close}},"stop":123.4,"strategie":"mon_setup"}
   ```
   `type` vaut `achat` ou `sortie`. Garde la bourse devant le code (`XETR:SXR8`) : elle sert à retrouver le code Yahoo (`SXR8.DE`). `stop` est facultatif.

Pour que la poche `tradingview` utilise les alertes, lance le passage quotidien sur la même machine que le serveur (ou indique le chemin du fichier dans `params.fichier` de la poche). `SIGNAUX_FICHIER` change l'emplacement du fichier.

Les webhooks TradingView demandent un abonnement payant. Ne mets jamais les jetons dans le code ni dans Git.

## Tests

```bash
cd node && npm test
```

## Lien avec MAÀT

SESHAT a déjà une intégration Telegram. Une fois l'outil stable, ses alertes pourront y être rattachées.
