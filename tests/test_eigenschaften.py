"""Eigenschaften der Suche mit Akzeptanzregeln (je 20 bis 50 Instanzen, fester Zufalls-Seed): Plan Z5, Eigenschaften 1 bis 9."""

import pytest
from conftest import zufallsinstanz

import aka_algorithm as A
import aka_constants as C
import aka_experiments as X
import aka_scenario as S
import aka_search as SR
from aka_rngblock import BlockSplitMix64

AKZ = ("ob", "rr", "sa", "gd", "la", "la10", "am")
ZEILEN = C.ZEILEN


def _lauf(familie, n, idx, lauf, zeile, akz, b, **kw):
    return A.run(familie, n, idx, lauf, zeile, akz, b, **kw)


def test_1_gleicher_zufalls_seed_gleiche_ausgabe_anderer_andere():
    for akz in AKZ:
        a = _lauf("cluster", 30, 3, 0, "cf", akz, 1500)
        b = _lauf("cluster", 30, 3, 0, "cf", akz, 1500)
        c = _lauf("cluster", 30, 3, 1, "cf", akz, 1500)
        assert (a["best"], a["final"], a["steps"], a["tour"]) == (b["best"], b["final"], b["steps"], b["tour"])
        assert (a["tour"], a["steps"]) != (c["tour"], c["steps"])


def test_2_nur_besser_ist_monoton():
    for familie in C.FAMILIEN:
        for idx in range(6):
            for zeile in ZEILEN:
                r = _lauf(familie, 30, idx, 0, zeile, "ob", 1500)
                assert r["final"] == r["best"]


@pytest.mark.parametrize("L", [1, 3, 10, 50])
def test_3_invariante_late_acceptance_nie_ueber_den_startkosten(L):
    for familie in C.FAMILIEN:
        for idx in range(10):
            r = _lauf(familie, 30, idx, 0, "rand", f"la{L}", 1500, trace=True)
            assert max([r["start"]] + [c for _u, _h, _m, _d, c, _b, _k in r["trace"]]) <= r["start"] + 1e-6


def test_4_l1_gleich_nur_besser_bitgleich():
    gleich = 0
    for familie in C.FAMILIEN:
        for idx in range(10):
            for zeile in ("rand", "cf", "s2"):
                a = _lauf(familie, 30, idx, 0, zeile, "ob", 1500, trace=True)
                b = _lauf(familie, 30, idx, 0, zeile, "la1", 1500, trace=True)
                assert (a["best"], a["final"], a["tour"], a["steps"], a["apps"]) == (b["best"], b["final"], b["tour"], b["steps"], b["apps"])
                gleich += 1
    assert gleich == 90


def test_4_rekord_zu_rekord_mit_rho_null_gleich_nur_besser(monkeypatch):
    orig = SR.AC.accept_rr
    monkeypatch.setattr(SR.AC, "accept_rr", lambda delta, neu, best: orig(delta, neu, best, 0.0))
    for familie in C.FAMILIEN:
        for idx in range(6):
            a = _lauf(familie, 30, idx, 0, "rand", "ob", 1500)
            b = _lauf(familie, 30, idx, 0, "rand", "rr", 1500)
            assert (a["best"], a["final"], a["tour"]) == (b["best"], b["final"], b["tour"])


def test_4_alle_zuege_annehmen_hat_annahmerate_genau_eins():
    for zeile in ZEILEN:
        r = _lauf("gleich", 30, 0, 0, zeile, "am", 1500)
        assert sum(r["accd"]) == r["steps"] == sum(r["apps"])


def test_5_skalieren_der_koordinaten_mit_acht():
    for akz in ("ob", "rr", "sa", "gd", "la", "am"):
        for zeile in ("rand", "ucb", "cf", "laut", "s2"):
            D, t0 = zufallsinstanz(30, 4)
            D8 = [[8.0 * x for x in row] for row in D]
            a = A.run_on(D, t0, BlockSplitMix64(5), zeile, akz, 1500, trace=True)
            b = A.run_on(D8, t0, BlockSplitMix64(5), zeile, akz, 1500, trace=True)
            assert [(h, mv) for _u, h, mv, *_ in a["trace"]] == [(h, mv) for _u, h, mv, *_ in b["trace"]], (akz, zeile)
            assert b["best"] == pytest.approx(8.0 * a["best"], rel=1e-9)


