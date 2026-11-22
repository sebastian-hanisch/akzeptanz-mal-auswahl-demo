"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b).

`hand`: sechs Orte auf dem Rand eines Rechtecks 8 x 3 (Handbeispiel der Wurzel-Demo, für die kopierten Module)."""

import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import aka_scenario as S  # noqa: E402


@pytest.fixture
def hand():
    """(Abstandsmatrix, Starttour) des Handbeispiels der Wurzel-Demo."""
    _, D = S.hand_instance()
    return D, list(S.HAND_START)


def zufallsinstanz(n: int, seed: int):
    """Kleine Zufallsinstanz für Orakel-Tests (Python-random nur hier in den Tests, nie im Kern)."""
    z = random.Random(seed)
    punkte = [(z.random() * 100.0, z.random() * 100.0) for _ in range(n)]
    tour = list(range(n))
    z.shuffle(tour)
    return S.distance_matrix(punkte), tour


def brute_force(D) -> float:
    """Exaktes Optimum per Aufzählung aller Rundtouren (n bis 9)."""
    import itertools

    n = len(D)
    best = 1e300
    for perm in itertools.permutations(range(1, n)):
        if perm[0] > perm[-1]:
            continue
        c = D[0][perm[0]] + D[perm[-1]][0] + sum(D[a][b] for a, b in zip(perm, perm[1:]))
        best = min(best, c)
    return best


class Skript:
    """Zufallsstrom mit vorgegebenen Werten (für Handrechnungen): `random()` gibt sie der Reihe nach aus."""

    def __init__(self, werte):
        self.werte = list(werte)
        self.gezogen = 0

    def random(self):
        self.gezogen += 1
        return self.werte.pop(0)
