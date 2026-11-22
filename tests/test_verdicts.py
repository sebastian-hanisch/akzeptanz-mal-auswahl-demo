"""Verdikte als reine Funktionen an handgesetzten Werten: Schwellen und jede Zahl im Text, Nullwächter (Nenner 0, zu wenige Instanzen)."""

import pytest

import aka_constants as C
import aka_evaluation as E


def _z(akz, ausgang):
    return dict(akz=akz, ausgang=ausgang)


# ---------------------------------------------------------------- Kernfrage 0
def test_ablauf_faktenzeile_mit_jeder_zahl():
    art, t = E.verdict_ablauf(1234.4, 12.34, 1500, 1480, 4.0, 42.3, 1.19)
    assert art == "info"
    for s in ("1234", "12,3 % unter der Startlösung", "1 500 Auswertungen", "1 480 Anwendungen", "4,0 % der Anwendungen angenommen",
              "davon 42,3 % ohne strenge Verbesserung", "1,19 % über der besten", "Einzellauf, kein Mittel"):
        assert s in t, s


def test_ablauf_ohne_annahme_hat_keinen_nenner_null():
    art, t = E.verdict_ablauf(1000.0, 0.0, 1500, 0, None, None, 0.0)
    assert art == "info" and "Keine Annahme." in t and "nan" not in t.lower()
    k = E.ablauf_kennzahlen(1000.0, 1000.0, 1000.0, 0, 0, 0)
    assert k["acc_pct"] is None and k["nonimp_pct"] is None and k["gain"] == 0.0


def test_ablauf_kennzahlen_gegen_handrechnung():
    k = E.ablauf_kennzahlen(100.0, 90.0, 92.0, 200, 10, 4)
    assert k["gain"] == pytest.approx(10.0) and k["acc_pct"] == pytest.approx(5.0) and k["nonimp_pct"] == pytest.approx(60.0)
    assert k["end_gap"] == pytest.approx(100 * 2 / 90)


# ---------------------------------------------------------------- Kernfrage 1
def test_gegen_zufall_zaehlung_und_art():
    namen = ["ob", "rr", "sa", "gd", "la", "la10"]
    art, t = E.verdict_gegen_zufall("Choice Function", [_z(a, "unentschieden") for a in namen], 15, 2)
    assert art == "info" and "Vorteil unter 0 von 6 Akzeptanzregeln, Nachteil unter 0, unentschieden unter 6" in t and "15 Instanzen × 2 Zufalls-Seeds" in t
    art, t = E.verdict_gegen_zufall("Choice Function", [_z("a", "vorteil"), _z("b", "vorteil"), _z("c", "unentschieden"), _z("d", "unentschieden"), _z("e", "nachteil"), _z("f", "unentschieden")], 15, 2)
    assert art == "warning" and "Vorteil unter 2 von 6 Akzeptanzregeln, Nachteil unter 1, unentschieden unter 3" in t and "Nachteil unter: e" in t and "Vorteil unter: a, b" in t
    art, t = E.verdict_gegen_zufall("X", [_z("a", "vorteil")] * 3 + [_z("b", "unentschieden")] * 3, 15, 2)
    assert art == "success"
    art, t = E.verdict_gegen_zufall("X", [_z("a", "nachteil")] + [_z("b", "unentschieden")] * 5, 15, 2)
    assert art == "warning"


def test_gegen_zufall_zu_wenige_instanzen():
    art, t = E.verdict_gegen_zufall("X", [_z("a", "vorteil")], 1, 2)
    assert art == "info" and "Zu wenige Instanzen" in t


# ---------------------------------------------------------------- Kernfrage 2: Fälle A, B, C aus der Vormessung (B4)
ALLE_LO = dict(auswahl=1.3, akzeptanz=51.5, ww=5.8, rest=41.4)
OHNE_LO = dict(auswahl=1.5, akzeptanz=13.4, ww=0.6, rest=84.5)
ALLE_HI = dict(auswahl=8.5, akzeptanz=11.2, ww=8.8, rest=71.5)
OHNE_HI = dict(auswahl=7.0, akzeptanz=12.7, ww=4.0, rest=76.4)


def test_tafel_fall_a_late_acceptance_erklaert_den_akzeptanzanteil():
    art, t = E.verdict_tafel(50, ALLE_LO, OHNE_LO, 3, 2, 14, 6, 10)
    assert art == "warning"
    for s in ("Stufe 50·n", "erklärt 51,5 % der Streuung der Zellmittel, die Auswahl 1,3 %", "entsteht durch Late Acceptance", "ohne Late Acceptance (L = 50 und L = 10) sind es 13,4 %",
              "kehrt sich gegenüber 3 von 4 anderen Akzeptanzregeln um", "L = 10: 2 von 4", "14 Vorteile, 6 Nachteile, 10 unentschieden von 30 Vergleichen"):
        assert s in t, s