def test_6_umnummerieren_der_orte_aendert_nichts():
    D, t0 = zufallsinstanz(30, 6)
    n = 30
    perm = list(range(n))[::-1]                                   # Ort i heißt künftig perm.index(i)
    neu_von_alt = {alt: neu for neu, alt in enumerate(perm)}
    D2 = [[D[perm[a]][perm[b]] for b in range(n)] for a in range(n)]
    t2 = [neu_von_alt[c] for c in t0]
    for akz in ("ob", "rr", "la", "sa"):
        for zeile in ("rand", "cf"):
            a = A.run_on(D, t0, BlockSplitMix64(9), zeile, akz, 1500)
            b = A.run_on(D2, t2, BlockSplitMix64(9), zeile, akz, 1500)
            assert (a["best"], a["final"], a["steps"]) == (b["best"], b["final"], b["steps"])


def test_7_groesseres_budget_verschlechtert_den_bestwert_nie():
    for akz in C.BUDGETFREI:
        for zeile in ("rand", "cf", "s2"):
            for idx in range(6):
                letzter = 1e300
                for faktor in (25, 50, 100, 200):
                    b = _lauf("gleich", 30, idx, 0, zeile, akz, faktor * 30, checkpoints=())["best"]
                    assert b <= letzter + 1e-9
                    letzter = b


def test_8_wiedergabe_der_spur_gleich_neulauf_bis_k():
    for akz in ("ob", "rr", "la"):
        r = X.ablauf("gleich", 30, 2, 0, "cf", akz, 50)
        spur = r["trace"]
        assert len(spur) > 5
        for pos in (0, len(spur) // 3, len(spur) - 1):
            used, k = spur[pos][0], spur[pos][6]
            neu = _lauf("gleich", 30, 2, 0, "cf", akz, used)                     # Neulauf mit genau den Auswertungen bis zu dieser Anwendung
            assert neu["tour"] == X.tour_nach(r, k)
            assert neu["steps"] == k
        assert X.tour_nach(r, 0) == r["t0"] and X.tour_nach(r, r["steps"]) == r["tour"]


def test_9_feste_zugart_waehlt_nie_eine_andere_und_b5_verbraucht_genau_den_rest():
    for akz in AKZ:
        r = _lauf("gleich", 30, 0, 0, "s2", akz, 1500)
        assert r["apps"][C.H_2OPT] == r["steps"] and sum(r["apps"]) == r["steps"]
    for akz in AKZ:
        for zeile in ZEILEN:
            for b in (1, 3, 7, 1499, 1500):
                r = _lauf("gleich", 30, 0, 0, zeile, akz, b)
                assert r["used"] == b and sum(r["evals"]) == b            # genau das Budget, auch am Rand mit 2opt_b5
    r = _lauf("gleich", 30, 0, 0, "s7", "ob", 12)
    assert r["evals"][C.H_2OPT_B5] == 12 and r["apps"][C.H_2OPT_B5] == 3 and r["steps"] == 3    # 5 + 5 + 2


def test_zweig_jede_akzeptanzregel_weicht_von_jeder_anderen_ab():
    """Zweig-Test (Nullspalte = Bug-Signal): auf mindestens einer Instanz unterscheiden sich je zwei Regeln. Ausnahme: la1 und ob sind dieselbe Regel."""
    namen = ("ob", "rr", "sa", "gd", "la", "la10", "am")
    ergebnis = {}
    for akz in namen:
        ergebnis[akz] = tuple(_lauf(f, 30, i, 0, "rand", akz, 1500)["best"] for f in C.FAMILIEN for i in range(8))
    for i, a in enumerate(namen):
        for b in namen[i + 1:]:
            assert ergebnis[a] != ergebnis[b], (a, b)


def test_akzeptanzname_und_unbekannte_regel():
    assert SR.parse_accept("la50") == ("la", 50) and SR.parse_accept("la") == ("la", 50) and SR.parse_accept("la10") == ("la", 10)
    assert SR.parse_accept("la200") == ("la", 200) and SR.parse_accept("am") == ("am", 0) and SR.parse_accept("ob") == ("ob", 0)
    for falsch in ("la0", "lax", "xx", ""):
        with pytest.raises(ValueError):
            SR.parse_accept(falsch)
    assert X.akz_name("la", 12) == "la12" and X.akz_name("ob", 12) == "ob"


def test_la50_und_la_sind_dieselbe_suche():
    a = _lauf("gleich", 30, 0, 0, "cf", "la", 1500)
    b = _lauf("gleich", 30, 0, 0, "cf", "la50", 1500)
    assert (a["best"], a["tour"]) == (b["best"], b["tour"])
    assert S.tour_cost(A.instance("gleich", 30, 0)[1], a["tour"]) == pytest.approx(a["final"])
