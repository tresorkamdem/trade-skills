"""Ligne de commande des agents.

  python -m tradeskills.agents backtest  --config agents/config.exemple.json --source simulee
  python -m tradeskills.agents quotidien --config agents/config.exemple.json --source yahoo
"""
from __future__ import annotations

import argparse
from pathlib import Path

from . import config as cfg
from . import marche, orchestre, time_machine


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m tradeskills.agents", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("commande", choices=["backtest", "quotidien"])
    parser.add_argument("--config", default="agents/config.exemple.json")
    parser.add_argument("--source", default="simulee", help="simulee, yahoo ou csv:<dossier>")
    parser.add_argument("--poche", help="backtest d'une seule poche (par défaut : toutes)")
    parser.add_argument("--dossier", default="agents", help="où écrire états, journaux et rapports")
    parser.add_argument("--sans-alertes", action="store_true", help="n'envoie rien sur Telegram")
    args = parser.parse_args(argv)

    conf = cfg.charger(args.config)
    src = marche.source(args.source)
    if args.commande == "quotidien":
        print(orchestre.passage(conf, src, args.dossier, envoyer=not args.sans_alertes))
        return

    poches = [conf.poche(args.poche)] if args.poche else conf.poches
    textes = [time_machine.rejouer(p, src.historique(p.univers, p.style)).texte() for p in poches]
    rapport = "\n\n".join(["# Time Machine", "", *textes])
    chemin = Path(args.dossier) / "rapports" / "backtest.md"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(rapport, encoding="utf-8")
    print(rapport)


if __name__ == "__main__":
    main()
