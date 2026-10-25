from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tradeskills import data, fundamentals, indicators as ind, optim, portfolio, report, signals, validation

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def ohlcv():
    return data.synthetic_ohlcv(n_days=600, seed=3)


@pytest.fixture(scope="module")
def industries48():
    return data.load_french_csv(ROOT / "data" / "48_Industry_Portfolios.csv", start=196901)


def test_synthetic_ohlcv_is_consistent(ohlcv):
    assert (ohlcv["high"] >= ohlcv[["open", "close"]].max(axis=1)).all()
    assert (ohlcv["low"] <= ohlcv[["open", "close"]].min(axis=1)).all()


def test_ema_and_rsi_known_values():
    c = pd.Series([10, 11, 12, 11, 13], dtype=float)
    assert ind.ema(c, 3).tolist() == pytest.approx([10, 10.5, 11.25, 11.125, 12.0625])
    up = pd.Series(np.arange(1, 50, dtype=float))
    assert ind.rsi(up).iloc[-1] == pytest.approx(100)


def test_indicators_only_use_the_past(ohlcv):
    full = ind.atr(ohlcv)
    cut = ind.atr(ohlcv.iloc[:300])
    assert full.iloc[:300].to_numpy() == pytest.approx(cut.to_numpy(), nan_ok=True)
    don = ind.donchian(ohlcv)
    assert don["haut"].iloc[25] == ohlcv["high"].iloc[5:25].max()


def test_vwap_resets_each_day():
    idx = pd.to_datetime(["2026-01-05 09:00", "2026-01-05 10:00", "2026-01-06 09:00"])
    df = pd.DataFrame({"high": [11, 13, 21], "low": [9, 11, 19], "close": [10, 12, 20], "volume": [1, 3, 5]}, index=idx)
    assert ind.vwap(df).tolist() == pytest.approx([10, 11.5, 20])


def test_backtest_signal_has_no_lookahead(ohlcv):
    close = ohlcv["close"]
    cheat = (close.pct_change() > 0).astype(int)  # signal connu seulement à la clôture
    r = signals.backtest_signal(close, cheat, cost_bps=0)
    # appliqué le lendemain, il ne capte pas le rendement du jour qui l'a déclenché
    assert r.mean() < close.pct_change().clip(lower=0).mean() / 2


def test_walk_forward_uses_only_test_windows(ohlcv):
    close = ohlcv["close"]
    run = lambda n: signals.backtest_signal(close, (close > ind.sma(close, n)).astype(int))
    oos, params = validation.walk_forward(run, {"n": [10, 50]}, close.index, train=200, test=100)
    assert len(oos) == 400 and oos.index[0] == close.index[200]
    assert set(params["n"]) <= {10, 50}


def test_sharpe_diff_test(ohlcv):
    r = ohlcv["close"].pct_change().dropna()
    z, p = validation.sharpe_diff_test(r, r * 2)  # même Sharpe
    assert z == pytest.approx(0) and p == pytest.approx(1)
    worse = r - 0.002  # même risque, moins de rendement
    z, p = validation.sharpe_diff_test(r, worse)
    assert z > 0 and p < 0.05


def test_deflated_sharpe_decreases_with_trials(ohlcv):
    r = ohlcv["close"].pct_change().dropna()
    assert validation.deflated_sharpe(r, 100, 1e-3) < validation.deflated_sharpe(r, 2, 1e-3)


def test_nonlinear_shrinkage_beats_empirical(industries48):
    r_emp, _ = portfolio.rolling_backtest(industries48.iloc[-300:], 60, portfolio.cov_empirical)
    r_nl, _ = portfolio.rolling_backtest(industries48.iloc[-300:], 60, optim.cov_nonlinear_shrinkage)
    assert r_nl.std() < r_emp.std()
    S = optim.cov_nonlinear_shrinkage(industries48.to_numpy()[-60:])
    assert np.allclose(S, S.T) and np.linalg.eigvalsh(S).min() > 0


def test_risk_parity_equalizes_contributions():
    rng = np.random.default_rng(0)
    A = rng.normal(size=(6, 6))
    S = A @ A.T + np.eye(6)
    w = optim.risk_parity(S)
    assert w.sum() == pytest.approx(1) and (w > 0).all()
    assert optim.risk_contributions(w, S) == pytest.approx(np.full(6, 1 / 6), abs=1e-8)


