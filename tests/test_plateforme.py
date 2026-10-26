import json

import numpy as np
import pandas as pd
import pytest

from tradeskills import data
from tradeskills.agents import marche, signaux, tableau, time_machine
from tradeskills.agents.__main__ import main
from tradeskills.agents.config import Config, Poche
from tradeskills.agents.moteur import Moteur

AUJ = pd.Timestamp("2020-12-31")


class FausseSource:
    """Remplace Yahoo : renvoie une fenêtre glissante d'un historique simulé."""

    def __init__(self, fin: int, echecs=()):
        self.fin, self.echecs = fin, set(echecs)

    def telecharger(self, symbole, style):
        if symbole in self.echecs:
            raise ConnectionError("Yahoo indisponible")
        df = data.synthetic_ohlcv(400, seed=len(symbole))
        return df.iloc[max(0, self.fin - 100): self.fin]


def test_cache_accumulates_and_keeps_old_data_on_failure(tmp_path):
    b1 = marche.actualiser(FausseSource(200), ["AAA", "BB"], "jour", tmp_path, AUJ)
    assert [b["barres"] for b in b1] == [100, 100]
    b2 = marche.actualiser(FausseSource(250, echecs={"BB"}), ["AAA", "BB"], "jour", tmp_path, AUJ)
    assert b2[0]["barres"] == 150 and b2[0]["nouvelles"] == 50  # 100 anciennes + 50 nouvelles, pas de doublon
    assert b2[1]["erreur"] == "Yahoo indisponible" and b2[1]["barres"] == 100  # ancien cache gardé
    df = marche.SourceCSV(tmp_path).historique(["AAA"], "swing")["AAA"]
    attendu = data.synthetic_ohlcv(400, seed=3).iloc[100:250]
    np.testing.assert_allclose(df["close"].to_numpy(), attendu["close"].to_numpy())
    assert "❌ Yahoo indisponible" in marche.bilan_texte(b2)


def test_cache_source_skips_missing_symbols(tmp_path):
    marche.actualiser(FausseSource(200), ["AAA"], "jour", tmp_path, AUJ)
    assert list(marche.source(f"cache:{tmp_path}").historique(["AAA", "ZZZ"], "swing")) == ["AAA"]
    with pytest.raises(FileNotFoundError):
        marche.source(f"csv:{tmp_path}").historique(["ZZZ"], "swing")


def test_quality_checks():
    df = data.synthetic_ohlcv(300)
    assert marche.qualite(df, "swing", df.index[-1]) == []
    mauvais = df.copy()
    mauvais.iloc[10, mauvais.columns.get_loc("close")] = mauvais["high"].iloc[10] * 2
    mauvais = mauvais.drop(mauvais.index[100:120])
    pb = " | ".join(marche.qualite(mauvais, "swing", df.index[-1] + pd.Timedelta(days=30)))
    assert "incohérentes" in pb and "trou de" in pb and "vieille de 30 jours" in pb and "40 %" in pb


def test_symbol_normalisation():
    assert signaux.normaliser_symbole("XETR:SXR8") == "SXR8.DE"
    assert signaux.normaliser_symbole("nasdaq:aapl") == "AAPL"
    assert signaux.normaliser_symbole("SAP.DE") == "SAP.DE"


def ecrire_signaux(chemin, alertes):
    chemin.write_text("\n".join(json.dumps(a) for a in alertes) + "\nligne cassée\n", encoding="utf-8")


def test_load_signals_ignores_bad_lines(tmp_path):
    f = tmp_path / "s.jsonl"
    ecrire_signaux(f, [
        {"recu": "2024-03-01T22:30:00+01:00", "type": "BUY", "symbole": "XETR:SXR8", "stop": "x"},
        {"recu": "2024-03-01T10:00:00Z", "type": "sortie", "symbole": "NASDAQ:AAPL", "poche": "autre"},
        {"type": "achat"},
    ])
    df = signaux.charger(f)
    assert list(df["symbole"]) == ["AAPL", "SXR8.DE"]  # trié par heure UTC
    assert list(df["type"]) == ["sortie", "achat"] and df["stop"].isna().iloc[1]
    assert list(signaux.pour_poche(df, "tv")["symbole"]) == ["SXR8.DE"]
    assert signaux.charger(tmp_path / "absent.jsonl").empty


