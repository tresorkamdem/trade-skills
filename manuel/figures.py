"""Figures du manuel (SVG), calculées avec le code du dépôt et l'état réel des poches dans suivi/.

  python manuel/figures.py   ->   manuel/build/fig/*.svg
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from tradeskills import data, indicators as ind  # noqa: E402
from tradeskills.risk import max_drawdowns, simulate_equity  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "manuel" / "build" / "fig"

BLEU, ORANGE, VERT, JAUNE, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#6250d6"
ROUGE, GRIS, ENCRE, ENCRE2 = "#e34948", "#9a9893", "#0b0b0b", "#52514e"

plt.rcParams.update({
    "font.family": ["Inter", "DejaVu Sans"], "font.size": 9, "axes.edgecolor": "#c9c8c3",
    "axes.labelcolor": ENCRE2, "xtick.color": ENCRE2, "ytick.color": ENCRE2, "axes.grid": True,
    "grid.color": "#ebeae6", "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 10, "axes.titleweight": "semibold", "axes.titlelocation": "left",
    "legend.frameon": False, "lines.linewidth": 1.8, "svg.fonttype": "none", "figure.dpi": 100,
})


def fig(w=6.4, h=2.8, **kw):
    return plt.subplots(figsize=(w, h), **kw)


def save(f, nom):
    f.tight_layout()
    f.savefig(SORTIE / f"{nom}.svg", bbox_inches="tight")
    plt.close(f)


def pct(ax, axe="y", dec=0):
    fmt = matplotlib.ticker.PercentFormatter(1.0, decimals=dec)
    (ax.yaxis if axe == "y" else ax.xaxis).set_major_formatter(fmt)


def carnet():
    f, ax = fig(5.6, 2.6)
    prix = ["100,04", "100,02", "100,00", "99,98"]
    qte = [300, 500, 400, 1000]
    cols = [ORANGE, ORANGE, BLEU, BLEU]
    ax.barh(range(4), qte, color=cols, height=0.62)
    ax.set_yticks(range(4), prix)
    ax.invert_yaxis()
    for i, q in enumerate(qte):
        ax.text(q + 20, i, f"{q} titres", va="center", color=ENCRE2)
    ax.axhline(1.5, color=GRIS, ls="--", lw=1)
    ax.text(820, 1.5, "spread 0,02", va="center", ha="left", color=ENCRE2, backgroundcolor="white")
    ax.text(5, -0.75, "Vendeurs (ask)", color=ORANGE, weight="semibold")
    ax.text(5, 3.75, "Acheteurs (bid)", color=BLEU, weight="semibold", va="top")
    ax.set_xlim(0, 1250)
    ax.set_xlabel("Quantité disponible")
    ax.grid(axis="y", visible=False)
    save(f, "carnet")


def couts_frequence():
    f, ax = fig(6.0, 2.6)
    ar = np.arange(1, 101)  # allers-retours par mois
    for cout, c, lab in [(0.0005, VERT, "0,05 % par aller-retour"), (0.001, BLEU, "0,10 %"), (0.002, ORANGE, "0,20 %")]:
        ax.plot(ar, ar * 12 * cout, color=c, label=lab)
    ax.axvline(6, color=GRIS, lw=1, ls=":")
    ax.text(7, 1.6, "swing : ~6 / mois", color=ENCRE2)
    ax.axvline(84, color=GRIS, lw=1, ls=":")
    ax.text(62, 1.6, "day : ~84 / mois", color=ENCRE2)
    pct(ax)
    ax.set_xlabel("Allers-retours par mois")
    ax.set_ylabel("Coût annuel (% de la position)")
    ax.legend(loc="upper left")
    save(f, "couts_frequence")


def systeme_tendance():
    df = data.synthetic_ohlcv(n_days=700, seed=11, drift=0.25)
    d = df.iloc[-260:]
    c = df["close"]
    mm200 = ind.sma(c, 200).loc[d.index]
    dch = ind.donchian(df, 20).loc[d.index]
    dcl = ind.donchian(df, 10).loc[d.index]
    f, ax = fig(6.6, 3.0)
    ax.plot(d.index, d["close"], color=ENCRE, lw=1.2, label="Clôture")
    ax.plot(d.index, mm200, color=ORANGE, label="Moyenne 200 jours")
    ax.plot(d.index, dch["haut"], color=BLEU, lw=1, ls="--", label="Plus haut 20 jours")
    ax.plot(d.index, dcl["bas"], color=VIOLET, lw=1, ls=":", label="Plus bas 10 jours")
    entree = (d["close"] > dch["haut"]) & (d["close"] > mm200)
    premier = entree & ~entree.shift(1, fill_value=False)
    ax.scatter(d.index[premier], d["close"][premier], color=VERT, s=34, zorder=5, label="Signal d'achat",
               edgecolor="white", linewidth=1.2)
    ax.legend(ncol=3, loc="upper left", fontsize=8)
    ax.set_ylabel("Prix")
    save(f, "systeme_tendance")


def rsi_fig():
    df = data.synthetic_ohlcv(n_days=400, seed=1)
    d = df.iloc[-200:]
    r = ind.rsi(df["close"]).loc[d.index]
    f, (a1, a2) = plt.subplots(2, 1, figsize=(6.4, 3.4), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    a1.plot(d.index, d["close"], color=ENCRE, lw=1.2)
    a1.set_ylabel("Prix")
    a2.plot(d.index, r, color=VIOLET, lw=1.3)
    a2.axhspan(70, 100, color=ORANGE, alpha=0.08)
    a2.axhspan(0, 30, color=BLEU, alpha=0.08)
    a2.axhline(70, color=ORANGE, lw=0.8)
    a2.axhline(30, color=BLEU, lw=0.8)
    a2.set_ylim(0, 100)
    a2.set_ylabel("RSI(14)")
    save(f, "rsi")


def recuperation():
    f, ax = fig(5.6, 2.6)
    p = np.linspace(0.01, 0.8, 200)
    ax.plot(p, 1 / (1 - p) - 1, color=ROUGE)
    for x in (0.1, 0.25, 0.5):
        y = 1 / (1 - x) - 1
        ax.scatter([x], [y], color=ROUGE, s=30, zorder=5, edgecolor="white")
        ax.annotate(f"−{x:.0%} → +{y:.0%}", (x, y), xytext=(6, 6), textcoords="offset points", color=ENCRE2)
    pct(ax)
    pct(ax, "x")
    ax.set_xlabel("Perte subie")
    ax.set_ylabel("Gain nécessaire pour revenir")
    ax.set_ylim(0, 4)
    save(f, "recuperation")


def monte_carlo():
    f, axs = plt.subplots(1, 2, figsize=(6.8, 2.8), sharey=False)
    for ax, risque, titre in [(axs[0], 0.01, "Risque 1 % par trade"), (axs[1], 0.05, "Risque 5 % par trade")]:
        eq = simulate_equity(0.40, 2.0, risque, n_trades=200, n_paths=2000, seed=3)
        x = np.arange(eq.shape[1])
        lo, med, hi = np.percentile(eq, [5, 50, 95], axis=0)
        ax.fill_between(x, lo, hi, color=BLEU, alpha=0.15, lw=0, label="90 % des cas")
        for i in range(12):
            ax.plot(x, eq[i], color=BLEU, lw=0.5, alpha=0.35)
        ax.plot(x, med, color=BLEU, lw=2, label="médiane")
        ax.axhline(1, color=GRIS, lw=0.8)
        dd = np.median(max_drawdowns(eq))
        ax.set_title(f"{titre} · baisse médiane {dd:.0%}")
        ax.set_xlabel("Trades")
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}×"))
    axs[0].set_ylabel("Capital (× départ)")
    axs[0].legend(loc="upper left", fontsize=8)
    save(f, "monte_carlo")


def esperance():
    f, ax = fig(5.6, 2.8)
    p = np.linspace(0.15, 0.8, 200)
    ax.plot(p, (1 - p) / p, color=ENCRE, lw=1.6)
    ax.fill_between(p, (1 - p) / p, 6, color=VERT, alpha=0.10, lw=0)
    ax.fill_between(p, 0, (1 - p) / p, color=ROUGE, alpha=0.08, lw=0)
    ax.text(0.55, 3.3, "espérance positive", color=VERT, weight="semibold")
    ax.text(0.2, 0.6, "espérance négative", color=ROUGE, weight="semibold")
    pts = [(0.43, 1.48 / 0.70, "poche swing (réel)"), (0.42, 0.41 / 0.53, "poche day (réel)")]
    for x, y, lab in pts:
        ax.scatter([x], [y], color=BLEU, s=34, zorder=5, edgecolor="white")
        ax.annotate(lab, (x, y), xytext=(6, 4), textcoords="offset points", color=ENCRE2)
    pct(ax, "x")
    ax.set_ylim(0, 6)
    ax.set_xlabel("Taux de réussite")
    ax.set_ylabel("Gain moyen / perte moyenne")
    save(f, "esperance")


def walk_forward():
    f, ax = fig(6.4, 2.4)
    for i in range(6):
        ax.barh(i, 3, left=i, color=BLEU, height=0.55)
        ax.barh(i, 1, left=i + 3, color=ORANGE, height=0.55)
    ax.set_yticks(range(6), [f"étape {i + 1}" for i in range(6)])
    ax.invert_yaxis()
    ax.set_xticks(range(0, 10), [str(2015 + i) for i in range(10)])
    ax.barh(7, 6, left=3, color=ORANGE, height=0.55)
    ax.set_yticks(list(range(6)) + [7], [f"étape {i + 1}" for i in range(6)] + ["résultat"])
    ax.text(0.05, 6.6, "■ entraînement (choix des paramètres)", color=BLEU, fontsize=8)
    ax.text(4.6, 6.6, "■ test (hors échantillon), mis bout à bout", color=ORANGE, fontsize=8)
    ax.grid(axis="y", visible=False)
    save(f, "walk_forward")


def ic_sharpe():
    f, ax = fig(5.6, 2.6)
    ans = np.linspace(1, 30, 200)
    ax.fill_between(ans, 0.8 - 1.96 / np.sqrt(ans), 0.8 + 1.96 / np.sqrt(ans), color=BLEU, alpha=0.15, lw=0)
    ax.plot(ans, np.full_like(ans, 0.8), color=BLEU)
    ax.axhline(0, color=ROUGE, lw=1)
    ax.axvline(6.0, color=GRIS, ls=":")
    ax.text(6.4, 2.0, "6 ans : l'intervalle\nne quitte pas encore 0", color=ENCRE2, fontsize=8)
    ax.set_xlabel("Années de données")
    ax.set_ylabel("Sharpe estimé 0,8 : IC 95 %")
    save(f, "ic_sharpe")


def these_vol():
    f, ax = fig(5.8, 2.5)
    noms = ["Empirique", "Ledoit-Wolf", "Non linéaire"]
    v60 = [0.2294, 0.1252, 0.1278]
    v120 = [0.1409, 0.1218, 0.1210]
    x = np.arange(3)
    ax.bar(x - 0.18, v60, 0.34, color=BLEU, label="fenêtre 60 mois")
    ax.bar(x + 0.18, v120, 0.34, color=ORANGE, label="fenêtre 120 mois")
    for i in range(3):
        ax.text(i - 0.18, v60[i] + 0.004, f"{v60[i]:.1%}", ha="center", fontsize=8, color=ENCRE2)
        ax.text(i + 0.18, v120[i] + 0.004, f"{v120[i]:.1%}", ha="center", fontsize=8, color=ENCRE2)
    ax.set_xticks(x, noms)
    pct(ax)
    ax.set_ylabel("Volatilité hors échantillon")
    ax.legend()
    ax.grid(axis="x", visible=False)
    save(f, "these_vol")


def parite_risque():
    f, ax = fig(5.6, 2.3)
    cats = ["60/40 (poids)", "60/40 (risque)", "Parité (poids)", "Parité (risque)"]
    act = [0.60, 0.91, 0.29, 0.50]
    ax.barh(range(4), act, color=BLEU, height=0.55, label="actions")
    ax.barh(range(4), [1 - a for a in act], left=act, color=VERT, height=0.55, label="obligations")
    for i, a in enumerate(act):
        ax.text(a / 2, i, f"{a:.0%}", color="white", ha="center", va="center", weight="semibold")
        ax.text(a + (1 - a) / 2, i, f"{1 - a:.0%}", color="white", ha="center", va="center", weight="semibold")
    ax.set_yticks(range(4), cats)
    ax.invert_yaxis()
    pct(ax, "x")
    ax.legend(ncol=2, loc="lower right", bbox_to_anchor=(1, 1.0))
    ax.grid(visible=False)
    save(f, "parite_risque")


def martingale():
    f, ax = fig(6.0, 2.6)
    n = np.arange(0, 11)
    or1 = 10_000 * 0.99 ** n
    mart = 10_000 - 10 * (2 ** n - 1)
    ax.plot(n, or1, color=BLEU, marker="o", ms=4, label="Or-1 : 1 % du capital par trade")
    ax.plot(n, np.maximum(mart, -500), color=ROUGE, marker="o", ms=4, label="Martingale : mise doublée après chaque perte")
    ax.axhline(0, color=GRIS, lw=0.8)
    ax.set_xlabel("Pertes consécutives")
    ax.set_ylabel("Capital (€)")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", " ")))
    ax.legend(loc="lower left")
    save(f, "martingale")


def serie_pertes():
    def proba(n_trades, longueur, p):
        etat = np.zeros(longueur)
        etat[0] = 1
        out = []
        for _ in range(n_trades):
            nv = np.zeros(longueur)
            nv[0] = etat.sum() * (1 - p)
            nv[1:] = etat[:-1] * p
            etat = nv
            out.append(1 - etat.sum())
        return np.array(out)
    f, ax = fig(5.8, 2.6)
    x = np.arange(1, 3001)
    for L, c in [(6, ORANGE), (8, BLEU), (10, VIOLET)]:
        ax.plot(x, proba(3000, L, 0.4), color=c, label=f"au moins {L} pertes de suite")
    pct(ax)
    ax.set_xlabel("Nombre de trades (60 % de trades gagnants)")
    ax.set_ylabel("Probabilité")
    ax.legend(loc="lower right")
    save(f, "serie_pertes")


def courbes_poches():
    f, ax = fig(6.6, 2.9)
    for nom, c in [("swing", BLEU), ("long_terme", VERT), ("day", ORANGE)]:
        e = json.loads((RACINE / "suivi" / "etat" / f"{nom}.json").read_text())
        s = pd.Series([v for _, v in e["historique"]], index=pd.to_datetime([d for d, _ in e["historique"]]))
        s = s.groupby(s.index.normalize()).last()
        ax.plot(s.index, s / s.iloc[0] - 1, color=c, label=nom.replace("_", " "))
    ax.axhline(0, color=GRIS, lw=0.8)
    pct(ax)
    ax.set_ylabel("Performance depuis le départ")
    ax.legend(loc="upper left")
    save(f, "courbes_poches")


def drawdown_poche():
    e = json.loads((RACINE / "suivi" / "etat" / "swing.json").read_text())
    s = pd.Series([v for _, v in e["historique"]], index=pd.to_datetime([d for d, _ in e["historique"]]))
    dd = s / s.cummax() - 1
    f, ax = fig(6.6, 2.2)
    ax.fill_between(dd.index, dd, 0, color=ROUGE, alpha=0.25, lw=0)
    ax.plot(dd.index, dd, color=ROUGE, lw=1)
    pct(ax)
    ax.set_ylabel("Baisse depuis le plus haut")
    save(f, "drawdown_swing")


def r_trades():
    e = json.loads((RACINE / "suivi" / "etat" / "swing.json").read_text())
    t = pd.DataFrame(e["courtier"]["trades"])
    r = (t["sortie"] - t["entree"]) / (t["entree"] - t["stop"])
    f, ax = fig(6.0, 2.5)
    bins = np.arange(-2, 6.5, 0.5)
    n, b, patches = ax.hist(r.clip(-2, 6), bins=bins, color=BLEU, edgecolor="white", linewidth=1.5)
    for p, g in zip(patches, b[:-1]):
        if g < 0:
            p.set_facecolor(ROUGE)
    ax.axvline(r.mean(), color=ENCRE, ls="--", lw=1)
    ax.text(r.mean() + 0.1, max(n) * 0.9, f"moyenne {r.mean():+.2f} R", color=ENCRE2)
    ax.set_xlabel("Résultat du trade en R (poche swing, 227 trades, 2021-2026)")
    ax.set_ylabel("Trades")
    ax.grid(axis="x", visible=False)
    save(f, "r_trades")


def range_ouverture():
    rng = np.random.default_rng(4)
    t = pd.date_range("2026-10-23 09:30", periods=78, freq="5min")
    r = rng.normal(0, 0.0018, 78)
    r[8:20] += 0.0012
    close = 100 * np.exp(np.cumsum(r))
    high = close * (1 + np.abs(rng.normal(0, 0.0008, 78)))
    low = close * (1 - np.abs(rng.normal(0, 0.0008, 78)))
    vwap = np.cumsum(close) / np.arange(1, 79)
    oh, ol = high[:6].max(), low[:6].min()
    f, ax = fig(6.4, 2.8)
    ax.axvspan(t[0], t[5], color=JAUNE, alpha=0.12, lw=0)
    ax.text(t[0], oh + 0.25, "30 premières minutes", color=ENCRE2, fontsize=8)
    ax.plot(t, close, color=ENCRE, lw=1.2, label="Prix (5 min)")
    ax.plot(t, vwap, color=VIOLET, lw=1.2, label="VWAP")
    ax.hlines([oh, ol], t[0], t[-1], colors=[BLEU, ORANGE], linestyles="--", lw=1)
    ax.text(t[-1], oh, " haut du range", va="center", color=BLEU, fontsize=8)
    ax.text(t[-1], ol, " bas = stop", va="center", color=ORANGE, fontsize=8)
    k = next(i for i in range(6, 78) if close[i] > oh and close[i] > vwap[i])
    ax.scatter([t[k]], [close[k]], color=VERT, s=40, zorder=5, edgecolor="white", label="Entrée")
    obj = close[k] + 2 * (close[k] - ol)
    ax.hlines(obj, t[k], t[-1], colors=VERT, linestyles=":", lw=1)
    ax.text(t[-1], obj, " objectif 2R", va="center", color=VERT, fontsize=8)
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M"))
    ax.legend(loc="lower left", fontsize=8)
    ax.set_xlabel("Heure de New York (15 h 30 à 22 h 00 à Berlin)")
    save(f, "range_ouverture")


if __name__ == "__main__":
    SORTIE.mkdir(parents=True, exist_ok=True)
    for fn in [carnet, couts_frequence, systeme_tendance, rsi_fig, recuperation, monte_carlo, esperance,
               walk_forward, ic_sharpe, these_vol, parite_risque, martingale, serie_pertes, courbes_poches,
               drawdown_poche, r_trades, range_ouverture]:
        fn()
    print(f"{len(list(SORTIE.glob('*.svg')))} figures dans {SORTIE}")
