"""Eingefrorene Messung (aka_frozen.json): Schema, Größe, Werte, Neu-Rechnen einer Stichprobe als Band, Neu-Rechnen der Auswertung aus den gespeicherten Abständen.

Nicht bitgleich über Plattformen: `math.exp` (Annealing), `math.log` und `math.sqrt` (UCB) kommen aus der C-Bibliothek und kippen selten Entscheidungen;
darum vergleichen die Tests neu gerechnete Läufe nur als Band aus der gespeicherten Standardabweichung (höchstens 3 Standardfehler, mindestens 0,05 Punkte)."""

import math

import numpy as np
import pytest

import aka_algorithm as A
import aka_constants as C
import aka_evaluation as E
import aka_frozen as F
import aka_stats as ST


@pytest.fixture(scope="module")
def d():
    return F.load()


def test_schema_zahl_der_instanzen_und_kopf(d):
    m = d["meta"]
    assert m["schema"] == F.SCHEMA and m["zufall"].startswith("SplitMix64")
    assert (m["tafel_laeufe"], m["budget_laeufe"], m["lreihe_laeufe"]) == (6, 3, 3)
    assert len(d["tafel"]["instanzen"]) == 180 and len(d["budget"]["instanzen"]) == 60 and len(d["lreihe"]["instanzen"]) == 60
    assert m["permutationen"] == 2000 and m["bootstrap_ziehungen"] == 40000
    assert m["auswertungen"]["gesamt"] == sum(m["auswertungen"][k] for k in ("tafel", "budget", "lreihe", "ende"))


def _alle_zahlen(x):
    if isinstance(x, dict):
        for v in x.values():
            yield from _alle_zahlen(v)
    elif isinstance(x, list):
        for v in x:
            yield from _alle_zahlen(v)
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        yield x


def test_alle_werte_endlich_und_abstaende_nicht_negativ(d):
    assert all(math.isfinite(x) for x in _alle_zahlen(d))
    for st in ("lo", "hi"):
        for akz, zeilen in d["tafel"]["stufen"][st]["gap"].items():
            for z, werte in zeilen.items():
                assert len(werte) == 180 and min(werte) >= -1e-9, (st, akz, z)       # Referenz = Minimum aus Referenz und allen Läufen: Abstand nie negativ
    for akz, zeilen in d["budget"]["gap"].items():
        for z, werte in zeilen.items():
            assert len(werte) == 60 and all(len(w) == 5 for w in werte) and min(min(w) for w in werte) >= -1e-9
    for z, ls in d["lreihe"]["gap"].items():
        for L, werte in ls.items():
            assert len(werte) == 60 and all(len(w) == 4 for w in werte) and min(min(w) for w in werte) >= -1e-9


def test_referenz_nicht_ueber_der_gespeicherten_und_unterbotene_gezaehlt(d):
    t = d["tafel"]
    inst = [tuple(x) for x in t["instanzen"]]
    unter = 0
    for (f, n, i), r in zip(inst, t["ref"], strict=True):
        assert r <= A.reference(f, n, i) + 1e-6
        unter += r < A.reference(f, n, i) - 1e-6
    assert unter == t["unterboten"]


def test_stufen_nicht_schlechter_bei_groesserem_budget(d):
    """Für die budgetfreien Regeln ist der Bestwert nach mehr Auswertungen nie schlechter (gleiche Läufe, Kontrollpunkte)."""
    for akz in C.BUDGETFREI + ("la10",):
        for z in C.ZEILEN:
            lo = d["tafel"]["stufen"]["lo"]["gap"][akz][z]
            hi = d["tafel"]["stufen"]["hi"]["gap"][akz][z]
            assert all(h <= l + 1e-4 for l, h in zip(lo, hi, strict=True)), (akz, z)
    b = d["budget"]["gap"]
    for akz in ("ob", "rr", "la"):
        for z in C.ZEILEN:
            for w in b[akz][z]:
                assert all(w[j + 1] <= w[j] + 1e-4 for j in range(4)), (akz, z)


def test_stichprobe_neu_gerechnet_im_band(d):
    t = d["tafel"]
    inst = [tuple(x) for x in t["instanzen"]]
    abweichungen = []
    for familie, n, idx in (("gleich", 30, 100), ("cluster", 60, 101), ("gitter", 30, 102)):
        i = inst.index((familie, n, idx))
        for zeile, akz in (("rand", "ob"), ("cf", "la"), ("s2", "rr")):
            g = [ST.gap(A.run(familie, n, idx, lauf, zeile, akz, 50 * n)["best"], t["ref"][i]) for lauf in range(6)]
            neu = sum(g) / 6
            gespeichert = t["stufen"]["lo"]["gap"][akz][zeile][i]
            band = max(0.05, 3 * math.sqrt(t["stufen"]["lo"]["var"][akz][zeile][i] / 6))
            if abs(neu - gespeichert) > band:
                abweichungen.append((familie, n, idx, zeile, akz, neu, gespeichert, band))
    assert not abweichungen, abweichungen


