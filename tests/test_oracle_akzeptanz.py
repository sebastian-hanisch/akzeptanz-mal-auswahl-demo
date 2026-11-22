"""Orakel (anderer Rechenweg, ORACLE-PLAYBOOK §2 „Metaheuristiken“): Delta gegen volle Neubewertung, exakte Wahrheit bei n = 8 und 9,
Replay der Akzeptanz durch eine naive Neuimplementierung der Regeln aus den Formeln.

(a) Delta jeder Zugart und Gültigkeit der Tour nach jedem angenommenen Zug (`check=True` der Suche prüft Permutation und Länge gegen
    `tour_cost`), für alle sieben Akzeptanzregeln. (b) Die Suche liegt nie unter dem Optimum (Aufzählung, Held-Karp als zweiter Weg) und erreicht es
    bei n = 9 in einem Band. (c) Replay: eine naive Fassung (Listen statt Ring, ohne Verteiler) liest Δ und Annahme jedes Schritts aus der Aufzeichnung
    der Suche und trifft in jedem Schritt dieselbe Entscheidung."""

import itertools
import math

import pytest
from conftest import brute_force, zufallsinstanz

import aka_algorithm as A
import aka_constants as C
import aka_scenario as S
from aka_rngblock import BlockSplitMix64
from aka_search import check_feasible, run_search

AKZ_ALLE = ("ob", "rr", "sa", "gd", "la", "la10", "la1", "la200", "am")


def held_karp(D) -> float:
    """Zweiter Rechenweg für das Optimum: dynamische Programmierung über Teilmengen."""
    n = len(D)
    voll = 1 << (n - 1)
    dp = [[math.inf] * (n - 1) for _ in range(voll)]
    for j in range(n - 1):
        dp[1 << j][j] = D[n - 1][j]
    for maske in range(voll):
        for j in range(n - 1):
            if not maske & (1 << j) or dp[maske][j] == math.inf:
                continue
            for k in range(n - 1):
                if maske & (1 << k):
                    continue
                m2 = maske | (1 << k)
                v = dp[maske][j] + D[j][k]
                if v < dp[m2][k]:
                    dp[m2][k] = v
    return min(dp[voll - 1][j] + D[j][n - 1] for j in range(n - 1))


@pytest.mark.parametrize("akz", AKZ_ALLE)
def test_a_delta_und_gueltigkeit_nach_jedem_angenommenen_zug(akz):
    for familie in C.FAMILIEN:
        _, D = A.instance(familie, 30, 0)
        t0 = S.start_tour(D, familie, 30, 0, 0)
        for zeile in ("rand", "cf", "s7"):
            A.run_on(D, t0, BlockSplitMix64(3), zeile, akz, 1500, check=True)       # check=True wirft bei falschem Delta oder keiner Permutation


@pytest.mark.parametrize("n", [8, 9])
def test_b_exakte_wahrheit_zwei_rechenwege(n):
    for seed in range(3):
        D, _ = zufallsinstanz(n, seed)
        assert brute_force(D) == pytest.approx(held_karp(D), abs=1e-9)


@pytest.mark.parametrize("akz", ["ob", "rr", "sa", "gd", "la", "am"])
def test_b_suche_liegt_nie_unter_dem_optimum_und_erreicht_es_oft(akz):
    erreicht, gesamt = 0, 0
    for seed in range(4):
        D, t0 = zufallsinstanz(9, seed)
        opt = brute_force(D)
        for lauf in range(10):
            r = run_search(D, t0, 3000, C.ALLE_ZUGARTEN, akz, BlockSplitMix64(100 * seed + lauf))
            assert r["best"] >= opt - 1e-9
            gesamt += 1
            erreicht += r["best"] <= opt + 1e-9
    if akz == "am":
        return                                              # Gegenprobe: Annahme aller Züge ist keine Suche, nur die Grenze nach unten gilt
    assert erreicht / gesamt >= 0.60, (akz, erreicht, gesamt)   # Band, im Bau gesetzt (gemessen siehe BAU_4)


