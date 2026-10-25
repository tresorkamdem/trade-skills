// Serveur minimal sans dépendance : TradingView -> (webhook) -> ce serveur -> Telegram.
// Chaque alerte avec un symbole est aussi ajoutée à `signaux.jsonl`, que la poche `signaux`
// des agents Python lit pour trader ces alertes en papier (voir agents/README.md).
//
// Variables d'environnement :
//   WEBHOOK_SECRET      jeton à mettre dans l'URL de l'alerte : https://<hôte>/alerte?cle=<jeton>
//   TELEGRAM_BOT_TOKEN  jeton du bot (créé avec @BotFather)
//   TELEGRAM_CHAT_ID    identifiant de la conversation qui reçoit les messages
//   PORT                port d'écoute (3000 par défaut)
//   SIGNAUX_FICHIER     fichier des signaux (signaux.jsonl par défaut)
import { createServer } from 'node:http';
import { appendFile } from 'node:fs/promises';

export function parseAlert(body) {
  let data;
  try {
    data = JSON.parse(body);
  } catch {
    return { type: 'texte', message: String(body).trim() };
  }
  if (typeof data !== 'object' || data === null) throw new Error('Alerte invalide');
  return data;
}

export function formatMessage(a) {
  if (a.type === 'texte') return `🔔 ${a.message}`;
  const icon = a.type === 'achat' ? '🟢' : a.type === 'sortie' ? '🔴' : '🔔';
  const parts = [`${icon} ${String(a.type).toUpperCase()} ${a.symbole ?? ''}`.trim()];
  if (a.prix !== undefined) parts.push(`Prix : ${a.prix}`);
  if (a.stop !== undefined) parts.push(`Stop : ${a.stop}`);
  if (a.unite !== undefined) parts.push(`Unité : ${a.unite}`);
  return parts.join('\n');
}

async function sendTelegram(text, { token, chatId, fetchImpl = fetch }) {
  const res = await fetchImpl(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ chat_id: chatId, text }),
  });
  if (!res.ok) throw new Error(`Telegram a répondu ${res.status}`);
}

// Une ligne JSON par alerte exploitable : heure de réception (UTC) + champs de l'alerte.
// Le symbole garde le format TradingView (`XETR:SXR8`) ; Python le traduit en code Yahoo.
export function toSignal(alert, receivedAt = new Date()) {
  if (alert.type === 'texte' || !alert.symbole) return null;
  const { type, symbole, prix, stop, poche, strategie } = alert;
  return { recu: receivedAt.toISOString(), type, symbole, prix, stop, poche, strategie };
}

export function createApp({
  secret,
  token,
  chatId,
  logFile = 'alertes.log',
  signauxFile = 'signaux.jsonl',
  fetchImpl = fetch,
}) {
  return createServer(async (req, res) => {
    const url = new URL(req.url, 'http://localhost');
    if (req.method !== 'POST' || url.pathname !== '/alerte') {
      res.writeHead(404).end();
      return;
    }
    if (!secret || url.searchParams.get('cle') !== secret) {
      res.writeHead(401).end();
      return;
    }
    let body = '';
    for await (const chunk of req) {
      body += chunk;
      if (body.length > 10_000) {
        res.writeHead(413).end();
        return;
      }
    }
    try {
      const alert = parseAlert(body);
      const text = formatMessage(alert);
      const now = new Date();
      await appendFile(logFile, `${now.toISOString()}\t${JSON.stringify(alert)}\n`);
      const signal = toSignal(alert, now);
      if (signal) await appendFile(signauxFile, `${JSON.stringify(signal)}\n`);
      if (token && chatId) await sendTelegram(text, { token, chatId, fetchImpl });
      res.writeHead(200, { 'content-type': 'text/plain' }).end('ok');
    } catch (err) {
      res.writeHead(400, { 'content-type': 'text/plain' }).end(err.message);
    }
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const port = Number(process.env.PORT ?? 3000);
  createApp({
    secret: process.env.WEBHOOK_SECRET,
    token: process.env.TELEGRAM_BOT_TOKEN,
    chatId: process.env.TELEGRAM_CHAT_ID,
    signauxFile: process.env.SIGNAUX_FICHIER ?? 'signaux.jsonl',
  }).listen(port, () => console.log(`Webhook en écoute sur le port ${port}`));
}
