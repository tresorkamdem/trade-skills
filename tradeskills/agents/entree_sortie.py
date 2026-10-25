"""Agents Entrée et Sortie : règles de trading de chaque style, appliquées à la clôture d'une barre."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .config import Poche


@dataclass
class Proposition:
    symbole: str
    setup: str
    prix: float          # dernier cours, sert à dimensionner
    stop: float
    objectif: float | None = None


def entree(row: pd.Series, symbole: str, poche: Poche) -> Proposition | None:
    """Signal d'achat à la clôture de la barre, exécuté à l'ouverture de la suivante."""
    p = poche.param
    close = row["close"]

    if poche.style == "swing":
        if pd.isna(row["haut_entree"]) or pd.isna(row["atr"]) or pd.isna(row["tendance"]):
            return None
        if close > row["haut_entree"] and close > row["tendance"]:
            return Proposition(symbole, "cassure_donchian", close, close - p("atr_stop") * row["atr"])

    elif poche.style == "day":
        if pd.isna(row["or_haut"]) or row["rang"] < p("n_ouverture") or row["heure"] >= p("derniere_entree"):
            return None
        if close > row["or_haut"] and close > row["vwap"] and row["or_bas"] < close:
            stop = row["or_bas"]
            return Proposition(symbole, "range_ouverture", close, stop, close + p("objectif_R") * (close - stop))

    return None


def sortie(row: pd.Series, position, poche: Poche) -> str | None:
    """Remonte le stop suiveur et renvoie la raison de sortir, ou None pour garder la position."""
    p = poche.param

    if poche.style == "swing":
        if not pd.isna(row["atr"]):
            position.stop = max(position.stop, row["close"] - p("atr_stop") * row["atr"])
        if not pd.isna(row["bas_sortie"]) and row["close"] < row["bas_sortie"]:
            return "sortie_donchian"

    elif poche.style == "day" and row["heure"] >= p("fermeture"):
        return "fin_de_seance"

    return None
