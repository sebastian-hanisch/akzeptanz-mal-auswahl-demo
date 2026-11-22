"""Handbeispiele von Hand gerechnet (handbeispiele_04.py, Teile A bis E des Plans): jede Zahl hier ist eine Handrechnung, kein Messwert.

A: fünf Akzeptanzregeln auf derselben Folge von Änderungen; B: Kreditzuweisung auf einer Spielzeugfolge; C: Zerlegung der Streuung im 2 x 2-Fall;
D: Rangumkehr in einer Zahl; E: Mini-Instanz für die Zugarten."""

import math

import pytest

import aka_accept as AC
import aka_belohnung as B
import aka_constants as C
import aka_evaluation as E
import aka_moves as M
import aka_scenario as S

DELTAS = (-4.0, -5.0, -3.0, 1.5, 1.0, 3.0, 1.0, 0.5)
ZUFALL_SA = (0.02, 0.10, 0.30, 0.50, 0.05)


def _ablauf(regel: str):
    """Die Folge A mit einer Regel: Startkosten 100, Budget 8, L = 3, rho = 1 %, Sintflut-Pegel 100 - 2,5 u, Annealing T = 1 mit gesetzten Zufallszahlen."""
    kosten, best = 100.0, 100.0
    hist = AC.new_hist(100.0, 3)
    u_sa = list(ZUFALL_SA)
    angenommen, verlauf = [], []
    for step, d in enumerate(DELTAS):
        neu = kosten + d
        used = step + 1
        if regel == "ob":
            ok = AC.accept_ob(d)
        elif regel == "rr":
            ok = AC.accept_rr(d, neu, best, 0.01)
        elif regel == "gd":
            ok = AC.accept_gd(d, neu, 100.0, used, 8, 0.8)
        elif regel == "la":
            ok = AC.accept_la(d, neu, hist, step)
        else:
            ok = d <= AC.EPS or AC.accept_sa(d, 1.0, u_sa.pop(0))
        if ok:
            kosten = neu
            best = min(best, kosten)
            angenommen.append(step + 1)
        if regel == "la":
            AC.update_hist(hist, step, kosten)
        verlauf.append(kosten)
    return angenommen, verlauf, best


@pytest.mark.parametrize("regel,schritte,ende", [
    ("ob", (1, 2, 3), 88.0), ("rr", (1, 2, 3, 8), 88.5), ("gd", (1, 2, 3, 4), 89.5), ("la", (1, 2, 3, 4, 5), 90.5), ("sa", (1, 2, 3, 4, 5, 8), 91.0)])
def test_teil_a_fuenf_akzeptanzregeln_auf_derselben_folge(regel, schritte, ende):
    angenommen, verlauf, best = _ablauf(regel)
    assert tuple(angenommen) == schritte
    assert verlauf[-1] == pytest.approx(ende) and best == pytest.approx(88.0)


def test_teil_a_verlauf_je_regel_wie_in_der_tabelle():
    assert _ablauf("ob")[1] == pytest.approx([96, 91, 88, 88, 88, 88, 88, 88])
    assert _ablauf("rr")[1] == pytest.approx([96, 91, 88, 88, 88, 88, 88, 88.5])
    assert _ablauf("gd")[1] == pytest.approx([96, 91, 88, 89.5, 89.5, 89.5, 89.5, 89.5])
    assert _ablauf("la")[1] == pytest.approx([96, 91, 88, 89.5, 90.5, 90.5, 90.5, 90.5])
    assert _ablauf("sa")[1] == pytest.approx([96, 91, 88, 89.5, 90.5, 90.5, 90.5, 91])


def test_teil_a_annealing_wahrscheinlichkeiten_und_schwellen():
    assert [math.exp(-d) for d in (1.5, 1.0, 3.0, 1.0, 0.5)] == pytest.approx([0.2231, 0.3679, 0.0498, 0.3679, 0.6065], abs=1e-4)
    assert 1.01 * 88.0 == pytest.approx(88.88)                       # Rekord-zu-Rekord: Schritt 5 (89) liegt 0,12 über der Schwelle, nie auf ihr
    assert [100 - 2.5 * u for u in (4, 5, 6, 7, 8)] == [90.0, 87.5, 85.0, 82.5, 80.0]