@pytest.fixture
def poche_signaux(tmp_path):
    f = tmp_path / "s.jsonl"
    idx = data.synthetic_ohlcv(600).index
    alertes = []
    for i in range(250, 560, 30):
        alertes.append({"recu": f"{idx[i]:%Y-%m-%d}T15:00:00Z", "type": "achat", "symbole": "XETR:AAA", "strategie": "test"})
        alertes.append({"recu": f"{idx[i + 10]:%Y-%m-%d}T15:00:00Z", "type": "sortie", "symbole": "XETR:AAA"})
    alertes.append({"recu": f"{idx[300]:%Y-%m-%d}T15:00:00Z", "type": "achat", "symbole": "XETR:ZZZ"})
    ecrire_signaux(f, alertes)
    poche = Poche("tv", "signaux", 10_000, ["AAA.DE", "BBB.DE"], params={"fichier": str(f)})
    donnees = {s: data.synthetic_ohlcv(600, seed=i) for i, s in enumerate(poche.univers)}
    return poche, donnees


def test_signal_pocket_trades_alerts_next_open(poche_signaux):
    poche, donnees = poche_signaux
    sig = signaux.de_la_poche(poche)
    res = time_machine.rejouer(poche, donnees, signaux=sig)
    trades = res.trades
    assert len(trades) == 11 and set(trades["setup"]) == {"test"}
    idx = donnees["AAA.DE"].index
    # Alerte reçue le jour i → achat à l'ouverture du jour i + 1
    assert trades["date"].iloc[0] == f"{idx[251]:%Y-%m-%d}"
    assert any(r["raison"] == "hors univers ou sans cours" for r in res.moteur.refus)
    assert all((trades["stop"] < trades["entree"]))


def test_signal_pocket_daily_resume_equals_backtest(poche_signaux):
    poche, donnees = poche_signaux
    sig = signaux.de_la_poche(poche)
    complet = time_machine.rejouer(poche, donnees, signaux=sig)
    coupure = complet.courbe.index[400]
    m1 = Moteur(poche)
    m1.charger({s: df.loc[:coupure] for s, df in donnees.items()}, sig)
    m1.executer()
    m2 = Moteur(poche, json.loads(json.dumps(m1.etat(), default=float)))
    m2.charger(donnees, sig)
    m2.executer()
    pd.testing.assert_series_equal(m2.courbe(), complet.courbe)


def test_cli_backtest_json_and_dashboard(tmp_path, poche_signaux):
    poche, _ = poche_signaux
    conf = {"poches": [
        {"nom": "lt", "style": "long_terme", "capital": 20_000, "univers": ["A", "B", "C"], "poids_max": 0.5},
        {"nom": "tv", "style": "signaux", "capital": 5_000, "univers": ["A", "B"], "params": poche.params},
    ]}
    chemin_conf = tmp_path / "conf.json"
    chemin_conf.write_text(json.dumps(conf))
    args = ["--config", str(chemin_conf), "--source", "simulee", "--dossier", str(tmp_path)]
    main(["tableau", *args])  # avant tout passage : la page s'affiche quand même
    assert "Pas encore de passage quotidien" in (tmp_path / "tableau.html").read_text()
    main(["backtest", *args])
    bt = json.loads((tmp_path / "rapports" / "backtest.json").read_text())
    assert [p["nom"] for p in bt["poches"]] == ["lt", "tv"]
    assert bt["poches"][0]["courbe"][0][1] == pytest.approx(20_000, rel=0.01)
    main(["quotidien", "--sans-alertes", *args])
    main(["tableau", *args])
    page = (tmp_path / "tableau.html").read_text()
    for texte in ["Total des poches", "Allocation · lt", "GMV Ledoit-Wolf", "Parité de risque",
                  "Time Machine · source simulee", "cours simulés", "Alertes TradingView · tv", "<svg"]:
        assert texte in page


