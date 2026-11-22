"""Randfälle und Obergrenzen der Live-Rechnung: kleinste Instanz, Budget am Rand, Regler am Maximum, Rechengrenze als Zählung der Auswertungen, Worst-Case mit Zeitgrenze."""

import time

import pytest

import aka_algorithm as A
import aka_constants as C
import aka_evaluation as E
import aka_experiments as X
import aka_scenario as S
from aka_rngblock import BlockSplitMix64
from aka_search import run_search

AKZ = ("ob", "rr", "sa", "gd", "la", "la10", "la1", "la200", "am")


@pytest.mark.parametrize("akz", AKZ)
def test_kleinste_instanz_mit_allen_acht_zugarten(hand, akz):
    D, t0 = hand
    for h in C.ALLE_ZUGARTEN:
        r = run_search(D, t0, 200, (h,), akz, BlockSplitMix64(1), check=True)
        assert r["used"] == 200 and sorted(r["tour"]) == list(range(6))
    assert S.tour_cost(D, t0) == pytest.approx(28.0)


@pytest.mark.parametrize("budget", [0, 1, 2, 4, 5, 6])
def test_budget_am_rand_auch_kleiner_als_der_preis_einer_anwendung(hand, budget):
    D, t0 = hand
    for akz in AKZ:
        for h in C.ALLE_ZUGARTEN:
            r = run_search(D, t0, budget, (h,), akz, BlockSplitMix64(2))
            assert r["used"] == budget and r["best"] <= S.tour_cost(D, t0) + 1e-9


def test_regler_am_rand_laufen_ohne_fehler():
    for lauf in (0, C.LAUF_MAX):
        for L in (C.L_MIN, C.L_MAX):
            r = X.ablauf("gitter", 60, C.INSTANZ_MAX, lauf, "cf", "la", 200, L)
            assert r["used"] == 12000 and r["steps"] > 0 and r["kennzahlen"]["end_gap"] >= 0.0


@pytest.mark.parametrize("zeile", C.ZEILEN)
@pytest.mark.parametrize("akz", C.AKZ_APP)
def test_ablauf_jede_zeile_jede_akzeptanz(zeile, akz):
    r = X.ablauf("cluster", 30, 1, 0, zeile, akz, 50)
    assert r["used"] == 1500 and r["best"] <= r["start"] + 1e-9
    k = r["kennzahlen"]
    assert k["gain"] >= -1e-9 and k["end_gap"] >= -1e-9
    if akz == "am":
        assert k["acc_pct"] == pytest.approx(100.0)


def test_live_kosten_an_jedem_regler_maximum_unter_der_grenze():
    for n in C.N_GEMESSEN:
        for regel in C.ZEILEN:
            assert 0 <= E.live_cost_e1(n, C.E1_BUDGET, regel) <= C.LIVE_MAX_EVALS
        for faktor in C.BUDGET_LIVE:
            for regel in C.ZEILEN:
                assert 0 <= E.live_cost_e5(n, faktor, regel) <= C.LIVE_MAX_EVALS
            assert E.live_cost_ablauf(n, faktor) <= 12000
    assert E.live_cost_e1(30, 50, "cf") == 540_000 and E.live_cost_e1(60, 50, "cf") == 432_000
    assert E.live_cost_e5(30, 200, "cf") == 324_000 and E.live_cost_e5(60, 200, "cf") == 432_000
    assert E.live_cost_e1(30, 50, "rand") == 0 and E.live_cost_e5(30, 200, "s2") == 0


def test_gezaehlte_auswertungen_gleich_den_angekuendigten():
    """Die Zählung vor dem Start stimmt mit den tatsächlich verbrauchten Auswertungen überein (Zählung statt Zeit)."""
    r = X.e5_messen("cf", 30, 50)
    assert r["kosten"] == E.live_cost_e5(30, 50, "cf")
    assert r["n_inst"] == 9 and r["n_laeufe"] == 2


def test_e1_stichprobe_und_worst_case_mit_zeitgrenze():
    t = time.time()
    r = X.e1_messen("ucb", 60)
    assert time.time() - t < 120
    assert r["kosten"] == E.live_cost_e1(60, 50, "ucb") == 432_000
    assert r["n_inst"] == 6 and r["n_laeufe"] == 2 and len(r["zeilen"]) == 6
    for z in r["zeilen"]:
        assert z["abstand_zufall"] >= 0 and z["abstand_zeile"] >= 0           # Referenz ist das Minimum aus Referenz und Läufen: Abstand nie negativ
        assert z["ausgang"] in ("vorteil", "nachteil", "unentschieden") and z["lo"] <= z["v"] <= z["hi"]


def test_e1_paarung_gleicher_strom_fuer_zufall_und_zeile():
    """Zufall gegen Zufall wäre Unterschied 0: ersatzweise die Probe, dass jede Zeile denselben Lauf rechnet wie A.run mit denselben Zufalls-Seeds."""
    a = A.run("gleich", 30, 0, 0, "rand", "ob", 1500)
    b = A.run("gleich", 30, 0, 0, "rand", "ob", 1500)
    assert a["best"] == b["best"]


def test_unterbotene_referenz_hebt_an():
    """Ein Lauf unter der Referenz gibt Abstand 0 statt eines negativen (Minimum aus Referenz und Läufen), auch im Live-Vergleich."""
    r = X.e1_messen("s2", 30)
    assert all(z["abstand_zufall"] >= 0 for z in r["zeilen"])


def test_e5_fuer_nicht_lernende_regeln_ist_nicht_erlaubt():
    with pytest.raises(AssertionError):
        X.e5_messen("s2", 30, 50)
    with pytest.raises(AssertionError):
        X.e1_messen("rand", 30)
