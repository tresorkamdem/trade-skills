"""Outils pour les bourses africaines peu liquides : BRVM (UEMOA) et BVMAC (CEMAC).

Sur ces marchés, beaucoup de titres ne s'échangent pas tous les jours. Le dernier cours
reste alors affiché et le titre « rattrape » le marché avec retard. Sur des rendements
journaliers, corrélations et bêtas paraissent alors bien plus faibles qu'ils ne sont :
le portefeuille semble plus diversifié qu'il ne l'est. Ces fonctions mesurent la liquidité
et corrigent le bêta.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# Parité fixe du franc CFA (XOF en UEMOA, XAF en CEMAC) : 1 EUR = 655,957 FCFA
PARITE_EUR = 655.957
LIMITE_BRVM = 0.075  # variation maximale d'une action en une séance à la BRVM (à vérifier dans le règlement en vigueur)


def vers_eur(montant_fcfa: float | pd.Series) -> float | pd.Series:
    return montant_fcfa / PARITE_EUR


def liquidite(df: pd.DataFrame) -> dict[str, float]:
    """Indicateurs de liquidité d'un titre à partir de barres journalières (close, volume).

    - `jours_sans_echange` : part des séances avec un volume nul ;
    - `jours_inchanges` : part des séances où le cours n'a pas bougé ;
    - `valeur_moyenne_echangee` : volume x cours moyen par séance (en devise du titre) ;
    - `amihud` : illiquidité d'Amihud, variation absolue moyenne par million échangé
      (plus c'est haut, plus un ordre fait bouger le prix).
    """
    close, volume = df["close"], df["volume"].fillna(0)
    r = close.pct_change().iloc[1:]
    valeur = (volume * close).iloc[1:]
    actifs = valeur > 0
    return {
        "jours_sans_echange": float((volume == 0).mean()),
        "jours_inchanges": float((r == 0).mean()),
        "valeur_moyenne_echangee": float(valeur.mean()),
        "amihud": float((r[actifs].abs() / (valeur[actifs] / 1e6)).mean()) if actifs.any() else float("nan"),
    }


def jours_a_la_limite(df: pd.DataFrame, limite: float = LIMITE_BRVM, tolerance: float = 0.002) -> int:
    """Nombre de séances où le titre a fini à sa limite de variation (hausse ou baisse bloquée)."""
    r = df["close"].pct_change().abs()
    return int((r >= limite - tolerance).sum())


def beta_dimson(r_titre: pd.Series, r_marche: pd.Series, retards: int = 1) -> float:
    """Bêta de Dimson (1979) : somme des bêtas sur le marché d'avant, de la veille et du jour.

    Quand le titre ne cote pas tous les jours, il réagit au marché avec retard ; le bêta
    habituel (même jour seulement) est alors trop faible."""
    X = pd.concat({k: r_marche.shift(k) for k in range(-retards, retards + 1)}, axis=1)
    d = pd.concat([r_titre.rename("y"), X], axis=1).dropna()
    A = np.column_stack([np.ones(len(d)), d.drop(columns="y").to_numpy()])
    coefs = np.linalg.lstsq(A, d["y"].to_numpy(), rcond=None)[0]
    return float(coefs[1:].sum())


def beta_simple(r_titre: pd.Series, r_marche: pd.Series) -> float:
    d = pd.concat([r_titre, r_marche], axis=1).dropna()
    return float(np.cov(d.iloc[:, 0], d.iloc[:, 1])[0, 1] / d.iloc[:, 1].var())


def cotations_figees(df: pd.DataFrame, proba_echange: float, seed: int | None = 0) -> pd.DataFrame:
    """Simule un titre peu liquide à partir d'un titre liquide : les jours sans échange,
    le cours reste celui du dernier échange et le volume est nul. Sert aux exercices."""
    rng = np.random.default_rng(seed)
    echange = rng.random(len(df)) < proba_echange
    echange[0] = True
    out = df.copy()
    out.loc[~echange, ["open", "high", "low", "close"]] = np.nan
    out["close"] = out["close"].ffill()
    for c in ("open", "high", "low"):
        out[c] = out[c].fillna(out["close"])
    out.loc[~echange, "volume"] = 0
    return out
