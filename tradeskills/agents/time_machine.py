"""Agent Time Machine : rejoue une poche sur l'historique avant de l'utiliser.

Compare à une référence (1/n achat-conservation de l'univers), donne un intervalle de
confiance du Sharpe (bootstrap par blocs, module 07) et le bilan des trades en R.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .. import metrics, validation
from . import journal_de_bord
from .config import Poche
from .moteur import Moteur


@dataclass
class Resultat:
    poche: Poche
    courbe: pd.Series           # valeur de la poche à chaque barre
    rendements: pd.Series       # rendements journaliers de la poche
    reference: pd.Series        # rendements journaliers de la référence
    trades: pd.DataFrame
    moteur: Moteur

    def resume(self) -> pd.DataFrame:
        r, b = self.rendements, self.reference.reindex(self.rendements.index).fillna(0)
        return pd.DataFrame({
            "poche": metrics.summary(r, periods=252),
            "reference_1/n": metrics.summary(b, periods=252),
        })

    def vers_dict(self) -> dict:
        """Résumé sérialisable en JSON, lu par le tableau de bord."""
        bas, haut = validation.bootstrap_sharpe_ci(self.rendements, periods=252, n=1_000)
        courbe = journalier(self.courbe)
        reference = self.poche.capital * (1 + self.reference.reindex(courbe.index).fillna(0)).cumprod()
        nb, res = len(self.trades), self.resume()
        return {
            "nom": self.poche.nom,
            "style": self.poche.style,
            "capital": self.poche.capital,
            "debut": f"{courbe.index[0]:%Y-%m-%d}",
            "fin": f"{courbe.index[-1]:%Y-%m-%d}",
            "valeur_finale": float(courbe.iloc[-1]),
            "resume": {k: {c: _propre(v[c]) for c in res.columns} for k, v in res.iterrows()},
            "sharpe_ic": [_propre(bas), _propre(haut)],
            "trades": nb,
            "esperance_R": _propre(journal_de_bord.stats_r(self.trades)["esperance_R"]) if nb else None,
            "courbe": [[f"{t:%Y-%m-%d}", round(float(v), 2)] for t, v in courbe.items()],
            "reference": [[f"{t:%Y-%m-%d}", round(float(v), 2)] for t, v in reference.items()],
        }

    def texte(self) -> str:
        bas, haut = validation.bootstrap_sharpe_ci(self.rendements, periods=252, n=1_000)
        res = self.resume()
        lignes = [
            f"## Time Machine · {self.poche.nom} ({self.poche.style})",
            "",
            f"Du {self.courbe.index[0]:%Y-%m-%d} au {self.courbe.index[-1]:%Y-%m-%d}, "
            f"capital {self.poche.capital:,.0f} → {self.courbe.iloc[-1]:,.0f}.",
            "",
            "| Mesure | Poche | Référence 1/n |",
            "| --- | --- | --- |",
            *[f"| {k} | {v['poche']:.3f} | {v['reference_1/n']:.3f} |" for k, v in res.iterrows()],
            "",
            _intervalle(bas, haut),
            "",
            "### Trades",
            "",
            journal_de_bord.bilan(self.trades) if self.poche.style != "long_terme"
            else f"Rééquilibrages mensuels : {sum(m['motif'] == 'reequilibrage' for m in self.moteur.courtier.mouvements)} ordres.",
        ]
        return "\n".join(lignes)


def _propre(x) -> float | None:
    x = float(x)
    return x if np.isfinite(x) else None


def _intervalle(bas: float, haut: float) -> str:
    if not (np.isfinite(bas) and np.isfinite(haut)):
        return "Sharpe : trop peu de jours de données pour un intervalle de confiance."
    texte = f"Sharpe : intervalle de confiance à 95 % [{bas:.2f} ; {haut:.2f}]"
    return texte + (" : contient 0, résultat non significatif." if bas <= 0 <= haut else ".")


def journalier(serie: pd.Series) -> pd.Series:
    """Dernière valeur de chaque jour (utile pour les barres intraday)."""
    return serie.groupby(serie.index.normalize()).last()


def rejouer(poche: Poche, donnees: dict[str, pd.DataFrame], jusqua=None, signaux: pd.DataFrame | None = None) -> Resultat:
    m = Moteur(poche)
    m.charger(donnees, signaux)
    m.executer(jusqua)
    courbe = m.courbe()
    rendements = journalier(courbe).pct_change().dropna()
    closes = journalier(m.closes.ffill())
    reference = closes.pct_change().iloc[1:].mean(axis=1)
    trades = pd.DataFrame(m.courtier.trades, columns=journal_de_bord.COLONNES)
    return Resultat(poche, courbe, rendements, reference, trades, m)
