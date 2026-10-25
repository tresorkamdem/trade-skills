"""Solutions du module 11 (exercices 1 à 6, sur données simulées)."""
import numpy as np
import pandas as pd

from tradeskills import afrique, data, portfolio
from tradeskills.optim import gmv_long_only

# 1
fcfa = 3_000 * afrique.PARITE_EUR
print(f"1. 3 000 EUR = {fcfa:,.0f} FCFA ; rendement en dividende {1_100 / 15_000:.1%} ; "
      f"13 actions -> {afrique.vers_eur(13 * 1_100):.2f} EUR de dividendes")

# 2
var99 = 10_000 * 2.326 * 0.12
print(f"2. VaR 99 % sur un an {var99:,.0f} EUR, dévaluation de 50 % : perte de 5 000 EUR. "
      "Le risque de change n'apparaît dans aucune série historique depuis 1994 : il faut un scénario de stress à part.")

# 3
rng = np.random.default_rng(0)
marche = data.synthetic_ohlcv(1_500, seed=1)
titre = marche.copy()
titre["close"] = marche["close"] * np.exp(np.cumsum(rng.normal(0, 0.008, len(marche))))
for c in ("open", "high", "low"):
    titre[c] = titre["close"]
fige = afrique.cotations_figees(titre, proba_echange=1 / 3, seed=2)
rm, rf = marche["close"].pct_change(), fige["close"].pct_change()
hebdo = lambda df: df["close"].resample("W").last().pct_change()  # noqa: E731
print("3. bêta journalier {:.2f}, Dimson 1 retard {:.2f}, Dimson 5 retards {:.2f}, hebdomadaire {:.2f} (vrai bêta : 1)".format(
    afrique.beta_simple(rf, rm), afrique.beta_dimson(rf, rm, 1), afrique.beta_dimson(rf, rm, 5),
    afrique.beta_simple(hebdo(fige), hebdo(marche))))

# 4
for nom, df in [("liquide", titre), ("figé", fige)]:
    liq = afrique.liquidite(df)
    print(f"4. {nom} : {liq['jours_sans_echange']:.0%} de séances sans échange, Amihud {liq['amihud']:.4f}")
valeur_jour = 2_000_000  # FCFA échangés par séance en moyenne, ordre de grandeur d'un petit titre
print(f"   5 M FCFA à 20 % de 2 M par séance : {np.ceil(5_000_000 / (0.2 * valeur_jour)):.0f} séances pour sortir")

# 5
titres = {}
for i in range(5):
    t = marche.copy()
    t["close"] = marche["close"] * np.exp(np.cumsum(rng.normal(0, 0.01, len(marche))))
    for c in ("open", "high", "low"):
        t[c] = t["close"]
    titres[f"T{i}"] = afrique.cotations_figees(t, 0.25, seed=i) if i >= 2 else t
closes = pd.DataFrame({k: v["close"] for k, v in titres.items()})
for nom, R in [("journalier", closes.pct_change().dropna()), ("hebdomadaire", closes.resample("W").last().pct_change().dropna()),
               ("mensuel", closes.resample("ME").last().pct_change().dropna())]:
    c = R.corr().to_numpy()
    w = gmv_long_only(portfolio.cov_ledoit_wolf(R.to_numpy()))
    print(f"5. {nom:<12} : corrélation moyenne {c[np.triu_indices(5, 1)].mean():.2f}, "
          f"part GMV des titres figés T2-T4 {w[2:].sum():.0%} (1/n : 60 %)")
print("   En journalier, les titres figés paraissent moins corrélés au reste qu'ils ne le sont :"
      " l'optimisation les surpondère au nom d'une diversification qui n'existe pas.")

# 6
for n, nom in [(12, "mensuel"), (1, "annuel")]:
    print(f"6. rééquilibrage {nom} : {n * 0.20 * 0.015:.2%} de coûts par an")