def test_tafel_fall_b_akzeptanz_gross_auch_ohne_late_acceptance():
    art, t = E.verdict_tafel(50, dict(auswahl=2.0, akzeptanz=60.0, ww=3.0, rest=35.0), dict(auswahl=2.0, akzeptanz=40.0, ww=3.0, rest=55.0), 0, 0, 5, 0, 25)
    assert art == "info" and "auch ohne Late Acceptance 40,0 %" in t and "Keine Rangumkehr unter Late Acceptance (0 von 4" in t


def test_tafel_fall_c_kein_faktor_zwei():
    art, t = E.verdict_tafel(200, ALLE_HI, OHNE_HI, 0, 0, 0, 16, 14)
    assert art == "info" and "kein Faktor 2" in t and "Akzeptanz 11,2 %, Auswahl 8,5 %, Wechselwirkung 8,8 %" in t and "Rest (71,5 %)" in t
    assert "0 Vorteile, 16 Nachteile, 14 unentschieden" in t


def test_tafel_schwellen_an_den_raendern():
    # genau Faktor 2: Akzeptanz 20 gegen Auswahl 10 zählt als Fall A/B (>=), 19,9 nicht
    assert E.verdict_tafel(50, dict(auswahl=10.0, akzeptanz=20.0, ww=0, rest=70.0), dict(auswahl=1, akzeptanz=5.0, ww=0, rest=94), 0, 0, 0, 0, 30)[0] == "info"
    assert "kein Faktor 2" in E.verdict_tafel(50, dict(auswahl=10.0, akzeptanz=19.9, ww=0, rest=70.1), dict(auswahl=1, akzeptanz=5.0, ww=0, rest=94), 0, 0, 0, 0, 30)[1]
    # Fall A verlangt Anteil ohne Late Acceptance unter 25 und Differenz mindestens 25 Punkte
    assert E.verdict_tafel(50, dict(auswahl=1.0, akzeptanz=50.0, ww=0, rest=49), dict(auswahl=1, akzeptanz=24.9, ww=0, rest=74), 3, 2, 0, 0, 30)[0] == "warning"
    assert E.verdict_tafel(50, dict(auswahl=1.0, akzeptanz=50.0, ww=0, rest=49), dict(auswahl=1, akzeptanz=25.0, ww=0, rest=74), 3, 2, 0, 0, 30)[0] == "info"
    assert E.verdict_tafel(50, dict(auswahl=1.0, akzeptanz=45.0, ww=0, rest=54), dict(auswahl=1, akzeptanz=20.1, ww=0, rest=79), 3, 2, 0, 0, 30)[0] == "info"   # Differenz 24,9
    # Rangumkehr ab 2 von 4
    assert "kehrt sich" in E.verdict_tafel(200, ALLE_HI, OHNE_HI, 2, 0, 0, 0, 30)[1] and "Keine Rangumkehr" in E.verdict_tafel(200, ALLE_HI, OHNE_HI, 1, 0, 0, 0, 30)[1]


# ---------------------------------------------------------------- Kernfrage 3
def _kurve(muster):
    return list(zip(C.L_WERTE, muster, strict=True))


V, N, U = "vorteil", "nachteil", "unentschieden"


def test_kipp_laengen_vorteil_zusammenhaengend_ab_l1():
    assert E.kipp_laengen(_kurve([V, V, U, U, U, N, N, N, N, N])) == (2, 30)
    assert E.kipp_laengen(_kurve([U, V, V, V, N, N, N, N, N, N])) == (None, 20)       # Vorteil nicht ab L = 1: kein zusammenhängender Vorteil
    assert E.kipp_laengen(_kurve([V] * 10)) == (50, None)                              # Vorteile über 50 hinaus zählen nicht zum Vorteil bis L = 50
    assert E.kipp_laengen(_kurve([U] * 10)) == (None, None)


def test_listenlaenge_verdikt_und_texte():
    art, t = E.verdict_listenlaenge("Choice Function", 50, _kurve([V, V, U, U, U, N, N, N, N, N]))
    assert art == "warning" and "Vorteil gegen Zufall bis L = 2, **Nachteil ab L = 30**, dazwischen unentschieden" in t and "nicht isoliert" in t and "50·n" in t
    art, t = E.verdict_listenlaenge("X", 200, _kurve([U, U, U, U, U, N, N, N, N, N]))
    assert art == "warning" and "Nachteil gegen Zufall ab L = 30, Vorteil bei keinem L" in t
    art, t = E.verdict_listenlaenge("X", 200, _kurve([V, V, V, V, V, V, V, U, U, U]))
    assert art == "success" and "Vorteil gegen Zufall ab L = 1" not in t and "Nachteil bei keinem L" in t
    art, t = E.verdict_listenlaenge("X", 200, _kurve([U] * 10))
    assert art == "info" and "weder Vorteil noch Nachteil" in t


