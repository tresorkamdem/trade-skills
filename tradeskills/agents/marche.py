"""Sources de données des agents.

Chaque source renvoie {symbole: DataFrame OHLCV} : barres journalières pour les poches
`swing` et `long_terme`, barres intraday pour la poche `day`.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .. import data


def synthetic_intraday(
    n_days: int = 60, bars_per_day: int = 78, start_price: float = 100.0, vol: float = 0.20, seed: int | None = 0
) -> pd.DataFrame:
    """Barres de 5 minutes simulées, de 09:30 à 15:55, sans structure exploitable."""
    df = data.synthetic_ohlcv(
        n_days * bars_per_day, start_price, drift=0.07 / bars_per_day, vol=vol / np.sqrt(bars_per_day), seed=seed
    )
    days = pd.bdate_range("2024-01-02", periods=n_days)
    minutes = pd.to_timedelta(9 * 60 + 30 + 5 * np.arange(bars_per_day), unit="min")
    df.index = pd.DatetimeIndex([d + m for d in days for m in minutes], name="date")
    return df


class SourceSimulee:
    """Cours simulés : pour apprendre et tester les agents sans connexion."""

    def __init__(self, n_jours: int = 1_000, n_jours_intraday: int = 60, seed: int = 0):
        self.n_jours, self.n_jours_intraday, self.seed = n_jours, n_jours_intraday, seed

    def historique(self, symboles: list[str], style: str) -> dict[str, pd.DataFrame]:
        out = {}
        for i, s in enumerate(symboles):
            seed = self.seed + i
            if style == "day":
                out[s] = synthetic_intraday(self.n_jours_intraday, seed=seed)
            else:
                out[s] = data.synthetic_ohlcv(self.n_jours, vol=0.15 + 0.02 * i, seed=seed)
        return out


class SourceCSV:
    """Exports TradingView (ou d'un broker) : `<dossier>/<SYMBOLE>.csv` en journalier,
    `<dossier>/<SYMBOLE>_intraday.csv` pour la poche day.

    `tolerante=True` ignore les fichiers absents (cache incomplet après un téléchargement raté)."""

    def __init__(self, dossier: str | Path, tolerante: bool = False):
        self.dossier, self.tolerante = Path(dossier), tolerante

    def historique(self, symboles: list[str], style: str) -> dict[str, pd.DataFrame]:
        out = {}
        for s in symboles:
            chemin = chemin_cache(self.dossier, s, style)
            if self.tolerante and not chemin.exists():
                print(f"⚠️ {chemin} absent : {s} ignoré")
                continue
            out[s] = data.load_ohlcv_csv(chemin)
        return out


class SourceYahoo:
    """Yahoo Finance via `yfinance` (pip install yfinance). Gratuit, non officiel, usage personnel
    uniquement ; l'intraday 5 minutes est limité aux 60 derniers jours (le cache les accumule)."""

    def telecharger(self, symbole: str, style: str) -> pd.DataFrame:
        import yfinance as yf

        periode, intervalle = ("60d", "5m") if style == "day" else ("5y", "1d")
        df = yf.Ticker(symbole).history(period=periode, interval=intervalle, auto_adjust=True)
        df.columns = [c.lower() for c in df.columns]
        if style == "day":  # heure de la bourse, sans fuseau : la séance US reste 09:30-15:55
            df.index = df.index.tz_localize(None)
        else:
            df.index = df.index.tz_localize(None).normalize()
        df.index.name = "date"
        return df[["open", "high", "low", "close", "volume"]].dropna()

    def historique(self, symboles: list[str], style: str) -> dict[str, pd.DataFrame]:
        return {s: self.telecharger(s, style) for s in symboles}


# --- cache local et contrôle qualité -------------------------------------------------------

def chemin_cache(dossier: str | Path, symbole: str, style: str) -> Path:
    return Path(dossier) / f"{symbole}{'_intraday' if style == 'day' else ''}.csv"


def qualite(df: pd.DataFrame, style: str, aujourdhui: pd.Timestamp | None = None) -> list[str]:
    """Problèmes de données qui fausseraient un backtest. Liste vide si tout va bien."""
    if df.empty:
        return ["aucune barre"]
    pb = []
    prix = df[["open", "high", "low", "close"]]
    if prix.isna().any().any():
        pb.append(f"{int(prix.isna().any(axis=1).sum())} barres avec un prix manquant")
    if (prix <= 0).any().any():
        pb.append("prix nuls ou négatifs")
    incoherent = (df["high"] < df["low"]) | (df["close"] > df["high"] * 1.0001) | (df["close"] < df["low"] * 0.9999)
    if incoherent.any():
        pb.append(f"{int(incoherent.sum())} barres incohérentes (clôture hors du range haut-bas)")
    if df.index.duplicated().any():
        pb.append(f"{int(df.index.duplicated().sum())} dates en double")
    rendements = df["close"].pct_change().abs()
    if (rendements > 0.4).any():
        pb.append(f"variation de plus de 40 % le {rendements.idxmax():%Y-%m-%d} : split ou erreur ?")
    jours = df.index.normalize().unique()
    if style != "day" and len(jours) > 1:
        trou = pd.Series(jours[1:] - jours[:-1], index=jours[1:]).max()
        if trou > pd.Timedelta(days=10):
            pb.append(f"trou de {trou.days} jours dans l'historique")
    aujourdhui = pd.Timestamp.today().normalize() if aujourdhui is None else aujourdhui
    retard = (aujourdhui - df.index[-1].normalize()).days
    if retard > 5:
        pb.append(f"dernière barre vieille de {retard} jours")
    return pb


def fusionner(ancien: pd.DataFrame | None, nouveau: pd.DataFrame) -> pd.DataFrame:
    """Ajoute les nouvelles barres au cache ; en cas de doublon, la version la plus récente gagne
    (Yahoo corrige parfois la dernière barre et ajuste l'historique des dividendes)."""
    if ancien is None or ancien.empty:
        return nouveau.sort_index()
    cols = list(dict.fromkeys([*ancien.columns, *nouveau.columns]))
    df = pd.concat([ancien.reindex(columns=cols), nouveau.reindex(columns=cols)])
    return df[~df.index.duplicated(keep="last")].sort_index()


def actualiser(
    distante, symboles: list[str], style: str, dossier: str | Path, aujourdhui: pd.Timestamp | None = None
) -> list[dict]:
    """Télécharge chaque symbole, le fusionne au cache `<dossier>/<SYMBOLE>[_intraday].csv`
    et contrôle la qualité. Un échec de téléchargement garde l'ancien cache."""
    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    bilan = []
    for s in symboles:
        chemin = chemin_cache(dossier, s, style)
        ancien = data.load_ohlcv_csv(chemin) if chemin.exists() else None
        ligne = {"symbole": s, "style": style, "erreur": None}
        try:
            nouveau = distante.telecharger(s, style)
            if nouveau.empty:
                raise ValueError("aucune donnée reçue (code inconnu ou marché fermé ?)")
        except Exception as e:  # noqa: BLE001 - un symbole raté ne doit pas bloquer les autres
            ligne["erreur"] = str(e) or type(e).__name__
            nouveau = None
        df = ancien if nouveau is None else fusionner(ancien, nouveau)
        if df is not None and nouveau is not None:
            df.to_csv(chemin, index_label="date")
        n_avant = 0 if ancien is None else len(ancien)
        ligne.update({
            "barres": 0 if df is None else len(df),
            "nouvelles": 0 if df is None else len(df) - n_avant,
            "derniere": None if df is None else str(df.index[-1]),
            "problemes": [] if df is None else qualite(df, style, aujourdhui),
        })
        bilan.append(ligne)
    return bilan


def bilan_texte(bilan: list[dict]) -> str:
    lignes = ["# Données de marché", "", "| Symbole | Style | Barres | Nouvelles | Dernière | Problèmes |",
              "| --- | --- | --- | --- | --- | --- |"]
    for b in bilan:
        pb = "; ".join(([f"❌ {b['erreur']}"] if b["erreur"] else []) + b["problemes"]) or "✅"
        lignes.append(f"| {b['symbole']} | {b['style']} | {b['barres']} | {b['nouvelles']} | "
                      f"{(b['derniere'] or '–')[:16]} | {pb} |")
    return "\n".join(lignes)


def source(spec: str):
    """`simulee`, `yahoo`, `csv:<dossier>` ou `cache:<dossier>` (le cache rempli par `actualiser`)."""
    if spec == "simulee":
        return SourceSimulee()
    if spec == "yahoo":
        return SourceYahoo()
    if spec.startswith("csv:"):
        return SourceCSV(spec[4:])
    if spec.startswith("cache:"):
        return SourceCSV(spec[6:], tolerante=True)
    raise ValueError(f"Source inconnue : {spec}")
