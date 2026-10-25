import json

import numpy as np
import pandas as pd
import pytest

from tradeskills.agents import alertes, budget, journal_de_bord, marche, orchestre, time_machine
from tradeskills.agents.__main__ import main
from tradeskills.agents.config import Config, Poche, charger
from tradeskills.agents.courtier import CourtierPapier, Ordre
from tradeskills.agents.moteur import Moteur

SWING = Poche("swing", "swing", 10_000, ["A", "B", "C", "D"])
DAY = Poche("day", "day", 5_000, ["A", "B"], risque_par_trade=0.005, max_positions=2, poids_max=0.5)
LONG = Poche("lt", "long_terme", 20_000, ["A", "B", "C", "D", "E"], poids_max=0.35)


@pytest.fixture(scope="module")
def source():
    return marche.SourceSimulee(n_jours=700, n_jours_intraday=30, seed=1)


def barre(o, h, l, c):
    return {"open": o, "high": h, "low": l, "close": c}


def test_config_rejects_unknown_style_and_params():
    with pytest.raises(ValueError):
        Poche("x", "scalping", 1_000, ["A"])
    with pytest.raises(ValueError):
        Poche("x", "swing", 1_000, ["A"], params={"inconnu": 1})
    assert SWING.param("entree") == 20


def test_example_config_loads():
    conf = charger("agents/config.exemple.json")
    assert {p.style for p in conf.poches} == {"swing", "day", "long_terme", "signaux"}


def test_paper_broker_fills_at_next_open_with_costs_and_records_r():
    c = CourtierPapier(10_000, cout_bps=10, glissement_bps=0)
    c.passer(Ordre("A", 10, "entree", stop=95, setup="test"))
    c.executer_ouvertures("j1", {"A": barre(100, 101, 99, 100)})
    assert c.positions["A"].quantite == 10
    assert c.cash == pytest.approx(10_000 - 1_000 - 1.0)
    # Gap sous le stop : sortie à l'ouverture (90), pas au stop (95)
    c.verifier_stops("j2", {"A": barre(90, 91, 89, 90)})
    assert "A" not in c.positions
    t = c.trades[0]
    assert t["sortie"] == 90 and t["stop"] == 95
    assert (t["sortie"] - t["entree"]) / (t["entree"] - t["stop"]) == pytest.approx(-2.0)


def test_paper_broker_cancels_entry_on_gap_below_stop():
    c = CourtierPapier(10_000)
    c.passer(Ordre("A", 10, "entree", stop=95))
    c.executer_ouvertures("j1", {"A": barre(94, 96, 93, 95)})
    assert not c.positions and c.mouvements[-1]["motif"] == "annule_gap"


def test_paper_broker_caps_risk_when_open_gaps_up():
    c = CourtierPapier(100_000, glissement_bps=0)
    c.passer(Ordre("A", 50, "entree", stop=98, risque_max=100))  # prévu : 50 x (100 - 98)
    c.executer_ouvertures("j1", {"A": barre(102, 103, 101, 102)})
    assert c.positions["A"].quantite == 25  # 100 / (102 - 98)


def test_paper_broker_never_spends_more_than_cash():
    c = CourtierPapier(1_000)
    c.passer(Ordre("A", 50, "entree", stop=90))
    c.executer_ouvertures("j1", {"A": barre(100, 101, 99, 100)})
    assert c.positions["A"].quantite == 9
    assert c.cash >= 0


def test_target_weights_respect_cap(source):
    closes = pd.DataFrame({s: df["close"] for s, df in source.historique(LONG.univers, "long_terme").items()})
    w = budget.poids_cibles(closes.pct_change().dropna().tail(252), LONG)
    assert w.sum() == pytest.approx(1)
    assert (w >= -1e-9).all() and (w <= 0.35 + 1e-9).all()