def test_cli_actualiser_uses_yahoo_and_writes_report(tmp_path, monkeypatch):
    monkeypatch.setattr(marche.SourceYahoo, "telecharger", lambda self, s, style: FausseSource(200).telecharger(s, style))
    conf = Config([Poche("a", "swing", 1, ["X", "Y"]), Poche("b", "long_terme", 1, ["Y", "Z"])])
    monkeypatch.setattr("tradeskills.agents.config.charger", lambda chemin: conf)
    main(["actualiser", "--donnees", str(tmp_path / "cache"), "--dossier", str(tmp_path)])
    assert sorted(p.name for p in (tmp_path / "cache").iterdir()) == ["X.csv", "Y.csv", "Z.csv"]
    assert "| Y | jour | 100 | 100 |" in (tmp_path / "rapports" / "donnees.md").read_text()


def test_snapshot_is_strict_json_and_publish_calls_trading_ingest(tmp_path, monkeypatch):
    from tradeskills.agents import instantane

    conf = Config([Poche("lt", "long_terme", 20_000, ["A", "B", "C"], poids_max=0.5),
                   Poche("sw", "swing", 10_000, ["A", "B", "C", "D"])])
    src = marche.SourceSimulee(n_jours=600, seed=1)
    vide = instantane.construire(conf, tmp_path, src)
    assert [p["lancee"] for p in vide["poches"]] == [False, False] and vide["positions"] == []
    from tradeskills.agents import orchestre
    orchestre.passage(conf, src, tmp_path, envoyer=False)
    inst = instantane.construire(conf, tmp_path, src)
    texte = json.dumps(inst, allow_nan=False)  # pas de NaN ni d'infini : JSON valide pour Postgres
    assert inst["version"] == 1 and len(texte) < 1_000_000
    lt = inst["poches"][0]
    assert lt["lancee"] and lt["courbe"][-1][1] == pytest.approx(lt["valeur"], rel=1e-6)
    alloc = inst["allocation"][0]
    assert [m["nom"] for m in alloc["methodes"]] == ["actuel", "gmv_lw", "parite_risque", "egal"]
    for m in alloc["methodes"][1:]:
        assert sum(m["poids"]) == pytest.approx(1, abs=1e-3)

    envois = []

    class Reponse:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b'"0b5c0f6e-0000-0000-0000-000000000001"'

    def faux_urlopen(req, timeout):
        envois.append((req.full_url, dict(req.header_items()), json.loads(req.data)))
        return Reponse()

    monkeypatch.setattr("urllib.request.urlopen", faux_urlopen)
    rid = instantane.publier(inst, "https://xyz.supabase.co/", "anon-key", "jeton")
    assert rid.startswith("0b5c0f6e")
    url, entetes, corps = envois[0]
    assert url == "https://xyz.supabase.co/rest/v1/rpc/trading_ingest"
    assert entetes["Apikey"] == "anon-key" and corps["p_token"] == "jeton" and corps["p_payload"]["version"] == 1
    instantane.publier(inst, " https://xyz.supabase.co/rest/v1/ ", "anon-key", "jeton")
    assert envois[1][0] == "https://xyz.supabase.co/rest/v1/rpc/trading_ingest"
    with pytest.raises(RuntimeError):
        instantane.publier(inst, "", "", "")

    import io
    import urllib.error

    def refus(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, io.BytesIO(b'{"code":"PGRST202"}'))

    monkeypatch.setattr("urllib.request.urlopen", refus)
    with pytest.raises(RuntimeError, match="PGRST202") as err:
        instantane.publier(inst, "https://xyz.supabase.co", "anon-key", "jeton")
    assert "migration 12" in str(err.value) and "jeton" not in str(err.value)
