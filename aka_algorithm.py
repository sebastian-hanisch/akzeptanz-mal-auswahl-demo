"""Ein Lauf der Suche mit Auswahlzeile und Akzeptanzregel. Dünne Komposition: keine eigene Regel.

Die sechs Auswahlzeilen der Kreuztafel (aka_constants.ZEILEN): Zufall, UCB, Choice Function, Lernautomat (alle acht Zugarten, Standardbelohnung =
Verbesserung des Vorschlags je Auswertung, wie in auswahlregeln-demo) und die festen Zugarten „nur 2-opt“ (`s2`) und „nur 2-opt (bester von 5)“ (`s7`).

Startlösung und Zufallsstrom hängen nur an (Familie, n, Instanz, Lauf); alle Zeilen und alle Akzeptanzregeln eines Laufs lesen denselben
Strom von vorn (gemeinsame Zufallszahlen, wie in den Vorgängern der Linie)."""

import json
from functools import lru_cache
from pathlib import Path

import aka_constants as C
import aka_regeln as R
import aka_scenario as S
import aka_select as SE
from aka_rngblock import BlockSplitMix64
from aka_search import run_search

_REFS = Path(__file__).resolve().parent / "aka_refs.json"


@lru_cache(maxsize=1)
def _refs() -> dict:
    return json.loads(_REFS.read_text(encoding="utf-8"))["refs"]


def reference(familie: str, n: int, idx: int) -> float:
    """Bester bekannter Wert der Instanz (Langläufe aus zugmenge-demo; 200 Instanzen je Familie und n). Er kann unterboten werden."""
    return _refs()[familie][str(n)][idx]


@lru_cache(maxsize=512)
def instance(familie: str, n: int, idx: int):
    return S.make_instance(familie, n, idx)


def arms_of(zeile: str) -> tuple[int, ...]:
    """Zugarten, über die die Zeile wählt: acht für Zufall und die Lernregeln, eine für die festen Zeilen."""
    a = C.ZEILEN_ARME[zeile]
    return C.ALLE_ZUGARTEN if a is None else a


def selector_of(zeile: str, start: float, n: int):
    """Haken für die Suche: None für Zufall und die festen Zeilen (die Suche würfelt bzw. wählt selbst, bitgleich zu `rand`), sonst die Lernregel."""
    if zeile in ("rand", "s2", "s7"):
        return None
    return SE.Selector(zeile, C.K, SE.standard_reward(start / n), funktionen={zeile: R.regel_funktionen(zeile)})


def run_on(D, t0, rng, zeile: str, akz: str, budget: int, checkpoints=(), trace: bool = False, stats: bool = False, check: bool = False) -> dict:
    """Ein Lauf auf der Abstandsmatrix D ab der Starttour t0 mit dem Zufallsstrom rng. Rückgabe: das dict von run_search plus `start`, `arms`."""
    n = len(t0)
    start = S.tour_cost(D, t0)
    r = run_search(D, t0, budget, arms_of(zeile), akz, rng, checkpoints=checkpoints, trace=trace, selector=selector_of(zeile, start, n),
                   check=check, stats=stats)
    r.update(start=start, arms=arms_of(zeile), t0=list(t0))
    return r


def run(familie: str, n: int, idx: int, lauf: int, zeile: str, akz: str, budget: int, checkpoints=(), trace: bool = False, stats: bool = False) -> dict:
    """Ein Lauf mit den festen Zufalls-Seeds der Linie (Instanz, Starttour und Strom aus Familie, n, Instanz, Lauf)."""
    _, D = instance(familie, n, idx)
    t0 = S.start_tour(D, familie, n, idx, lauf)
    rng = BlockSplitMix64(S.run_seed(familie, n, idx, lauf))
    return run_on(D, t0, rng, zeile, akz, budget, checkpoints, trace, stats)


def shares(apps, evals) -> tuple[list[float], list[float]]:
    """Anteile je Zugart an den Anwendungen und an den Auswertungen (Nullen, wenn nichts gezählt ist)."""
    sa = sum(apps)
    se = sum(evals)
    return [a / sa if sa else 0.0 for a in apps], [e / se if se else 0.0 for e in evals]


def replay(t0, spur, bis_anwendung: int | None = None) -> list[int]:
    """Tour nach `bis_anwendung` Anwendungen: die angenommenen Züge der Spur der Reihe nach auf die Starttour anwenden."""
    from aka_moves import apply_move

    t = list(t0)
    for _used, h, mv, _delta, _cost, _best, k in spur:
        if bis_anwendung is not None and k > bis_anwendung:
            break
        apply_move(t, h, mv)
    return t
