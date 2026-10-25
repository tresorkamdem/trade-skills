"""Mesure de performance relative et rapport client (module 09)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from . import metrics


def alpha_beta(r: pd.Series, bench: pd.Series, rf: float = 0.0, periods: int = 12) -> dict[str, float]:
    """Régression CAPM des rendements excédentaires : r − rf = α + β (b − rf) + ε.

    α est annualisé ; la t-stat dit si α est significativement différent de zéro.
    """
    y = (r - rf / periods).to_numpy()
    x = (bench - rf / periods).to_numpy()
    X = np.column_stack([np.ones_like(x), x])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ coef
    s2 = resid @ resid / (len(y) - 2)
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    return {
        "alpha_annuel": coef[0] * periods,
        "t_alpha": coef[0] / se[0],
        "beta": coef[1],
        "r2": 1 - resid.var() / y.var(),
    }


def tracking_error(r: pd.Series, bench: pd.Series, periods: int = 12) -> float:
    return (r - bench).std(ddof=1) * np.sqrt(periods)


def information_ratio(r: pd.Series, bench: pd.Series, periods: int = 12) -> float:
    """Surperformance annualisée par unité de tracking error."""
    return (r - bench).mean() * periods / tracking_error(r, bench, periods)


def brinson(w_p: pd.Series, w_b: pd.Series, r_p: pd.Series, r_b: pd.Series) -> pd.DataFrame:
    """Attribution de Brinson-Fachler sur une période, par segment (secteur, classe d'actifs).

    allocation = (w_p − w_b)(r_b,i − R_b) ; sélection = w_b (r_p,i − r_b,i) ;
    interaction = (w_p − w_b)(r_p,i − r_b,i). La somme égale R_p − R_b.
    """
    Rb = (w_b * r_b).sum()
    out = pd.DataFrame({
        "allocation": (w_p - w_b) * (r_b - Rb),
        "selection": w_b * (r_p - r_b),
        "interaction": (w_p - w_b) * (r_p - r_b),
    })
    out["total"] = out.sum(axis=1)
    return out


def monthly_table(r: pd.Series) -> pd.DataFrame:
    """Tableau année x mois des rendements, avec le total de l'année (format des rapports de fonds)."""
    idx = r.index.to_timestamp() if isinstance(r.index, pd.PeriodIndex) else r.index
    s = pd.Series(r.to_numpy(), index=idx)
    tab = s.groupby([s.index.year, s.index.month]).apply(lambda x: (1 + x).prod() - 1).unstack()
    tab.columns = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"][: tab.shape[1]]
    tab["Année"] = s.groupby(s.index.year).apply(lambda x: (1 + x).prod() - 1)
    return tab


def _markdown_table(df: pd.DataFrame) -> str:
    head = "| | " + " | ".join(map(str, df.columns)) + " |"
    sep = "| --- " * (df.shape[1] + 1) + "|"
    body = [
        f"| {i} | " + " | ".join("" if pd.isna(v) else f"{v:.1f}" for v in row) + " |"
        for i, row in zip(df.index, df.to_numpy())
    ]
    return "\n".join([head, sep, *body])


def write_report(
    r: pd.Series, bench: pd.Series, path: str | Path, title: str = "Rapport de performance", periods: int = 12
) -> Path:
    """Écrit un rapport Markdown avec graphique (courbe de capital et drawdown) à côté.

    Renvoie le chemin du fichier .md. Le graphique est `<nom>.png` dans le même dossier.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    idx = r.index.to_timestamp() if isinstance(r.index, pd.PeriodIndex) else r.index

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    ax1.plot(idx, (1 + r).cumprod().to_numpy(), label="Portefeuille", color="#1f4e79")
    ax1.plot(idx, (1 + bench).cumprod().to_numpy(), label="Référence", color="#a6a6a6")
    ax1.set_yscale("log")
    ax1.set_ylabel("Valeur de 1 EUR")
    ax1.legend()
    ax2.fill_between(idx, metrics.drawdown(r).to_numpy(), 0, color="#c00000", alpha=0.4)
    ax2.set_ylabel("Drawdown")
    fig.tight_layout()
    png = path.with_suffix(".png")
    fig.savefig(png, dpi=120)
    plt.close(fig)

    s_p, s_b = metrics.summary(r, periods=periods), metrics.summary(bench, periods=periods)
    ab = alpha_beta(r, bench, periods=periods)
    labels = {
        "rendement_annuel": "Rendement annualisé", "vol_annuelle": "Volatilité annualisée",
        "sharpe": "Sharpe", "sortino": "Sortino", "max_drawdown": "Perte maximale", "calmar": "Calmar",
    }
    pct = {"rendement_annuel", "vol_annuelle", "max_drawdown"}
    fmt = lambda k, v: f"{v:.2%}" if k in pct else f"{v:.2f}"
    rows = "\n".join(f"| {labels[k]} | {fmt(k, s_p[k])} | {fmt(k, s_b[k])} |" for k in labels)
    last12 = monthly_table(r).tail(3)
    md = f"""# {title}

Période : {r.index[0]} à {r.index[-1]} ({len(r)} périodes)

![Courbe de capital et drawdown]({png.name})

## Synthèse

| Mesure | Portefeuille | Référence |
| --- | --- | --- |
{rows}

## Performance relative

| Mesure | Valeur |
| --- | --- |
| Alpha annualisé | {ab['alpha_annuel']:.2%} (t = {ab['t_alpha']:.2f}) |
| Bêta | {ab['beta']:.2f} |
| Tracking error | {tracking_error(r, bench, periods):.2%} |
| Information ratio | {information_ratio(r, bench, periods):.2f} |

## Rendements mensuels (3 dernières années)

{_markdown_table(last12 * 100)}

*Les performances passées ne préjugent pas des performances futures.*
"""
    path.write_text(md, encoding="utf-8")
    return path
