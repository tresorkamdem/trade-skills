from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tradeskills import data, journal, metrics, portfolio, risk

ROOT = Path(__file__).resolve().parents[1]


def test_french_loader_returns_decimal_monthly_returns():
    R = data.load_french_csv(ROOT / "data" / "10_Industry_Portfolios.csv")
    assert R.shape[1] == 10
    assert str(R.index[0]) == "1926-07"
    assert R.iloc[0]["NoDur"] == pytest.approx(0.0144)
    assert not R.isna().any().any()
    assert R.index.is_monotonic_increasing


def test_gmv_weights_sum_to_one_and_minimize_variance():
    rng = np.random.default_rng(0)
    A = rng.normal(size=(5, 5))
    sigma = A @ A.T + 5 * np.eye(5)
    w = portfolio.gmv_weights(sigma)
    assert w.sum() == pytest.approx(1.0)
    eq = np.ones(5) / 5
    assert w @ sigma @ w <= eq @ sigma @ eq


def test_shrinkage_beats_empirical_out_of_sample():
    # Résultat central de la thèse, sur le fichier à 10 secteurs depuis 1969
    R = data.load_french_csv(ROOT / "data" / "10_Industry_Portfolios.csv", start=196901)
    table = portfolio.compare(R, window=60)
    assert table.loc["Ledoit-Wolf", "vol_annuelle"] < table.loc["Empirique", "vol_annuelle"]
    assert table.loc["Ledoit-Wolf", "turnover"] < table.loc["Empirique", "turnover"]
    assert table.loc["1/n", "turnover"] == pytest.approx(0.0)


def test_costs_reduce_returns():
    R = data.load_french_csv(ROOT / "data" / "10_Industry_Portfolios.csv", start=200001)
    gross, _ = portfolio.rolling_backtest(R, 60, portfolio.cov_empirical)
    net, _ = portfolio.rolling_backtest(R, 60, portfolio.cov_empirical, cost_bps=20)
    assert net.sum() < gross.sum()


def test_metrics_on_known_series():
    r = pd.Series([0.10, -0.50, 0.20])
    assert metrics.max_drawdown(r) == pytest.approx(-0.5)
    assert metrics.annualized_return(pd.Series([0.01] * 12)) == pytest.approx(1.01**12 - 1)


def test_risk_tools():
    assert risk.position_size(10_000, 0.01, 50, 48) == 50
    assert risk.r_multiple(50, 48, 54) == pytest.approx(2.0)
    assert risk.r_multiple(100, 105, 90) == pytest.approx(2.0)  # vente à découvert
    assert risk.kelly_fraction(0.5, 2.0) == pytest.approx(0.25)
    assert risk.expectancy(0.4, 2.0) == pytest.approx(0.2)
    with pytest.raises(ValueError):
        risk.position_size(10_000, 0.01, 50, 50)


def test_journal_example():
    df = journal.load(ROOT / "journal" / "modele_journal.csv")
    s = journal.stats(df)
    assert s["trades"] == 4
    assert df["r"].iloc[0] == pytest.approx(2.0)
    assert df["r"].iloc[2] == pytest.approx(2.0)
    assert df["pnl"].iloc[2] == pytest.approx(118.0)
