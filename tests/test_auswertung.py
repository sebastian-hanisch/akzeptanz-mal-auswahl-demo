"""Auswertung: Zerlegung, Permutationstest, Rangkorrelation, Bootstrap gegen unabhängige Rechenwege (Orakel d bis g des Plans)."""

import numpy as np
import pytest

import aka_evaluation as E


def zerlege_unabhaengig(gap):
    """Zweiter Rechenweg: kleinste Quadrate mit Entwurfsmatrix. Spalten: Auswahl-Effekte, Akzeptanz-Effekte (je Summe 0), Wechselwirkung = Rest der Zellmittel."""
    g = np.asarray(gap, dtype=float)
    i, s, r = g.shape
    y = (g - g.mean(axis=(1, 2), keepdims=True)).reshape(-1)
    zeilen = np.tile(np.repeat(np.arange(s), r), i)
    spalten = np.tile(np.arange(r), i * s)

    def effekt(idx, k):
        x = np.zeros((len(y), k - 1))
        for j in range(k - 1):
            x[:, j] = (idx == j).astype(float) - (idx == k - 1).astype(float)
        return x

    xa, xr = effekt(zeilen, s), effekt(spalten, r)
    ss = float((y ** 2).sum())
    beta_a = np.linalg.lstsq(np.hstack([xa, xr]), y, rcond=None)[0]
    fit_beide = np.hstack([xa, xr]) @ beta_a
    fit_a = xa @ np.linalg.lstsq(xa, y, rcond=None)[0]
    fit_r = xr @ np.linalg.lstsq(xr, y, rcond=None)[0]
    # Das Modell ist ausgewogen: die Spaltenräume stehen senkrecht aufeinander, die Teilsummen sind die Quadratsummen der Effekte
    ss_a, ss_r = float((fit_a ** 2).sum()), float((fit_r ** 2).sum())
    assert float((fit_beide ** 2).sum()) == pytest.approx(ss_a + ss_r, rel=1e-9)
    zellen = np.zeros((s, r))
    for a in range(s):
        for b in range(r):
            zellen[a, b] = y[(zeilen == a) & (spalten == b)].mean()
    wechsel = zellen - (fit_beide.reshape(i, s, r).mean(axis=0))
    ss_w = i * float((wechsel ** 2).sum())
    return 100 * ss_a / ss, 100 * ss_r / ss, 100 * ss_w / ss


@pytest.mark.parametrize("seed", range(10))
def test_zerlegung_stimmt_mit_dem_zweiten_rechenweg(seed):
    z = np.random.default_rng(seed)
    g = z.normal(size=(12, 4, 5)) + z.normal(size=(1, 4, 1)) * 2 + z.normal(size=(1, 1, 5)) * 3 + z.normal(size=(1, 4, 5))
    a, r, w = zerlege_unabhaengig(g)
    ist = E.zerlege(g)
    assert ist["auswahl"] == pytest.approx(a, abs=1e-8) and ist["akzeptanz"] == pytest.approx(r, abs=1e-8) and ist["ww"] == pytest.approx(w, abs=1e-8)
    assert ist["auswahl"] + ist["akzeptanz"] + ist["ww"] + ist["rest"] == pytest.approx(100.0)


def test_zerlegung_nullfall_und_reiner_effekt():
    assert E.zerlege(np.ones((3, 2, 2)))["ss"] == 0.0
    g = np.zeros((5, 3, 4))
    g[:, :, 2] = 1.0                                    # nur ein Akzeptanz-Effekt
    z = E.zerlege(g)
    assert z["akzeptanz"] == pytest.approx(100.0) and z["auswahl"] == pytest.approx(0.0, abs=1e-9)


def test_rauschanteil():
    g = np.random.default_rng(1).normal(size=(10, 3, 3))
    var = np.full((10, 3, 3), 0.5)
    y = g - g.mean(axis=(1, 2), keepdims=True)
    assert E.rauschanteil(g, var, 4) == pytest.approx(100 * 0.5 * 90 / 4 / float((y ** 2).sum()))


