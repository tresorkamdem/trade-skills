"""Moteur commun : fait travailler les agents barre après barre pour une poche.

Le même code sert au backtest (Time Machine, sur tout l'historique) et au suivi
quotidien (orchestrateur, sur les seules barres nouvelles depuis le dernier passage,
à partir de l'état sauvegardé). Ce qui marche en backtest est donc exactement ce qui
tourne en papier.

À chaque barre t :
1. Courtier : exécute à l'ouverture les ordres décidés en t-1, puis vérifie stops et objectifs.
2. Sortie : remonte les stops suiveurs, décide les sorties (day : immédiatement à la clôture).
3. Scanner → Entrée → Budget → Risque : nouveaux ordres pour l'ouverture de t+1.
   (Long terme : rééquilibrage vers les poids cibles le premier jour de chaque mois.)
"""
from __future__ import annotations

import math

import pandas as pd

from . import budget, entree_sortie, risque, scanner
from .config import Poche
from .courtier import CourtierPapier, Ordre


class Moteur:
    def __init__(self, poche: Poche, etat: dict | None = None):
        self.poche = poche
        etat = etat or {}
        self.courtier = (
            CourtierPapier.depuis_dict(etat["courtier"]) if "courtier" in etat
            else CourtierPapier(poche.capital, poche.cout_bps, poche.glissement_bps)
        )
        self.derniere_date = pd.Timestamp(etat["derniere_date"]) if etat.get("derniere_date") else None
        self.dernier_prix: dict[str, float] = dict(etat.get("dernier_prix", {}))
        self.plus_haut: float = etat.get("plus_haut", poche.capital)
        self.historique: list[list] = [list(x) for x in etat.get("historique", [])]
        self.coupe_circuit = pd.Timestamp(etat["coupe_circuit"]) if etat.get("coupe_circuit") else None
        self.refus: list[dict] = []

    # --- données ------------------------------------------------------------
    def charger(self, donnees: dict[str, pd.DataFrame]) -> None:
        self.donnees = donnees
        self.lignes = {s: scanner.preparer(df, self.poche) for s, df in donnees.items()}
        self.closes = pd.DataFrame({s: df["close"] for s, df in donnees.items()}).sort_index()
        # Accès rapide aux barres : {date: {symbole: ligne}}
        self._barres: dict[pd.Timestamp, dict[str, pd.Series]] = {}
        for s, f in self.lignes.items():
            for t, row in zip(f.index, f.to_dict("records")):
                self._barres.setdefault(t, {})[s] = row

    def executer(self, jusqua=None) -> None:
        """Avance sur toutes les barres postérieures au dernier passage (jusqu'à `jusqua` inclus)."""
        dates = sorted(self._barres)
        if self.derniere_date is not None:
            dates = [t for t in dates if t > self.derniere_date]
        if jusqua is not None:
            dates = [t for t in dates if t <= pd.Timestamp(jusqua)]
        for t in dates:
            self.pas(t)

    # --- une barre ------------------------------------------------------------
    def pas(self, t: pd.Timestamp) -> None:
        c, poche = self.courtier, self.poche
        barres = self._barres[t]
        c.executer_ouvertures(t, barres)
        c.verifier_stops(t, barres)
        self.dernier_prix.update({s: b["close"] for s, b in barres.items()})

        if poche.style == "long_terme":
            if self.derniere_date is None or t.to_period("M") != self.derniere_date.to_period("M"):
                self._reequilibrer(t)
        else:
            self._sorties(t, barres)
            self._entrees(t, barres)

        valeur = c.valeur(self.dernier_prix)
        self.plus_haut = max(self.plus_haut, valeur)
        self.historique.append([str(t), valeur])
        self.derniere_date = t

    def _sorties(self, t, barres) -> None:
        c = self.courtier
        for s in list(c.positions):
            if s not in barres or c.en_attente(s):
                continue
            raison = entree_sortie.sortie(pd.Series(barres[s]), c.positions[s], self.poche)
            if raison is None:
                continue
            if self.poche.style == "day":
                c.cloturer(t, s, barres[s]["close"], raison)
            else:
                c.passer(Ordre(s, -c.positions[s].quantite, raison))

    def _entrees(self, t, barres) -> None:
        c, poche = self.courtier, self.poche
        exclus = set(c.positions) | {o.symbole for o in c.ordres}
        if poche.style == "day":  # un seul trade par symbole et par séance
            jour = str(t.normalize())[:10]
            exclus |= {m["symbole"] for m in c.mouvements if m["date"][:10] == jour}
        lignes = {s: pd.Series(b) for s, b in barres.items()}
        props = [entree_sortie.entree(lignes[s], s, poche) for s in scanner.scanner(lignes, poche, exclus)]
        props = [p for p in props if p is not None]
        if not props:
            return
        valeur = c.valeur(self.dernier_prix)
        candidats = budget.dimensionner(props, poche, c, valeur)
        rendements = self.closes.loc[:t].tail(61).pct_change().iloc[1:] if c.positions else None
        acceptes, refus = risque.controler(
            candidats, poche, c, valeur, self.dernier_prix, self._drawdown(t, valeur), rendements
        )
        for p, q in acceptes:
            c.passer(Ordre(p.symbole, q, "entree", p.stop, p.objectif, p.setup, risque_max=(p.prix - p.stop) * q))
        self.refus += [{"date": str(t), "symbole": s, "raison": r} for s, r in refus]

    def _drawdown(self, t, valeur: float) -> float:
        """Baisse depuis le plus haut ; après `pause_jours` de coupe-circuit, le plus haut repart de la valeur actuelle."""
        dd = valeur / self.plus_haut - 1
        if dd > -self.poche.drawdown_max:
            self.coupe_circuit = None
        elif self.coupe_circuit is None:
            self.coupe_circuit = t
        elif (t - self.coupe_circuit).days >= self.poche.pause_jours:
            self.plus_haut, self.coupe_circuit, dd = valeur, None, 0.0
        return dd

    def _reequilibrer(self, t) -> None:
        c, poche = self.courtier, self.poche
        fenetre = poche.param("fenetre")
        R = self.closes.loc[:t].pct_change().iloc[1:].tail(fenetre).dropna(axis=1)
        if len(R) < fenetre or R.empty:
            return
        cibles = budget.poids_cibles(R, poche)
        valeur = c.valeur(self.dernier_prix) * 0.99  # marge pour les frais et le glissement
        for s in sorted(set(cibles.index) | set(c.positions)):
            prix = self.dernier_prix[s]
            voulu = math.floor(cibles.get(s, 0.0) * valeur / prix)
            actuel = c.positions[s].quantite if s in c.positions else 0
            if voulu != actuel:
                c.passer(Ordre(s, voulu - actuel, "reequilibrage"))

    # --- résultats ------------------------------------------------------------
    def courbe(self) -> pd.Series:
        if not self.historique:
            return pd.Series(dtype=float)
        idx, vals = zip(*self.historique)
        return pd.Series(vals, index=pd.DatetimeIndex(pd.to_datetime(list(idx)), name="date"), name=self.poche.nom)

    def etat(self) -> dict:
        return {
            "poche": self.poche.nom,
            "derniere_date": str(self.derniere_date) if self.derniere_date is not None else None,
            "dernier_prix": self.dernier_prix,
            "plus_haut": self.plus_haut,
            "historique": self.historique,
            "coupe_circuit": str(self.coupe_circuit) if self.coupe_circuit is not None else None,
            "courtier": self.courtier.vers_dict(),
        }