def test_teil_a_late_acceptance_nie_ueber_den_startkosten():
    import random

    z = random.Random(5)
    for L in (1, 3, 10):
        for _ in range(200):
            kosten, hist = 100.0, AC.new_hist(100.0, L)
            for step in range(60):
                d = z.uniform(-4.0, 6.0)
                neu = kosten + d
                if AC.accept_la(d, neu, hist, step):
                    kosten = neu
                AC.update_hist(hist, step, kosten)
                assert kosten <= 100.0 + 1e-6


def test_teil_b_kreditzuweisung_spielzeugfolge():
    delta = (-4.0, -5.0, -4.0, 3.0, 0.5, 1.5, -2.5, -1.5)
    art = "BBBSSSBB"
    kante = 1000.0                                                # Normierung: Belohnung = Verbesserung / 1000
    kosten, hist = 100.0, AC.new_hist(100.0, 3)
    tr = B.BestTracker(100.0)
    r2_summe = {"B": 0.0, "S": 0.0}
    best_summe = {"B": 0.0, "S": 0.0}
    la_kosten = []
    for step, (d, a) in enumerate(zip(delta, art, strict=True)):
        neu = kosten + d
        ok = AC.accept_la(d, neu, hist, step)
        if ok:
            kosten = neu
        AC.update_hist(hist, step, kosten)
        la_kosten.append(kosten)
        r2_summe[a] += B.reward_r2(d, 1, kante) * kante
        s = tr.senkung(d, ok)
        best_summe[a] += B.reward_best(s, 1, kante) * kante if s > 0 else 0.0
    assert la_kosten == pytest.approx([96, 91, 87, 90, 90.5, 90.5, 88, 86.5])
    assert r2_summe["B"] == pytest.approx(17.0) and r2_summe["S"] == 0.0
    assert best_summe["B"] == pytest.approx(13.5) and best_summe["S"] == 0.0
    assert 17.0 - 13.5 == pytest.approx(90.5 - 87.0)               # Reparatur-Gutschrift = Abstand vom Rekord vor der Reparatur


def test_teil_c_zerlegung_im_kleinsten_fall():
    z = E.zerlege([[[6.01, 9.52], [5.72, 11.49]]])               # eine Instanz, Zeilen Zufall und Choice Function, Spalten nur besser und Late Acceptance
    assert z["auswahl"] == pytest.approx(100 * 0.7056 / 23.5121, abs=1e-3)
    assert z["akzeptanz"] == pytest.approx(100 * 21.5296 / 23.5121, abs=1e-3)
    assert z["ww"] == pytest.approx(100 * 1.2769 / 23.5121, abs=1e-3)
    assert (round(z["auswahl"], 1), round(z["akzeptanz"], 1), round(z["ww"], 1)) == (3.0, 91.6, 5.4) and z["rest"] == pytest.approx(0.0, abs=1e-9)
    assert (5.72 - 6.01, 11.49 - 9.52) == pytest.approx((-0.29, 1.97))     # Unterschied der Unterschiede


def test_teil_d_rangumkehr_in_einer_zahl():
    rang_ob = [6, 5, 1, 2, 3, 4]
    rang_la = [2, 3, 5, 4, 1, 6]
    d2 = sum((a - b) ** 2 for a, b in zip(rang_ob, rang_la, strict=True))
    assert d2 == 48 and 1 - 6 * d2 / (6 * 35) == pytest.approx(-0.3714, abs=1e-4)
    assert E.spearman(rang_ob, rang_la) == pytest.approx(-0.3714, abs=1e-4)


def test_teil_e_mini_instanz_der_zugarten():
    punkte = [(0.0, 0.0), (3.0, 0.0), (3.0, 4.0), (0.0, 4.0), (1.5, 2.0)]
    D = S.distance_matrix(punkte)
    assert S.tour_cost(D, [0, 1, 2, 3, 4]) == pytest.approx(15.0)
    assert S.tour_cost(D, [0, 2, 1, 3, 4]) == pytest.approx(19.0)           # 2-opt Position 1 bis 2: Delta +4
    assert S.tour_cost(D, [0, 3, 2, 1, 4]) == pytest.approx(16.0)           # Tausch der Positionen 1 und 3: Delta +1
    assert S.tour_cost(D, [0, 4, 1, 2, 3]) == pytest.approx(16.0)           # Or-opt: Delta +1
    assert M.PROPOSE is not None and C.K == 8