def test_spearman_gegen_scipy():
    stats = pytest.importorskip("scipy.stats")
    z = np.random.default_rng(3)
    for _ in range(40):
        a = z.normal(size=6)
        b = z.normal(size=6)
        assert E.spearman(a, b) == pytest.approx(stats.spearmanr(a, b)[0], abs=1e-12)
    a = [1.0, 1.0, 2.0, 3.0, 3.0, 5.0]                  # mit Gleichständen: mittlere Ränge
    b = [2.0, 1.0, 1.0, 4.0, 6.0, 5.0]
    assert E.spearman(a, b) == pytest.approx(stats.spearmanr(a, b)[0], abs=1e-12)
    assert E.ranks([3.0, 1.0, 1.0, 2.0]) == [4.0, 1.5, 1.5, 3.0]


def test_spearman_matrix_symmetrisch_mit_einsen():
    m = np.random.default_rng(2).normal(size=(6, 6))
    sm = E.spearman_matrix(m)
    for a in range(6):
        assert sm[a][a] == pytest.approx(1.0)
        for b in range(6):
            assert sm[a][b] == pytest.approx(sm[b][a])


def test_permutationstest_ohne_wechselwirkung_liegt_um_0_05():
    """Additive Tafel plus Rauschen: der Anteil der p-Werte unter 0,05 liegt in einem Band um 0,05 (hier 80 Wiederholungen mit 150 Vertauschungen)."""
    z = np.random.default_rng(11)
    zeile, spalte = z.normal(size=(1, 4, 1)), z.normal(size=(1, 1, 4)) * 2
    klein = 0
    for rep in range(80):
        g = zeile + spalte + z.normal(size=(15, 4, 4))
        klein += E.permutationstest(g, 150, seed=100 + rep)["p"] < 0.05
    assert klein / 80 <= 0.20


def test_permutationstest_findet_starke_wechselwirkung():
    z = np.random.default_rng(5)
    g = z.normal(size=(15, 4, 4)) * 0.3
    g[:, 0, 0] += 5.0
    r = E.permutationstest(g, 200, seed=7)
    assert r["p"] == pytest.approx(r["kleinster"]) and r["kleinster"] == pytest.approx(1 / 201)
    assert E.permutationstest(g, 200, seed=7)["p"] == r["p"]      # fester Zufalls-Seed, feste Ausgabe


def test_bootstrap_intervall_eigenschaften():
    werte = [float(i % 7) - 3.0 for i in range(70)]
    lo, hi = E.bootstrap_interval(werte, 7, 4000)
    assert lo < 0 < hi
    assert E.bootstrap_interval(werte, 7, 4000) == (lo, hi) and E.bootstrap_interval(werte, 8, 4000) != (lo, hi)
    breit = (hi - lo)
    vier = E.bootstrap_interval(werte * 4, 7, 4000)
    assert 0.35 * breit <= vier[1] - vier[0] <= 0.65 * breit          # vierfache Stichprobe: etwa halbe Breite
    sd = float(np.std(werte, ddof=1))
    normal = 2 * 1.96 * sd / np.sqrt(len(werte))
    assert breit == pytest.approx(normal, rel=0.15)
    assert E.bootstrap_interval([1.0], 7) is None
    schmal = E.bootstrap_interval(werte, 7, 4000, 0.95)
    weit = E.bootstrap_interval(werte, 7, 4000, 1 - 0.05 / 30)
    assert weit[0] < schmal[0] and weit[1] > schmal[1]                  # Bonferroni ist breiter


def test_vergleich_klassen_und_zaehlung():
    zufall = [10.0, 10.0, 10.0, 10.0, 10.0, 10.0]
    r = E.vergleich_gegen_zufall(zufall, [9.0, 9.1, 8.9, 9.0, 9.2, 8.8], vergleiche=1)
    assert r["ausgang"] == "vorteil" and r["klasse"] == "klar"
    r = E.vergleich_gegen_zufall(zufall, [11.0, 11.1, 10.9, 11.0, 11.2, 10.8])
    assert r["ausgang"] == "nachteil"
    r = E.vergleich_gegen_zufall(zufall, [10.05, 9.95, 10.0, 10.02, 9.98, 10.0])
    assert r["ausgang"] == "unentschieden"
    assert E.vergleich_gegen_zufall([1.0], [0.0])["klasse"] is None
    assert E.zaehle(["vorteil", "nachteil", "vorteil", "unentschieden"]) == (2, 1, 1)
