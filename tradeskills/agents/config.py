"""Configuration des poches : chaque poche a son capital, son style et ses règles.

Trois styles :
- `swing` : cassure de Donchian dans une tendance (le système de `pine/systeme_tendance_strategie.pine`),
  barres journalières, positions tenues de quelques jours à quelques semaines ;
- `day` : cassure du range d'ouverture au-dessus du VWAP, barres intraday, tout est fermé en fin de séance ;
- `long_terme` : allocation GMV Ledoit-Wolf (la thèse), parité de risque ou 1/n, rééquilibrée chaque mois ;
- `signaux` : les entrées et sorties viennent de tes alertes TradingView (reçues par `node/webhook.mjs`),
  barres journalières, avec les mêmes contrôles de budget et de risque que les autres poches.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

STYLES = ("swing", "day", "long_terme", "signaux")

DEFAUTS: dict[str, dict] = {
    "swing": {
        "tendance": 200,      # moyenne mobile de tendance
        "entree": 20,         # Donchian d'entrée
        "sortie": 10,         # Donchian de sortie
        "atr": 14,
        "atr_stop": 2.0,      # stop initial et stop suiveur en ATR
        "momentum": 126,      # classement du scanner : performance sur ~6 mois
        "volume_min": 0,      # volume moyen minimal sur 20 jours
    },
    "day": {
        "n_ouverture": 6,     # nombre de barres du range d'ouverture (6 x 5 min = 30 min)
        "atr": 14,
        "objectif_R": 2.0,    # objectif de gain en multiples du risque
        "derniere_entree": "15:00",
        "fermeture": "15:50",  # heure (des données) à partir de laquelle tout est fermé
    },
    "long_terme": {
        "methode": "gmv_lw",  # gmv_lw, parite_risque ou egal
        "fenetre": 252,       # jours de rendements pour estimer la covariance
    },
    "signaux": {
        "fichier": "node/signaux.jsonl",  # écrit par node/webhook.mjs
        "atr": 14,
        "atr_stop": 2.0,      # stop si l'alerte n'en donne pas (ou en donne un au-dessus du prix)
    },
}


@dataclass
class Poche:
    nom: str
    style: str
    capital: float
    univers: list[str]
    risque_par_trade: float = 0.01   # part du capital perdue si le stop est touché
    max_positions: int = 5
    poids_max: float = 0.25          # part maximale du capital dans une ligne
    risque_total_max: float = 0.06   # somme des risques ouverts (distance au stop)
    drawdown_max: float = 0.15       # coupe-circuit : plus d'entrées au-delà de cette baisse...
    pause_jours: int = 10            # ...pendant ce nombre de jours, puis on repart du niveau atteint
    correlation_max: float = 0.8     # refuse une ligne trop corrélée à une position existante
    cout_bps: float = 5.0            # frais par ordre, en points de base du montant
    glissement_bps: float = 2.0      # écart défavorable au prix d'exécution
    params: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.style not in STYLES:
            raise ValueError(f"Style inconnu « {self.style} » : choisir parmi {STYLES}")
        inconnus = set(self.params) - set(DEFAUTS[self.style])
        if inconnus:
            raise ValueError(f"Paramètres inconnus pour {self.style} : {sorted(inconnus)}")

    def param(self, cle: str):
        return self.params.get(cle, DEFAUTS[self.style][cle])


@dataclass
class Config:
    poches: list[Poche]

    def poche(self, nom: str) -> Poche:
        for p in self.poches:
            if p.nom == nom:
                return p
        raise KeyError(f"Pas de poche « {nom} » ; poches : {[p.nom for p in self.poches]}")


def charger(chemin: str | Path) -> Config:
    brut = json.loads(Path(chemin).read_text(encoding="utf-8"))
    return Config([Poche(**p) for p in brut["poches"]])
