"""Agent Courtier : un courtier papier (argent fictif) qui exécute les ordres de façon réaliste.

- Les ordres décidés à la clôture sont exécutés à l'ouverture de la barre suivante,
  avec glissement et frais.
- Un achat est annulé si l'ouverture est déjà sous le stop (gap défavorable) ; si elle est
  plus haute que prévu, la quantité est réduite pour ne pas dépasser le risque prévu.
- Les stops et objectifs sont vérifiés pendant la barre ; si l'ouverture saute le stop,
  la sortie se fait à l'ouverture, pas au stop. Si stop et objectif sont tous deux
  touchés dans la même barre, on suppose le pire (le stop).

Achats uniquement (pas de vente à découvert). Un courtier réel (IBKR, Alpaca) pourra
remplacer cette classe en gardant les mêmes méthodes.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field


@dataclass
class Position:
    symbole: str
    quantite: int
    prix_entree: float
    date_entree: str
    setup: str = ""
    stop: float | None = None
    stop_initial: float | None = None
    objectif: float | None = None
    frais: float = 0.0


@dataclass
class Ordre:
    symbole: str
    quantite: int          # > 0 achat, < 0 vente
    motif: str             # entree, sortie_..., reequilibrage
    stop: float | None = None
    objectif: float | None = None
    setup: str = ""
    risque_max: float | None = None   # montant maximal perdu au stop ; réduit la quantité si l'ouverture monte


@dataclass
class CourtierPapier:
    cash: float
    cout_bps: float = 5.0
    glissement_bps: float = 2.0
    positions: dict[str, Position] = field(default_factory=dict)
    ordres: list[Ordre] = field(default_factory=list)
    trades: list[dict] = field(default_factory=list)       # trades clos avec stop, format du journal
    mouvements: list[dict] = field(default_factory=list)   # toutes les exécutions

    # --- ordres -------------------------------------------------------------
    def passer(self, ordre: Ordre) -> None:
        self.ordres.append(ordre)

    def en_attente(self, symbole: str) -> bool:
        return any(o.symbole == symbole for o in self.ordres)

    # --- exécution ----------------------------------------------------------
    def _frais(self, montant: float) -> float:
        return abs(montant) * self.cout_bps / 1e4

    def _noter(self, t, symbole, quantite, prix, motif) -> None:
        self.mouvements.append({"date": str(t), "symbole": symbole, "quantite": int(quantite),
                                "prix": float(prix), "motif": motif})

    def _acheter(self, t, o: Ordre, prix: float) -> None:
        q = min(o.quantite, math.floor(self.cash / (prix * (1 + self.cout_bps / 1e4))))
        if o.risque_max is not None and o.stop is not None:
            q = min(q, math.floor(o.risque_max / (prix - o.stop)))
        if q <= 0:
            self._noter(t, o.symbole, 0, prix, "annule_cash")
            return
        frais = self._frais(q * prix)
        self.cash -= q * prix + frais
        pos = self.positions.get(o.symbole)
        if pos is None:
            self.positions[o.symbole] = Position(o.symbole, q, prix, str(t), o.setup, o.stop, o.stop, o.objectif, frais)
        else:  # renforcement (rééquilibrage) : prix moyen
            pos.prix_entree = (pos.prix_entree * pos.quantite + prix * q) / (pos.quantite + q)
            pos.quantite += q
            pos.frais += frais
        self._noter(t, o.symbole, q, prix, o.motif)

    def _vendre(self, t, symbole: str, quantite: int, prix: float, motif: str) -> None:
        pos = self.positions[symbole]
        q = min(quantite, pos.quantite)
        frais = self._frais(q * prix)
        self.cash += q * prix - frais
        self._noter(t, symbole, -q, prix, motif)
        if q < pos.quantite:
            pos.quantite -= q
            pos.frais += frais
            return
        del self.positions[symbole]
        if pos.stop_initial is not None:
            self.trades.append({
                "date": pos.date_entree[:10], "actif": symbole, "sens": "achat", "setup": pos.setup,
                "entree": pos.prix_entree, "stop": pos.stop_initial, "sortie": prix, "quantite": pos.quantite,
                "frais": pos.frais + frais, "note": motif, "date_sortie": str(t),
            })

    def executer_ouvertures(self, t, barres: dict) -> None:
        """Exécute à l'ouverture les ordres des symboles qui ont une barre en t (ventes d'abord)."""
        g = self.glissement_bps / 1e4
        restants = []
        for o in sorted(self.ordres, key=lambda o: o.quantite):
            if o.symbole not in barres:
                restants.append(o)
                continue
            ouverture = barres[o.symbole]["open"]
            if o.quantite < 0:
                if o.symbole in self.positions:
                    self._vendre(t, o.symbole, -o.quantite, ouverture * (1 - g), o.motif)
            elif o.stop is not None and ouverture <= o.stop:
                self._noter(t, o.symbole, 0, ouverture, "annule_gap")
            else:
                self._acheter(t, o, ouverture * (1 + g))
        self.ordres = restants

    def verifier_stops(self, t, barres: dict) -> None:
        g = self.glissement_bps / 1e4
        for s in list(self.positions):
            pos, b = self.positions[s], barres.get(s)
            if b is None:
                continue
            if pos.stop is not None and b["low"] <= pos.stop:
                self._vendre(t, s, pos.quantite, min(b["open"], pos.stop) * (1 - g), "stop")
            elif pos.objectif is not None and b["high"] >= pos.objectif:
                self._vendre(t, s, pos.quantite, max(b["open"], pos.objectif) * (1 - g), "objectif")

    def cloturer(self, t, symbole: str, prix: float, motif: str) -> None:
        """Sortie immédiate au prix donné (par ex. la clôture en fin de séance)."""
        self._vendre(t, symbole, self.positions[symbole].quantite, prix * (1 - self.glissement_bps / 1e4), motif)

    # --- état ---------------------------------------------------------------
    def valeur(self, prix: dict[str, float]) -> float:
        return self.cash + sum(p.quantite * prix.get(s, p.prix_entree) for s, p in self.positions.items())

    def risque_ouvert(self, prix: dict[str, float]) -> float:
        """Perte si tous les stops étaient touchés maintenant."""
        return sum(max(prix.get(s, p.prix_entree) - p.stop, 0) * p.quantite
                   for s, p in self.positions.items() if p.stop is not None)

    def vers_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def depuis_dict(cls, d: dict) -> "CourtierPapier":
        d = dict(d)
        d["positions"] = {s: Position(**p) for s, p in d["positions"].items()}
        d["ordres"] = [Ordre(**o) for o in d["ordres"]]
        return cls(**d)
