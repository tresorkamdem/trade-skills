"""Agent Alertes : messages courts, affichés et envoyés sur Telegram si configuré.

Même format que le serveur `node/webhook.mjs`. Variables d'environnement :
TELEGRAM_BOT_TOKEN et TELEGRAM_CHAT_ID (jamais dans le code ni dans Git).
"""
from __future__ import annotations

import json
import os
import urllib.request


def formater(poche: str, m: dict) -> str:
    """Un mouvement du courtier (ou un ordre en attente) en message lisible."""
    q = m["quantite"]
    if m["motif"].startswith("annule"):
        return f"⚪ [{poche}] {m['symbole']} : ordre annulé ({m['motif']})"
    icone, sens = ("🟢", "ACHAT") if q > 0 else ("🔴", "VENTE")
    texte = f"{icone} [{poche}] {sens} {abs(q)} {m['symbole']}"
    if m.get("prix") is not None:
        texte += f" à {m['prix']:.2f}"
    if m.get("stop") is not None:
        texte += f", stop {m['stop']:.2f}"
    return f"{texte} ({m['motif']})"


def envoyer(messages: list[str], token: str | None = None, chat_id: str | None = None) -> bool:
    """Affiche les messages ; les envoie sur Telegram en un seul message si les jetons existent."""
    for m in messages:
        print(m)
    token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
    if not (messages and token and chat_id):
        return False
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps({"chat_id": chat_id, "text": "\n".join(messages)}).encode(),
        headers={"content-type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status == 200