def test_vorzeichenmuster_nur_aus_gespeicherten_werten(d):
    """Choice Function liegt unter Late Acceptance (L = 50) bei 50·n hinter Zufall, 2-opt allein davor; unter „nur besser“ ist der Unterschied klein."""
    assert F.vergleich(50, "la", "cf")["v"] < 0 and F.vergleich(50, "la", "cf")["hi"] < 0
    assert F.vergleich(50, "la", "s2")["v"] > 0 and F.vergleich(50, "la", "s2")["lo"] > 0
    assert abs(F.vergleich(50, "ob", "cf")["v"]) < 1.0


def test_zerlegung_aus_den_gespeicherten_abstaenden_neu_gerechnet(d):
    for st, faktor in (("lo", 50), ("hi", 200)):
        t = d["tafel"]["stufen"][st]
        arr = np.array([[[t["gap"][a][z][i] for a in C.AKZ6] for z in C.ZEILEN] for i in range(180)])
        alle = E.zerlege(arr)
        for k in ("auswahl", "akzeptanz", "ww", "rest"):
            assert alle[k] == pytest.approx(t["zerlegung"]["alle"][k], abs=0.01), (st, k)
        la, la10 = C.AKZ6.index("la"), C.AKZ6.index("la10")
        ohne = E.zerlege(arr[:, :, [k for k in range(6) if k not in (la, la10)]])
        assert ohne["akzeptanz"] == pytest.approx(t["zerlegung"]["ohne_la"]["akzeptanz"], abs=0.01)
        var = np.array([[[t["var"][a][z][i] for a in C.AKZ6] for z in C.ZEILEN] for i in range(180)])
        assert E.rauschanteil(arr, var, 6) == pytest.approx(t["rauschen"], abs=0.01)
        sm = E.spearman_matrix(arr.mean(axis=0))
        assert np.allclose(sm, t["spearman"], atol=1e-3)
        assert (E.umkehr(sm, la, [0, 1, 2, 3]), E.umkehr(sm, la10, [0, 1, 2, 3])) == (t["umkehr"]["la"], t["umkehr"]["la10"])
        assert faktor == C.STUFEN_TAFEL[0 if st == "lo" else 1]


def test_permutationstest_und_vergleiche_aus_den_gespeicherten_abstaenden(d):
    t = d["tafel"]["stufen"]["lo"]
    arr = np.array([[[t["gap"][a][z][i] for a in C.AKZ6] for z in C.ZEILEN] for i in range(180)])
    p = E.permutationstest(arr)
    assert p["p"] == pytest.approx(t["permutation"]["alle"]["p"], abs=1e-5) and p["c"] == t["permutation"]["alle"]["c"]
    for akz, zeile in (("la", "cf"), ("rr", "cf"), ("ob", "ucb")):
        v95 = E.vergleich_gegen_zufall(t["gap"][akz]["rand"], t["gap"][akz][zeile], C.ZWECK_BOOT, 40000, 1)
        vk = E.vergleich_gegen_zufall(t["gap"][akz]["rand"], t["gap"][akz][zeile], C.ZWECK_BOOT, 40000, 30)
        g = t["vergleiche"][akz][zeile]
        assert (v95["v"], v95["lo"], v95["hi"]) == pytest.approx((g["v"], g["lo"], g["hi"]), abs=2e-4)
        assert (vk["lo"], vk["hi"]) == pytest.approx((g["lo_k"], g["hi_k"]), abs=2e-4)
        assert (v95["ausgang"], vk["ausgang"]) == (g["ausgang"], g["ausgang_k"])


def test_zaehler_stimmen_mit_den_laeufen_ueberein(d):
    """Je Zelle: Summe der Auswertungen = Läufe × Budget (n = 30 und 60 je zur Hälfte); Anwendungen ≥ Annahmen ≥ strenge Verbesserungen."""
    summe_n = 90 * 30 + 90 * 60
    for st, f in (("lo", 50), ("hi", 200)):
        for akz in C.AKZ6:
            for z in C.ZEILEN:
                zz = d["tafel"]["stufen"][st]["zaehler"][akz][z]
                assert zz["laeufe"] == 1080 and sum(zz["evals"]) >= 6 * f * summe_n
                assert sum(zz["apps"]) == zz["steps"] >= sum(zz["accd"]) >= sum(zz["succ"]) > 0
        assert sum(d["tafel"]["stufen"][st]["zaehler"]["ob"]["rand"]["apps"]) > 0
    am = d["tafel"]["stufen"]["lo"]["zaehler"]["am"]["rand"]
    assert sum(am["accd"]) == am["steps"]                                  # alle Züge angenommen: Annahmerate genau 1


def test_ablesefunktionen(d):
    a, e = F.anteil_b5(200, "la", "cf")
    assert 0 < a < 100 and 0 < e < 100 and F.anwendungen_je_lauf(50, "ob", "rand") > 100
    k = F.annahme_kennzahlen(50, "la", "rand")
    assert k["angenommen"] > F.annahme_kennzahlen(50, "ob", "rand")["angenommen"]
    vor, nach = F.budget_zaehlung("ob")
    assert [s for s, _ in vor] == [50, 100, 200, 400, 800] and all(0 <= c <= 5 for _, c in vor + nach)
    assert len(F.l_mittel("cf", 0)) == len(C.L_WERTE) and F.l_ausgaenge("cf", 0)[0][0] == 1
    assert F.l_wanderung("rand", 1, 0)["wanderung"] == pytest.approx(0.0, abs=1e-9)        # L = 1: „nur besser“, die aktuelle Tour ist immer die beste