class Aufzeichner:
    """Zufallsstrom mit Protokoll; zugleich Haken der Suche, der Δ, Länge der Anwendung und Annahme je Anwendung festhält (wählt gleichverteilt wie die Suche)."""

    def __init__(self, seed, m):
        self.inner = BlockSplitMix64(seed)
        self.u = []
        self.m = m
        self.protokoll = []

    def random(self):
        x = self.inner.random()
        self.u.append(x)
        return x

    def choose(self, rng):
        return 0 if self.m == 1 else int(rng.random() * self.m)

    def update(self, index, delta, kosten, angenommen):
        self.protokoll.append((delta, kosten, angenommen, self.u[-1]))


def naive_entscheidung(regel, L, schritt, delta, kosten, best, c0, n, used, budget, verlauf, u):
    """Naive Neuimplementierung der Regeln aus den Formeln (Listen statt Ring)."""
    eps, rho = 1e-9, 0.01
    neu = kosten + delta
    if regel == "ob":
        return delta < -eps
    if regel == "rr":
        return delta <= eps or neu <= (1 + rho) * best
    if regel == "la":
        vor = c0 if schritt < L else verlauf[schritt - L]
        return delta <= eps or neu <= vor
    if regel == "gd":
        return delta <= eps or neu <= c0 * (1 - (1 - 0.8) * used / budget)
    if regel == "sa":
        kante = c0 / n
        temp = 0.3 * kante * (0.003 / 0.3) ** (used / budget)
        return delta <= eps or u < math.exp(-delta / temp)
    return True


@pytest.mark.parametrize("akz,regel,L", [("ob", "ob", 0), ("rr", "rr", 0), ("la", "la", 50), ("la10", "la", 10), ("la1", "la", 1), ("la200", "la", 200),
                                          ("gd", "gd", 0), ("sa", "sa", 0), ("am", "am", 0)])
def test_c_replay_trifft_in_jedem_schritt_dieselbe_entscheidung(akz, regel, L):
    schritte = 0
    for familie in C.FAMILIEN:
        n = 30
        _, D = A.instance(familie, n, 1)
        t0 = S.start_tour(D, familie, n, 1, 0)
        for zeile_m in (8, 1):
            rec = Aufzeichner(7, zeile_m)
            arms = C.ALLE_ZUGARTEN if zeile_m == 8 else (2,)
            r = run_search(D, t0, 1500, arms, akz, rec, selector=rec)
            c0 = S.tour_cost(D, t0)
            kosten, best, used, verlauf = c0, c0, 0, []
            for schritt, (delta, c, angenommen, u) in enumerate(rec.protokoll):
                used += c
                erwartet = naive_entscheidung(regel, L, schritt, delta, kosten, best, c0, n, used, 1500, verlauf, u)
                assert angenommen == erwartet, (akz, schritt)
                if angenommen:
                    kosten += delta
                    best = min(best, kosten)
                verlauf.append(kosten)
                schritte += 1
            assert r["final"] == pytest.approx(kosten, abs=1e-6)
    assert schritte > 3000


def test_c_replay_prueft_auch_ablehnungen():
    """Der Replay ist nicht leer: unter jeder Regel außer „alle Züge“ kommen Ablehnungen vor."""
    _, D = A.instance("gleich", 30, 2)
    t0 = S.start_tour(D, "gleich", 30, 2, 0)
    for akz in ("ob", "rr", "la", "gd", "sa"):
        rec = Aufzeichner(3, 8)
        run_search(D, t0, 1500, C.ALLE_ZUGARTEN, akz, rec, selector=rec)
        a = [p[2] for p in rec.protokoll]
        assert any(a) and not all(a), akz
    assert check_feasible(t0, 30)
    assert list(itertools.islice(range(3), 2)) == [0, 1]
