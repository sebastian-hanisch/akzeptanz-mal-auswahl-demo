"""Lesen der eingefrorenen Messung (aka_frozen.json, erzeugt von tools/aka_make_frozen.py) mit Schemaprüfung.

Aufbau: `tafel` (M-A: sechs Auswahlzeilen x sechs Akzeptanzregeln x zwei Stufen, 180 Instanzen), `budget` (M-B: Stufen 50·n bis 800·n, 60 Instanzen),
`lreihe` (M-C: Listenlänge von Late Acceptance, 60 Instanzen), `vormessung` (Zahlen der Vormessung für den Abschnitt „Befunde und Korrekturen“).
Abstände in Prozent über dem besten bekannten Wert; Unterschied = Abstand(Zufall) - Abstand(Zeile), positiv heißt: die Zeile ist besser."""

import json
from functools import lru_cache
from pathlib import Path

import aka_constants as C

PFAD = Path(__file__).resolve().parent / "aka_frozen.json"
SCHEMA = 1
STUFE_KEY = {50: "lo", 200: "hi"}


@lru_cache(maxsize=1)
def load() -> dict:
    d = json.loads(PFAD.read_text(encoding="utf-8"))
    pruefe(d)
    return d


def pruefe(d: dict) -> None:
    """Schemaprüfung: Version, Teile, Zahl der Instanzen und Zellen."""
    m = d["meta"]
    assert m["schema"] == SCHEMA, f"Schema {m['schema']} statt {SCHEMA}"
    assert m["zufall"].startswith("SplitMix64")
    for teil in ("tafel", "budget", "lreihe", "vormessung"):
        assert teil in d, teil
    n_a = 3 * len(C.N_GEMESSEN) * C.TAFEL_INSTANZEN
    assert len(d["tafel"]["instanzen"]) == n_a and len(d["tafel"]["ref"]) == n_a
    for st in ("lo", "hi"):
        for akz in C.AKZ6:
            for z in C.ZEILEN:
                assert len(d["tafel"]["stufen"][st]["gap"][akz][z]) == n_a
    n_b = 3 * len(C.N_GEMESSEN) * C.BUDGET_INSTANZEN
    assert len(d["budget"]["instanzen"]) == n_b and len(d["lreihe"]["instanzen"]) == 3 * len(C.N_GEMESSEN) * C.LREIHE_INSTANZEN


def meta() -> dict:
    return load()["meta"]


def tafel(faktor: int) -> dict:
    """Die Tafel der Stufe (faktor 50 oder 200)."""
    return load()["tafel"]["stufen"][STUFE_KEY[faktor]]


def tafel_instanzen() -> int:
    return len(load()["tafel"]["instanzen"])


def vergleich(faktor: int, akz: str, zeile: str) -> dict:
    """Gepaarter Vergleich einer Zeile mit Zufall unter einer Akzeptanzregel: v, lo, hi (95 %), lo_k, hi_k (30 Vergleiche), klasse, ausgang (und `_k`)."""
    return tafel(faktor)["vergleiche"][akz][zeile]


def zellmittel(faktor: int, akz: str, zeile: str) -> float:
    t = tafel(faktor)
    return t["mittel"][C.ZEILEN.index(zeile)][C.AKZ6.index(akz)]


def mittel_matrix(faktor: int) -> list[list[float]]:
    return tafel(faktor)["mittel"]


def anteil_b5(faktor: int, akz: str, zeile: str) -> tuple[float, float]:
    """Anteil von 2opt_b5 an Anwendungen und Auswertungen in Prozent (Summe über alle Läufe der Zelle bis zur Stufe)."""
    z = tafel(faktor)["zaehler"][akz][zeile]
    return 100.0 * z["apps"][C.H_2OPT_B5] / sum(z["apps"]), 100.0 * z["evals"][C.H_2OPT_B5] / sum(z["evals"])


def anwendungen_je_lauf(faktor: int, akz: str, zeile: str) -> float:
    z = tafel(faktor)["zaehler"][akz][zeile]
    return z["steps"] / z["laeufe"]


def annahme_kennzahlen(faktor: int, akz: str, zeile: str) -> dict:
    """Annahmequote und Anteil nicht streng verbessernder Annahmen (in Prozent), Abstand der aktuellen zur besten Tour im Mittel über die Anwendungen."""
    z = tafel(faktor)["zaehler"][akz][zeile]
    apps, accd, succ = sum(z["apps"]), sum(z["accd"]), sum(z["succ"])
    return dict(angenommen=100.0 * accd / apps, ohne_verbesserung=100.0 * (accd - succ) / accd if accd else None, wanderung=100.0 * z["wsum"] / z["steps"])


# ---------------------------------------------------------------- Budgetreihe (M-B)
def budget_vergleich(akz: str, zeile: str, j: int) -> dict:
    return load()["budget"]["vergleiche"][akz][zeile][j]


def budget_mittel(akz: str, zeile: str) -> list[float]:
    return load()["budget"]["mittel"][akz][zeile]


def budget_zaehlung(akz: str) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """Je Stufe: (Stufe, Zahl der fünf Zeilen mit Vorteil) und (Stufe, Zahl mit Nachteil) gegen Zufall (Intervall nach Bonferroni für 25 Vergleiche je Stufe)."""
    stufen = load()["budget"]["stufen"]
    vorteil, nachteil = [], []
    for j, s in enumerate(stufen):
        a = [budget_vergleich(akz, z, j)["ausgang_k"] for z in C.LERN_ZEILEN_FUENF]
        vorteil.append((s, a.count("vorteil")))
        nachteil.append((s, a.count("nachteil")))
    return vorteil, nachteil


# ---------------------------------------------------------------- L-Reihe (M-C)
def l_mittel(zeile: str, j: int) -> list[float]:
    """Mittlerer Abstand je Listenlänge (Reihenfolge C.L_WERTE) bei Stufe j."""
    d = load()["lreihe"]["mittel"][zeile]
    return [d[str(L)][j] for L in C.L_WERTE]


def l_vergleich(zeile: str, L: int, j: int) -> dict:
    return load()["lreihe"]["vergleiche"][zeile][str(L)][j]


def l_ausgaenge(zeile: str, j: int) -> list[tuple[int, str]]:
    return [(L, l_vergleich(zeile, L, j)["ausgang"]) for L in C.L_WERTE]


def l_wanderung(zeile: str, L: int, j: int) -> dict:
    z = load()["lreihe"]["wanderung"][zeile][str(L)][j]
    return dict(angenommen=100.0 * z["accd"] / z["steps"], ohne_verbesserung=100.0 * (z["accd"] - z["succ"]) / z["accd"] if z["accd"] else None,
                wanderung=100.0 * z["wsum"] / z["steps"])


def vormessung() -> dict:
    return load()["vormessung"]


# ---------------------------------------------------------------- Ende des Laufs (Zufall, 50·n, 180 Instanzen x 6 Zufalls-Seeds)
def ende(akz: str) -> dict:
    """Mittel über alle Läufe: Abstand der letzten zur besten Tour am Ende in Prozent, angenommen (% der Anwendungen), davon ohne strenge Verbesserung (%), Gewinn gegen die Startlösung (%)."""
    z = load()["ende"][akz]
    return dict(end_gap=z["end_gap"], angenommen=100.0 * z["accd"] / z["steps"], ohne_verbesserung=100.0 * (z["accd"] - z["succ"]) / z["accd"] if z["accd"] else None,
                gewinn=z["gewinn"], laeufe=z["laeufe"])