def test_long_only_and_cap(industries48):
    S = np.cov(industries48.to_numpy()[-120:], rowvar=False)
    w = optim.gmv_long_only(S, max_weight=0.1)
    assert w.min() >= -1e-9 and w.max() <= 0.1 + 1e-9 and w.sum() == pytest.approx(1)


def test_black_litterman_view_equal_to_equilibrium_changes_nothing():
    S = np.array([[0.04, 0.01], [0.01, 0.09]])
    w = np.array([0.5, 0.5])
    pi = 2.5 * S @ w
    P = np.array([[1.0, -1.0]])
    mu = optim.black_litterman(S, w, P, P @ pi)
    assert mu == pytest.approx(pi)


def test_min_cvar_is_not_worse_than_equal_weights(industries48):
    X = industries48.to_numpy()[-120:, :8]
    w = optim.min_cvar(X)
    assert optim.cvar(X @ w) <= optim.cvar(X @ (np.ones(8) / 8)) + 1e-12


def test_brinson_sums_to_active_return():
    seg = ["a", "b", "c"]
    wp, wb = pd.Series([0.5, 0.3, 0.2], seg), pd.Series([0.4, 0.4, 0.2], seg)
    rp, rb = pd.Series([0.1, 0.02, -0.03], seg), pd.Series([0.08, 0.03, -0.01], seg)
    assert report.brinson(wp, wb, rp, rb)["total"].sum() == pytest.approx((wp * rp).sum() - (wb * rb).sum())


def test_alpha_beta_recovers_parameters():
    rng = np.random.default_rng(1)
    b = pd.Series(rng.normal(0.01, 0.04, 2_000))
    r = 0.002 + 0.7 * b + pd.Series(rng.normal(0, 0.01, 2_000))
    ab = report.alpha_beta(r, b)
    assert ab["beta"] == pytest.approx(0.7, abs=0.02)
    assert ab["alpha_annuel"] == pytest.approx(0.024, abs=0.006)


def test_write_report(tmp_path):
    R = data.load_french_csv(ROOT / "data" / "10_Industry_Portfolios.csv", start=200001)
    r, _ = portfolio.rolling_backtest(R, 60, portfolio.cov_ledoit_wolf)
    b, _ = portfolio.rolling_backtest(R, 60, None)
    md = report.write_report(r, b, tmp_path / "rapport.md")
    assert "Information ratio" in md.read_text() and md.with_suffix(".png").exists()


def test_dcf_matches_closed_form_without_growth_phase():
    # sans phase de croissance, la valeur est la rente de Gordon-Shapiro
    assert fundamentals.dcf(100, 0.0, 1, 0.10, 0.0) == pytest.approx(100 / 1.1 + 100 / 0.10 / 1.1)
    with pytest.raises(ValueError):
        fundamentals.dcf(100, 0.05, 5, 0.02, 0.03)


def test_gmv_long_only_works_on_daily_scale_covariances():
    rng = np.random.default_rng(0)
    X = rng.normal(0, 0.01, (500, 4)) * np.array([0.5, 1, 1.5, 2])  # volatilités journalières différentes
    S = np.cov(X, rowvar=False)
    w = optim.gmv_long_only(S)
    assert w[0] > 0.5 and w[0] > w[1] > w[2] > w[3]
    np.testing.assert_allclose(w, optim.gmv_long_only(S * 1e4), atol=1e-4)


def test_afrique_stale_prices_hide_beta_and_dimson_recovers_it():
    from tradeskills import afrique

    rng = np.random.default_rng(0)
    marche = data.synthetic_ohlcv(1_500, seed=1)
    titre = marche.copy()
    titre["close"] = marche["close"] * np.exp(np.cumsum(rng.normal(0, 0.008, len(marche))))
    fige = afrique.cotations_figees(titre, proba_echange=1 / 3, seed=2)
    rm, rf = marche["close"].pct_change(), fige["close"].pct_change()
    assert afrique.beta_simple(rf, rm) < 0.5
    assert afrique.beta_dimson(rf, rm, 5) == pytest.approx(1, abs=0.15)
    liq = afrique.liquidite(fige)
    assert liq["jours_sans_echange"] == pytest.approx(2 / 3, abs=0.05)
    assert afrique.liquidite(titre)["jours_sans_echange"] == 0
    assert afrique.vers_eur(655_957) == pytest.approx(1_000)
    bloque = titre.copy()
    bloque.iloc[100:103, bloque.columns.get_loc("close")] = bloque["close"].iloc[99] * 1.075 ** np.arange(1, 4)
    assert afrique.jours_a_la_limite(bloque) >= 3