def test_listenlaenge_verdikt_bei_nicht_zusammenhaengendem_vorteil():
    """Vorteil erst bei langen Listen (feste Zugart): kein „Vorteil bis L“, sondern die Längen aufgezählt; nie „weder noch“."""
    art, t = E.verdict_listenlaenge("nur 2-opt", 50, _kurve([U, U, U, U, V, V, V, V, V, V]))
    assert art == "success" and "Vorteil gegen Zufall ab L = 20" in t
    art, t = E.verdict_listenlaenge("X", 50, _kurve([U, V, U, V, U, U, U, U, N, U]))
    assert art == "warning" and "Vorteil gegen Zufall bei L = 2, 10" in t and "**Nachteil bei L = 100**" in t
    assert E.laengen_text([], "Nachteil") == "Nachteil bei keinem L" and E.laengen_text([200], "Nachteil") == "Nachteil bei L = 200"
    assert E.laengen_text([75, 100, 200]) == "ab L = 75" and E.laengen_text([10, 20, 30], "Vorteil") == "Vorteil bei L = 10, 20, 30"


# ---------------------------------------------------------------- Kernfrage 4
def test_budget_verdikt():
    stufen = (50, 100, 200, 400, 800)
    art, t = E.verdict_budget("„nur besser“", list(zip(stufen, (1, 1, 0, 0, 0), strict=True)), list(zip(stufen, (0, 0, 0, 0, 3), strict=True)))
    assert art == "info" and "Vorteil gegen Zufall bei 1 von 5 Auswahlzeilen bei 50·n, **ab 200·n bei keiner mehr**; Nachteil bei 3 von 5 bei 800·n" in t
    art, t = E.verdict_budget("X", list(zip(stufen, (0,) * 5, strict=True)), list(zip(stufen, (0,) * 5, strict=True)))
    assert art == "info" and "bei keiner Stufe ein Vorteil gegen Zufall; Nachteil bei 0 von 5 bei 800·n" in t
    art, t = E.verdict_budget("X", list(zip(stufen, (2,) * 5, strict=True)), list(zip(stufen, (0,) * 5, strict=True)))
    assert art == "success" and "bei jeder Stufe" in t
    art, t = E.verdict_budget("X", list(zip(stufen, (1, 0, 1, 0, 0), strict=True)), list(zip(stufen, (0,) * 5, strict=True)))
    assert "ab 400·n bei keiner mehr" in t


# ---------------------------------------------------------------- Kernfrage 5
def test_zugart_verdikt_schwelle_zwanzig_punkte():
    art, t = E.verdict_zugart("Choice Function", 17.7, 63.6, 51.9, 89.7)
    assert art == "warning"
    for s in ("63,6 % der Anwendungen (89,7 % der Auswertungen)", "„nur besser“ 17,7 % (51,9 %)", "12,5 %", "nicht isoliert"):
        assert s in t, s
    assert E.verdict_zugart("X", 40.0, 60.0, 70.0, 80.0)[0] == "warning"        # genau 20 Punkte
    art, t = E.verdict_zugart("X", 40.1, 60.0, 70.0, 80.0)
    assert art == "info" and "unter 20 Prozentpunkten" in t
    art, t = E.verdict_zugart("X", None, 60.0, 70.0, 80.0)
    assert art == "info" and "keine Anwendung" in t


def test_anteil_b5_und_nenner_null():
    assert E.anteil_b5([0] * 8, [0] * 8) == (None, None)
    apps, evals = [1] * 7 + [1], [1] * 7 + [5]
    a, e = E.anteil_b5(apps, evals)
    assert a == pytest.approx(12.5) and e == pytest.approx(100 * 5 / 12)
    assert sum(E.anteile_je_zugart([2, 2, 0, 0, 0, 0, 0, 4])) == pytest.approx(100.0) and E.anteile_je_zugart([0] * 8) == [0.0] * 8


def test_format_und_tausender_nur_auf_der_zahl():
    assert E.de(-0.254, 2, True) == "−0,25" and E.de(0.254, 2, True) == "+0,25" and E.tsd(600000) == "600 000"
    assert E.intervall(-0.5, 1.25) == "[−0,50; +1,25]"
