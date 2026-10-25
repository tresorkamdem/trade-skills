import { test } from 'node:test';
import assert from 'node:assert/strict';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createApp, formatMessage, parseAlert } from './webhook.mjs';

test('parse une alerte JSON et la met en forme', () => {
  const a = parseAlert('{"type":"achat","symbole":"SPY","prix":580.5,"stop":571.2}');
  assert.equal(formatMessage(a), '🟢 ACHAT SPY\nPrix : 580.5\nStop : 571.2');
});

test('accepte une alerte en texte libre', () => {
  assert.equal(formatMessage(parseAlert('Divergence sur DAX')), '🔔 Divergence sur DAX');
});

async function withServer(opts, fn) {
  const server = createApp({ logFile: join(tmpdir(), `alertes-${process.pid}.log`), ...opts });
  await new Promise((r) => server.listen(0, r));
  const base = `http://127.0.0.1:${server.address().port}`;
  try {
    await fn(base);
  } finally {
    server.close();
  }
}

test('refuse une requête sans le bon jeton', async () => {
  await withServer({ secret: 's3cret' }, async (base) => {
    const res = await fetch(`${base}/alerte?cle=faux`, { method: 'POST', body: '{}' });
    assert.equal(res.status, 401);
  });
});

test('transmet à Telegram avec le bon jeton', async () => {
  const sent = [];
  const fakeFetch = async (url, init) => {
    sent.push({ url, body: JSON.parse(init.body) });
    return { ok: true, status: 200 };
  };
  await withServer({ secret: 's3cret', token: 'T', chatId: '42', fetchImpl: fakeFetch }, async (base) => {
    const res = await fetch(`${base}/alerte?cle=s3cret`, {
      method: 'POST',
      body: '{"type":"sortie","symbole":"QQQ","prix":495}',
    });
    assert.equal(res.status, 200);
  });
  assert.equal(sent.length, 1);
  assert.equal(sent[0].url, 'https://api.telegram.org/botT/sendMessage');
  assert.equal(sent[0].body.chat_id, '42');
  assert.match(sent[0].body.text, /SORTIE QQQ/);
});
