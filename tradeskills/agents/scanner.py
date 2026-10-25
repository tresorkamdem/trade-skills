"""Agent Scanner : prépare les indicateurs de chaque actif et classe les candidats.

`preparer` calcule toutes les colonnes une seule fois sur l'historique complet. Les
indicateurs ne regardent que le passé, donc la ligne à la date t est exactement celle
qu'on aurait obtenue en direct à la clôture de t.
"""
from __future__ import annotations

import pandas as pd

from .. import indicators as ind
from .config import Poche


def preparer(df: pd.DataFrame, poche: Poche) -> pd.DataFrame:
    p = poche.param
    close = df["close"]
    out = df[["open", "high", "low", "close"]].copy()

    if poche.style == "signaux":
        out["atr"] = ind.atr(df, p("atr"))

    elif poche.style == "swing":
        out["atr"] = ind.atr(df, p("atr"))
        out["tendance"] = ind.sma(close, p("tendance"))
        out["haut_entree"] = ind.donchian(df, p("entree"))["haut"]
        out["bas_sortie"] = ind.donchian(df, p("sortie"))["bas"]
        out["momentum"] = close / close.shift(p("momentum")) - 1
        volume = df["volume"] if "volume" in df else pd.Series(float("nan"), index=df.index)
        out["volume_moyen"] = volume.rolling(20).mean()

    elif poche.style == "day":
        jour = df.index.normalize()
        rang = df.groupby(jour).cumcount()
        n = p("n_ouverture")
        # Range d'ouverture : plus haut et plus bas des n premières barres, connu à la fin de la n-ième
        out["or_haut"] = df["high"].groupby(jour).cummax().where(rang == n - 1).groupby(jour).ffill()
        out["or_bas"] = df["low"].groupby(jour).cummin().where(rang == n - 1).groupby(jour).ffill()
        out["vwap"] = ind.vwap(df) if "volume" in df else close.groupby(jour).expanding().mean().droplevel(0)
        out["atr"] = ind.atr(df, p("atr"))
        out["rang"] = rang
        out["heure"] = df.index.strftime("%H:%M")
        out["momentum"] = close / df["open"].groupby(jour).transform("first") - 1

    return out


def scanner(lignes: dict[str, pd.Series], poche: Poche, exclus: set[str] = frozenset()) -> list[str]:
    """Symboles qui passent les filtres, du plus fort au plus faible momentum."""
    retenus = []
    for s, row in lignes.items():
        if s in exclus or pd.isna(row.get("momentum")):
            continue
        if poche.style == "swing":
            if pd.isna(row["tendance"]) or row["close"] <= row["tendance"]:
                continue
            vmin = poche.param("volume_min")
            if vmin and not row["volume_moyen"] >= vmin:
                continue
        elif poche.style == "day" and not row["close"] > row["vwap"]:
            continue
        retenus.append((row["momentum"], s))
    return [s for _, s in sorted(retenus, reverse=True)]
