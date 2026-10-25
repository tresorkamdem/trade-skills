# Outils Node.js : alertes TradingView vers Telegram

`webhook.mjs` est un petit serveur sans dépendance qui reçoit les alertes de TradingView et les envoie sur Telegram. Chaque alerte est aussi enregistrée dans `alertes.log`.

## Mise en place

1. Crée un bot Telegram avec **@BotFather** et note son jeton. Envoie un message au bot, puis récupère ton `chat_id` via `https://api.telegram.org/bot<jeton>/getUpdates`.
2. Lance le serveur :
   ```bash
   cd node
   WEBHOOK_SECRET=un-long-jeton-aleatoire TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... npm start
   ```
3. Rends-le accessible depuis Internet (TradingView n'accepte que les ports 80 et 443) : un petit serveur, un service comme Render ou Railway, ou un tunnel (`cloudflared`, `ngrok`) pour tester.
4. Dans TradingView, crée une alerte sur `systeme_tendance_indicateur.pine`, coche **Webhook URL** et mets `https://<ton-hôte>/alerte?cle=<WEBHOOK_SECRET>`.

Les webhooks TradingView demandent un abonnement payant. Ne mets jamais les jetons dans le code ni dans Git.

## Tests

```bash
cd node && npm test
```

## Lien avec MAÀT

SESHAT a déjà une intégration Telegram. Une fois l'outil stable, ses alertes pourront y être rattachées.
