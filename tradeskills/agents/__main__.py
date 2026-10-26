"""Ligne de commande des agents.

  python -m tradeskills.agents actualiser --donnees donnees/marche
  python -m tradeskills.agents backtest   --source cache:donnees/marche
  python -m tradeskills.agents quotidien  --source cache:donnees/marche
  python -m tradeskills.agents tableau    --source cache:donnees/marche
  python -m tradeskills.agents publier    --source cache:donnees/marche   (envoi vers SESHAT)

Sources : simulee, yahoo, csv:<dossier> (exports TradingView) ou cache:<dossier> (rempli par `actualiser`).
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from . import config as cfg
from . import instantane, marche, orchestre, signaux, tableau, time_machine


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m tradeskills.agents", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("commande", choices=["actualiser", "backtest", "quotidien", "tableau", "publier"])
    parser.add_argument("--config", default="agents/config.exemple.json")
    parser.add_argument("--source", default="simulee", help="simulee, yahoo, csv:<dossier> ou cache:<dossier>")
    parser.add_argument("--donnees", default="donnees/marche", help="dossier du cache (commande actualiser)")
    parser.add_argument("--poche", help="backtest d'une seule poche (par défaut : toutes)")
    parser.add_argument("--dossier", default="agents", help="où écrire états, journaux et rapports")
    parser.add_argument("--sans-alertes", action="store_true", help="n'envoie rien sur Telegram")
    args = parser.parse_args(argv)

    conf = cfg.charger(args.config)
    dossier = Path(args.dossier)

    if args.commande == "actualiser":
        yahoo, bilan = marche.SourceYahoo(), []
        a_charger = {}
        for p in conf.poches:  # un symbole commun à plusieurs poches n'est téléchargé qu'une fois
            a_charger.setdefault("day" if p.style == "day" else "jour", set()).update(p.univers)
        for style, symboles in sorted(a_charger.items()):
            bilan += marche.actualiser(yahoo, sorted(symboles), style, args.donnees)
        texte = marche.bilan_texte(bilan)
        _ecrire(dossier / "rapports" / "donnees.md", texte)
        _ecrire(dossier / "rapports" / "donnees.json", json.dumps(bilan, ensure_ascii=False))
        print(texte)
        return

    src = marche.source(args.source)
    if args.commande == "quotidien":
        print(orchestre.passage(conf, src, dossier, envoyer=not args.sans_alertes))
        return

    if args.commande == "publier":
        inst = instantane.construire(conf, dossier, src)
        chemin = instantane.ecrire(inst, dossier / "rapports" / "instantane.json")
        print(f"Instantané : {chemin}")
        if all(os.environ.get(v) for v in ("SESHAT_SUPABASE_URL", "SESHAT_SUPABASE_ANON_KEY", "SESHAT_ROBOT_TOKEN")):
            print(f"Envoyé à SESHAT : rapport {instantane.publier(inst)}")
        else:
            print("SESHAT non configuré (SESHAT_SUPABASE_URL, SESHAT_SUPABASE_ANON_KEY, SESHAT_ROBOT_TOKEN) : rien envoyé")
        return

    if args.commande == "tableau":
        chemin = tableau.generer(conf, dossier, src)
        print(f"Tableau de bord : {chemin}")
        return

    poches = [conf.poche(args.poche)] if args.poche else conf.poches
    resultats = []
    for p in poches:
        donnees = src.historique(p.univers, p.style)
        if not donnees:
            print(f"⚠️ {p.nom} : aucune donnée, poche ignorée")
            continue
        resultats.append(time_machine.rejouer(p, donnees, signaux=signaux.de_la_poche(p)))
    rapport = "\n\n".join(["# Time Machine", "", *[r.texte() for r in resultats]])
    _ecrire(dossier / "rapports" / "backtest.md", rapport)
    _ecrire(dossier / "rapports" / "backtest.json",
            json.dumps({"source": args.source, "poches": [r.vers_dict() for r in resultats]}, ensure_ascii=False))
    print(rapport)


def _ecrire(chemin: Path, texte: str) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(texte, encoding="utf-8")


if __name__ == "__main__":
    main()
