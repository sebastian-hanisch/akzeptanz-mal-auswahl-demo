"""Orchestrierung der Live-Experimente (Experiment 0, 1 und 5) mit Zählung der Auswertungen vor dem Start.

Alle Läufe benutzen die festen Zufalls-Seeds der Linie (aka_algorithm.run): gleiche Instanz und Starttour und derselbe Zufallsstrom für jede Auswahlzeile
und jede Akzeptanzregel (gepaart). Die eingefrorenen Messreihen liest aka_frozen."""

import aka_algorithm as A
import aka_constants as C
import aka_evaluation as E
import aka_stats as ST


def akz_name(akz: str, laenge: int = C.LA_LEN) -> str:
    """Name der Akzeptanz für die Suche: 'la' mit dem Regler L wird 'la<L>' (L = 50 und 10 sind dieselben Regeln wie 'la' und 'la10')."""
    return f"la{int(laenge)}" if akz == "la" else akz


def ablauf(familie: str, n: int, idx: int, lauf: int, zeile: str, akz: str, faktor: int, laenge: int = C.LA_LEN) -> dict:
    """Experiment 0: ein Lauf mit Spur (angenommene Züge) und den Kennzahlen der Faktenzeile."""
    r = A.run(familie, n, idx, lauf, zeile, akz_name(akz, laenge), faktor * n, trace=True)
    r["kennzahlen"] = E.ablauf_kennzahlen(r["start"], r["best"], r["final"], r["steps"], sum(r["accd"]), sum(r["succ"]))
    return r


def tour_nach(r: dict, k: int) -> list[int]:
    """Tour nach k Anwendungen (Wiedergabe der angenommenen Züge der Spur)."""
    return A.replay(r["t0"], r["trace"], k)


def zugart_anteile(r: dict, k: int):
    """Anteile je Zugart an den Anwendungen bis k aus der Spur nicht ableitbar (nur angenommene Züge); Gesamtanteile des Laufs: (Anwendungen, Auswertungen)."""
    return A.shares(r["apps"], r["evals"])


def _instanz_liste(n: int, anzahl: dict, familien=C.FAMILIEN):
    return [(f, j) for f in familien for j in range(anzahl[n])]


def e1_messen(auswahl: str, n: int, faktor: int = C.E1_BUDGET) -> dict:
    """Experiment 1: die Auswahlzeile gegen Zufall unter jeder der sechs Akzeptanzregeln, gepaart, Intervall nach Bonferroni für 6 Vergleiche.

    Rückgabe: zeilen (je Akzeptanz: Abstand Zufall, Abstand Zeile, v, lo, hi, klasse, ausgang), n_inst, n_laeufe, kosten (Auswertungen)."""
    assert auswahl != "rand"
    budget = faktor * n
    inst = _instanz_liste(n, C.E1_INSTANZEN)
    kosten = 0
    gaps = {a: {"rand": [], auswahl: []} for a in C.AKZ6}
    for familie, idx in inst:
        runs = {a: {z: [A.run(familie, n, idx, lauf, z, a, budget) for lauf in range(C.E1_LAEUFE)] for z in ("rand", auswahl)} for a in C.AKZ6}
        alle = [r["best"] for a in runs.values() for z in a.values() for r in z]
        kosten += sum(r["used"] for a in runs.values() for z in a.values() for r in z)
        ref = min(A.reference(familie, n, idx), min(alle))
        for a in C.AKZ6:
            for z in ("rand", auswahl):
                gaps[a][z].append(sum(ST.gap(r["best"], ref) for r in runs[a][z]) / C.E1_LAEUFE)
    zeilen = []
    for a in C.AKZ6:
        v = E.vergleich_gegen_zufall(gaps[a]["rand"], gaps[a][auswahl], C.ZWECK_BOOT, C.BOOTSTRAP_LIVE, len(C.AKZ6))
        zeilen.append(dict(akz_key=a, akz=C.AKZ_KURZ[a], abstand_zufall=sum(gaps[a]["rand"]) / len(inst), abstand_zeile=sum(gaps[a][auswahl]) / len(inst),
                           v=v["v"], lo=v["lo"], hi=v["hi"], klasse=v["klasse"], ausgang=v["ausgang"]))
    return dict(zeilen=zeilen, n_inst=len(inst), n_laeufe=C.E1_LAEUFE, kosten=kosten, je_instanz=gaps)


def e5_messen(regel: str, n: int, faktor: int) -> dict:
    """Experiment 5: die Lernregel unter „nur besser“, Rekord-zu-Rekord und Late Acceptance (L = 50), Anteile je Zugart (Summe über alle Läufe)."""
    assert regel in C.LERN_REGELN_APP
    budget = faktor * n
    inst = _instanz_liste(n, C.E5_INSTANZEN)
    out = {}
    kosten = 0
    for a in C.E5_AKZ:
        apps, evals = [0] * C.K, [0] * C.K
        for familie, idx in inst:
            for lauf in range(C.E5_LAEUFE):
                r = A.run(familie, n, idx, lauf, regel, a, budget)
                apps = [x + y for x, y in zip(apps, r["apps"], strict=True)]
                evals = [x + y for x, y in zip(evals, r["evals"], strict=True)]
                kosten += r["used"]
        out[a] = dict(apps=apps, evals=evals, b5=E.anteil_b5(apps, evals))
    return dict(akz=out, n_inst=len(inst), n_laeufe=C.E5_LAEUFE, kosten=kosten)