@pytest.mark.parametrize("poche", [SWING, DAY, LONG], ids=lambda p: p.style)
def test_no_look_ahead(poche, source):
    """Couper l'historique à une date ne change rien à ce qui s'est passé avant."""
    donnees = source.historique(poche.univers, poche.style)
    complet = time_machine.rejouer(poche, donnees).courbe
    coupure = complet.index[len(complet) * 2 // 3]
    tronque = time_machine.rejouer(poche, {s: df.loc[:coupure] for s, df in donnees.items()}).courbe
    pd.testing.assert_series_equal(complet.loc[:coupure], tronque)


@pytest.mark.parametrize("poche", [SWING, DAY, LONG], ids=lambda p: p.style)
def test_daily_resume_from_saved_state_equals_backtest(poche, source):
    """Le suivi quotidien (reprise depuis l'état JSON) donne exactement le backtest."""
    donnees = source.historique(poche.univers, poche.style)
    complet = time_machine.rejouer(poche, donnees)
    coupure = complet.courbe.index[len(complet.courbe) // 2]

    m1 = Moteur(poche)
    m1.charger({s: df.loc[:coupure] for s, df in donnees.items()})
    m1.executer()
    etat = json.loads(json.dumps(m1.etat(), default=float))
    m2 = Moteur(poche, etat)
    m2.charger(donnees)
    m2.executer()
    pd.testing.assert_series_equal(m2.courbe(), complet.courbe)
    assert m2.courtier.trades == complet.moteur.courtier.trades


def test_swing_trades_and_risk_limits(source):
    res = time_machine.rejouer(SWING, source.historique(SWING.univers, "swing"))
    assert len(res.trades) > 0
    assert (res.trades["stop"] < res.trades["entree"]).all()
    # Perte prévue au stop initial <= 1 % de la valeur de la poche, même si l'ouverture a monté
    risque = (res.trades["entree"] - res.trades["stop"]) * res.trades["quantite"]
    assert (risque <= 0.01 * res.courbe.max() + 1e-9).all()


def test_day_positions_are_closed_every_evening(source):
    res = time_machine.rejouer(DAY, source.historique(DAY.univers, "day"))
    assert len(res.trades) > 0
    assert (pd.to_datetime(res.trades["date_sortie"]).dt.normalize() == pd.to_datetime(res.trades["date"])).all()
    assert not res.moteur.courtier.positions


def test_circuit_breaker_blocks_entries():
    poche = Poche("p", "swing", 10_000, ["A"], drawdown_max=0.1)
    m = Moteur(poche)
    m.plus_haut = 20_000
    assert m._drawdown(pd.Timestamp("2024-01-01"), 10_000) == pytest.approx(-0.5)
    assert m._drawdown(pd.Timestamp("2024-01-05"), 10_000) == pytest.approx(-0.5)
    assert m._drawdown(pd.Timestamp("2024-01-20"), 10_000) == 0.0  # pause finie : on repart d'ici


def test_journal_bilan_and_file(tmp_path):
    trades = [
        {"date": "2024-01-02", "actif": "A", "sens": "achat", "setup": "s", "entree": 100, "stop": 95,
         "sortie": 110, "quantite": 10, "frais": 1, "note": "objectif", "date_sortie": "2024-01-05"},
        {"date": "2024-01-08", "actif": "B", "sens": "achat", "setup": "s", "entree": 50, "stop": 48,
         "sortie": 48, "quantite": 10, "frais": 1, "note": "stop", "date_sortie": "2024-01-09"},
    ]
    texte = journal_de_bord.bilan(trades)
    assert "Espérance : 0.50 R" in texte and "Moins de 30 trades" in texte
    chemin = tmp_path / "j.csv"
    journal_de_bord.enregistrer(trades[:1], chemin)
    journal_de_bord.enregistrer(trades[1:], chemin)
    assert len(pd.read_csv(chemin)) == 2


def test_alert_format():
    msg = alertes.formater("swing", {"symbole": "SPY", "quantite": 10, "prix": 500.0, "stop": 490.0, "motif": "entree"})
    assert msg == "🟢 [swing] ACHAT 10 SPY à 500.00, stop 490.00 (entree)"
    assert alertes.envoyer([msg], token=None, chat_id=None) is False


def test_daily_run_twice_is_idempotent(tmp_path, source):
    conf = Config([SWING, LONG])
    orchestre.passage(conf, source, tmp_path, envoyer=False)
    etat1 = (tmp_path / "etat" / "swing.json").read_text()
    rapport = orchestre.passage(conf, source, tmp_path, envoyer=False)
    assert (tmp_path / "etat" / "swing.json").read_text() == etat1
    assert "Nouvelles exécutions depuis le dernier passage : 0." in rapport


def test_cli_backtest(tmp_path, capsys):
    main(["backtest", "--config", "agents/config.exemple.json", "--poche", "long_terme", "--dossier", str(tmp_path)])
    assert "Time Machine · long_terme" in capsys.readouterr().out
    assert (tmp_path / "rapports" / "backtest.md").exists()
