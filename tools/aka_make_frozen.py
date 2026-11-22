"""Erzeugt aka_frozen.json (eingefrorene Messreihen M-A bis M-C) mit dem SplitMix64-Strom der Demo.

    python tools/aka_make_frozen.py messen --teil tafel|budget|lreihe [--procs 2]   rechnet eine Reihe, Rohdaten nach %TEMP%/sh-tests/aka_roh
    python tools/aka_make_frozen.py bauen                                           wertet die Rohdaten aus und schreibt aka_frozen.json
    python tools/aka_make_frozen.py --check                                         rechnet drei Instanzen der Tafel neu und vergleicht als Band

Reihen (Plan 04, Bau-Vormessung): M-A Tafel 6 Auswahlzeilen x 6 Akzeptanzregeln x 2 Stufen, 180 Instanzen (Familie x n x Instanzen 100 bis 129),
6 Zufalls-Seeds; M-B Budgetreihe 6 Zeilen x 5 Akzeptanzregeln x 5 Stufen, 60 Instanzen (130 bis 139), 3 Zufalls-Seeds; M-C Listenlänge von
Late Acceptance 5 Zeilen x 10 Längen x 4 Stufen, 60 Instanzen (140 bis 149), 3 Zufalls-Seeds. Referenz je Instanz = Minimum aus aka_refs.json und
allen Läufen der Reihe. Abstand in Prozent. Alle Zufalls-Seeds kommen aus aka_scenario.derive (Zweck, Familie, n, Instanz, Lauf), nie aus hash()."""

import argparse
import json
import multiprocessing
import os
import pickle
import platform
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import aka_algorithm as A  # noqa: E402
import aka_constants as C  # noqa: E402
import aka_evaluation as E  # noqa: E402
import aka_stats as ST  # noqa: E402

ROH = Path(os.environ.get("AKA_ROH", Path(tempfile.gettempdir()) / "sh-tests" / "aka_roh"))
AUSGABE = ROOT / "aka_frozen.json"
SCHEMA = 1
AKZ_EIN_LAUF = ("ob", "rr", "la", "la10")          # Ergebnis bis zu einer Auswertungszahl hängt nicht am Gesamtbudget: ein Lauf mit Kontrollpunkten
AKZ_JE_STUFE = ("sa", "gd")                        # Plan hängt am Gesamtbudget: eigener Lauf je Stufe

# Zahlen der Vormessung (M1b, numpy.default_rng) und der Vorgänger-Stücke (SplitMix64) für den Abschnitt „Befunde und Korrekturen“
VORMESSUNG = {
    "quelle": "VORMESSUNG_NACHMESSUNG_M1.md (M1b, numpy.default_rng, 180 Instanzen x 6 Zufalls-Seeds)",
    "cf_gegen_zufall_lo": {"ob": 0.29, "rr": 0.74, "sa": 0.42, "gd": 0.34, "la": -1.97, "la10": -0.66},
    "anteile_lo_alle": {"auswahl": 1.3, "akzeptanz": 51.5, "ww": 5.8, "rest": 41.4},
    "anteile_lo_ohne_la": {"auswahl": 1.5, "akzeptanz": 13.4, "ww": 0.6, "rest": 84.5},
    "anteile_hi_alle": {"auswahl": 8.5, "akzeptanz": 11.2, "ww": 8.8, "rest": 71.5},
    "spearman_la_lo": {"ob": -0.37, "rr": -0.83, "sa": -0.60, "gd": -0.66},
    "spearman_la10_lo": {"ob": -0.20, "rr": -0.71, "sa": -0.54, "gd": -0.49},
    "zaehlung_lo": [14, 6, 10], "zaehlung_hi": [0, 16, 14],
    "la_minus_ob_zufall_lo": 3.51,
    "stueck_2_3": {"rr_lo_cf_laut_q": [1.14, 0.84, 0.88], "rr_lo_ucb": 0.51, "la_lo_cf_laut_q": [-1.57, -1.18, -1.36],
                   "quelle": "BAU_3.md, BAU_2.md (SplitMix64, 120 Instanzen x 3 Läufe)"},
}


# ---------------------------------------------------------------- Aufgaben (je Instanz alle Läufe; laufen in Unterprozessen)
def _snap(ck_stat, i):
    s = ck_stat[i]
    return dict(steps=s[0], apps=s[1], evals=s[2], accd=s[3], succ=s[4], wsum=s[5])


def tafel_task(arg):
    familie, n, idx = arg
    lo, hi = C.STUFEN_TAFEL[0] * n, C.STUFEN_TAFEL[1] * n
    bests, stats = {}, {}
    for lauf in range(C.TAFEL_LAEUFE):
        for zeile in C.ZEILEN:
            for akz in AKZ_EIN_LAUF:
                r = A.run(familie, n, idx, lauf, zeile, akz, hi, checkpoints=(lo, hi), stats=True)
                for j in (0, 1):
                    bests.setdefault((j, akz, zeile), []).append(r["ck"][j])
                    stats.setdefault((j, akz, zeile), []).append(_snap(r["ck_stat"], j))
            for akz in AKZ_JE_STUFE:
                for j, b in enumerate((lo, hi)):
                    r = A.run(familie, n, idx, lauf, zeile, akz, b, checkpoints=(b,), stats=True)
                    bests.setdefault((j, akz, zeile), []).append(r["ck"][0])
                    stats.setdefault((j, akz, zeile), []).append(_snap(r["ck_stat"], 0))
        r = A.run(familie, n, idx, lauf, "rand", "am", hi, checkpoints=(lo, hi), stats=True)      # Gegenprobe: alle Züge annehmen
        for j in (0, 1):
            bests.setdefault((j, "am", "rand"), []).append(r["ck"][j])
            stats.setdefault((j, "am", "rand"), []).append(_snap(r["ck_stat"], j))
    return (familie, n, idx), bests, stats


def budget_task(arg):
    familie, n, idx = arg
    fs = [f * n for f in C.STUFEN_BUDGET]
    bests = {}
    for lauf in range(C.BUDGET_LAEUFE):
        for zeile in C.ZEILEN:
            for akz in C.BUDGETFREI:
                r = A.run(familie, n, idx, lauf, zeile, akz, fs[-1], checkpoints=tuple(fs))
                bests.setdefault((akz, zeile), []).append(list(r["ck"]))
            for akz in AKZ_JE_STUFE:
                zeilen = []
                for b in fs:
                    r = A.run(familie, n, idx, lauf, zeile, akz, b, checkpoints=(b,))
                    zeilen.append(r["ck"][0])
                bests.setdefault((akz, zeile), []).append(zeilen)
    return (familie, n, idx), bests


def lreihe_task(arg):
    familie, n, idx = arg
    fs = [f * n for f in C.STUFEN_L]
    bests, stats = {}, {}
    for lauf in range(C.LREIHE_LAEUFE):
        for zeile in C.L_ZEILEN:
            for L in C.L_WERTE:
                r = A.run(familie, n, idx, lauf, zeile, f"la{L}", fs[-1], checkpoints=tuple(fs), stats=True)
                bests.setdefault((zeile, L), []).append(list(r["ck"]))
                stats.setdefault((zeile, L), []).append([_snap(r["ck_stat"], j) for j in range(len(fs))])
    return (familie, n, idx), bests, stats


def ende_task(arg):
    """Zufall unter allen Akzeptanzregeln (und der Gegenprobe) bei 50·n: Abstand der letzten zur besten Tour am Ende des Laufs in Prozent, Annahmen."""
    familie, n, idx = arg
    b = C.STUFEN_TAFEL[0] * n
    out = {}
    for lauf in range(C.TAFEL_LAEUFE):
        for akz in C.AKZ6 + ("am",):
            r = A.run(familie, n, idx, lauf, "rand", akz, b)
            out.setdefault(akz, []).append(dict(end_gap=100.0 * (r["final"] - r["best"]) / r["best"], steps=r["steps"], accd=sum(r["accd"]), succ=sum(r["succ"]),
                                                gewinn=100.0 * (r["start"] - r["best"]) / r["start"]))
    return (familie, n, idx), out


def instanzen(start: int, m: int):
    return [(f, n, start + j) for f in C.FAMILIEN for n in C.N_GEMESSEN for j in range(m)]


TEILE = {
    "tafel": (tafel_task, instanzen(C.TAFEL_START, C.TAFEL_INSTANZEN)),
    "budget": (budget_task, instanzen(C.BUDGET_START, C.BUDGET_INSTANZEN)),
    "lreihe": (lreihe_task, instanzen(C.LREIHE_START, C.LREIHE_INSTANZEN)),
    "ende": (ende_task, instanzen(C.TAFEL_START, C.TAFEL_INSTANZEN)),
}


def messen(teil: str, procs: int) -> None:
    fn, tasks = TEILE[teil]
    ROH.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    out = []
    with multiprocessing.Pool(procs) as pool:
        for i, res in enumerate(pool.imap_unordered(fn, tasks, chunksize=1), 1):
            out.append(res)
            if i % 10 == 0 or i == len(tasks):
                print(f"{teil}: {i}/{len(tasks)} Instanzen, {time.time() - t0:.0f} s", flush=True)
    out.sort(key=lambda r: r[0])
    with open(ROH / f"{teil}.pkl", "wb") as f:
        pickle.dump(dict(ergebnis=out, sekunden=time.time() - t0), f)
    print(f"{teil}: fertig in {time.time() - t0:.0f} s, Rohdaten {ROH / (teil + '.pkl')}")


# ---------------------------------------------------------------- Auswertung
def _lade(teil):
    with open(ROH / f"{teil}.pkl", "rb") as f:
        return pickle.load(f)


def _ref(familie, n, idx, alle_bests):
    return min(A.reference(familie, n, idx), min(alle_bests))


def _r(x, k=4):
    return round(float(x), k)


def _vergleich_dict(zufall, regel, vergleiche, ziehungen=C.BOOTSTRAP_OFFLINE):
    v95 = E.vergleich_gegen_zufall(zufall, regel, C.ZWECK_BOOT, ziehungen, 1)
    vk = E.vergleich_gegen_zufall(zufall, regel, C.ZWECK_BOOT, ziehungen, vergleiche)
    return dict(v=_r(v95["v"]), lo=_r(v95["lo"]), hi=_r(v95["hi"]), klasse=v95["klasse"], ausgang=v95["ausgang"],
                lo_k=_r(vk["lo"]), hi_k=_r(vk["hi"]), klasse_k=vk["klasse"], ausgang_k=vk["ausgang"], vergleiche_k=vergleiche)


def bau_tafel(roh):
    import numpy as np

    res = roh["ergebnis"]
    inst = [r[0] for r in res]
    refs, gap, var, zaehler = [], {}, {}, {}
    for (familie, n, idx), bests, stats in res:
        alle = [b for v in bests.values() for b in v]
        ref = _ref(familie, n, idx, alle)
        refs.append(ref)
        for (j, akz, zeile), b in bests.items():
            g = [ST.gap(x, ref) for x in b]
            m = sum(g) / len(g)
            gap.setdefault((j, akz, zeile), []).append(m)
            var.setdefault((j, akz, zeile), []).append(sum((x - m) ** 2 for x in g) / (len(g) - 1))
        for key, snaps in stats.items():
            z = zaehler.setdefault(key, dict(apps=[0] * 8, evals=[0] * 8, accd=[0] * 8, succ=[0] * 8, steps=0, wsum=0.0, laeufe=0))
            for s in snaps:
                for fld in ("apps", "evals", "accd", "succ"):
                    z[fld] = [a + b for a, b in zip(z[fld], s[fld], strict=True)]
                z["steps"] += s["steps"]
                z["wsum"] += s["wsum"]
                z["laeufe"] += 1
    n_i = len(inst)
    out = dict(instanzen=[list(i) for i in inst], ref=[_r(x, 6) for x in refs],
               unterboten=sum(1 for (f, n, i), r in zip(inst, refs, strict=True) if r < A.reference(f, n, i) - 1e-6))
    stufen = {}
    for j, name in enumerate(("lo", "hi")):
        gj, vj, zj = {}, {}, {}
        for akz in C.AKZ6 + ("am",):
            zeilen = C.ZEILEN if akz != "am" else ("rand",)
            gj[akz] = {z: [_r(x) for x in gap[(j, akz, z)]] for z in zeilen}
            vj[akz] = {z: [_r(x, 5) for x in var[(j, akz, z)]] for z in zeilen}
            zj[akz] = {z: dict(apps=zaehler[(j, akz, z)]["apps"], evals=zaehler[(j, akz, z)]["evals"], accd=zaehler[(j, akz, z)]["accd"],
                               succ=zaehler[(j, akz, z)]["succ"], steps=zaehler[(j, akz, z)]["steps"], wsum=_r(zaehler[(j, akz, z)]["wsum"], 3),
                               laeufe=zaehler[(j, akz, z)]["laeufe"]) for z in zeilen}
        arr = np.array([[[gj[a][z][i] for a in C.AKZ6] for z in C.ZEILEN] for i in range(n_i)])      # Instanzen x Zeile x Akzeptanz
        var_arr = np.array([[[vj[a][z][i] for a in C.AKZ6] for z in C.ZEILEN] for i in range(n_i)])
        mittel = arr.mean(axis=0)
        la, la10 = C.AKZ6.index("la"), C.AKZ6.index("la10")
        ohne_la = [k for k in range(6) if k not in (la, la10)]
        ohne_la10 = [k for k in range(6) if k != la10]
        zer = {"alle": E.zerlege(arr), "ohne_la": E.zerlege(arr[:, :, ohne_la]), "ohne_la10": E.zerlege(arr[:, :, ohne_la10])}
        perm = {"alle": E.permutationstest(arr), "ohne_la": E.permutationstest(arr[:, :, ohne_la])}
        sm = E.spearman_matrix(mittel)
        vgl = {a: {z: _vergleich_dict([gj[a]["rand"][i] for i in range(n_i)], [gj[a][z][i] for i in range(n_i)], 30)
                   for z in C.LERN_ZEILEN_FUENF} for a in C.AKZ6}
        stufen[name] = dict(
            gap=gj, var=vj, zaehler=zj, mittel=[[_r(x) for x in row] for row in mittel],
            zerlegung={k: {a: _r(b, 3) for a, b in v.items() if a != "ss"} for k, v in zer.items()},
            rauschen=_r(E.rauschanteil(arr, var_arr, C.TAFEL_LAEUFE), 3),
            permutation={k: dict(p=_r(v["p"], 5), c=v["c"], vertauschungen=v["vertauschungen"]) for k, v in perm.items()},
            spearman=[[_r(x, 3) for x in row] for row in sm],
            umkehr={"la": E.umkehr(sm, la, ohne_la), "la10": E.umkehr(sm, la10, ohne_la)},
            vergleiche=vgl,
            zaehlung={"95": E.zaehle(vgl[a][z]["ausgang"] for a in C.AKZ6 for z in C.LERN_ZEILEN_FUENF),
                      "30": E.zaehle(vgl[a][z]["ausgang_k"] for a in C.AKZ6 for z in C.LERN_ZEILEN_FUENF)},
            zaehlung_je_akz={a: E.zaehle(vgl[a][z]["ausgang"] for z in C.LERN_ZEILEN_FUENF) for a in C.AKZ6},
            zaehlung_je_akz_30={a: E.zaehle(vgl[a][z]["ausgang_k"] for z in C.LERN_ZEILEN_FUENF) for a in C.AKZ6},
            spannweite_auswahl={a: _r(mittel[:, k].max() - mittel[:, k].min(), 3) for k, a in enumerate(C.AKZ6)},
            spannweite_akzeptanz={z: _r(mittel[s, :].max() - mittel[s, :].min(), 3) for s, z in enumerate(C.ZEILEN)},
            spielraum=[_r(mittel.min(), 3), _r(mittel.max(), 3)],
        )
    out["stufen"] = stufen
    return out


def bau_budget(roh):
    res = roh["ergebnis"]
    inst = [r[0] for r in res]
    gap = {}
    nst = len(C.STUFEN_BUDGET)
    for (familie, n, idx), bests in res:
        alle = [x for v in bests.values() for lauf in v for x in lauf]
        ref = _ref(familie, n, idx, alle)
        for key, laeufe in bests.items():
            for jj in range(nst):
                g = [ST.gap(lauf[jj], ref) for lauf in laeufe]
                gap.setdefault((key, jj), []).append(sum(g) / len(g))
    akz_liste = ("ob", "rr", "la", "sa", "gd")
    out = dict(instanzen=[list(i) for i in inst], stufen=list(C.STUFEN_BUDGET), akzeptanzen=list(akz_liste), gap={}, vergleiche={}, mittel={})
    for a in akz_liste:
        out["gap"][a] = {z: [[_r(gap[((a, z), jj)][i]) for jj in range(nst)] for i in range(len(inst))] for z in C.ZEILEN}
        out["mittel"][a] = {z: [_r(sum(gap[((a, z), jj)]) / len(inst)) for jj in range(nst)] for z in C.ZEILEN}
        out["vergleiche"][a] = {z: [_vergleich_dict(gap[((a, "rand"), jj)], gap[((a, z), jj)], 25) for jj in range(nst)] for z in C.LERN_ZEILEN_FUENF}
    return out


def bau_lreihe(roh):
    res = roh["ergebnis"]
    inst = [r[0] for r in res]
    gap, zaehl = {}, {}
    nst = len(C.STUFEN_L)
    for (familie, n, idx), bests, stats in res:
        alle = [x for v in bests.values() for lauf in v for x in lauf]
        ref = _ref(familie, n, idx, alle)
        for key, laeufe in bests.items():
            for jj in range(nst):
                g = [ST.gap(lauf[jj], ref) for lauf in laeufe]
                gap.setdefault((key, jj), []).append(sum(g) / len(g))
            for lauf in stats[key]:
                for jj in range(nst):
                    z = zaehl.setdefault((key, jj), dict(steps=0, accd=0, succ=0, wsum=0.0, laeufe=0))
                    s = lauf[jj]
                    z["steps"] += s["steps"]
                    z["accd"] += sum(s["accd"])
                    z["succ"] += sum(s["succ"])
                    z["wsum"] += s["wsum"]
                    z["laeufe"] += 1
    out = dict(instanzen=[list(i) for i in inst], stufen=list(C.STUFEN_L), laengen=list(C.L_WERTE), zeilen=list(C.L_ZEILEN), gap={}, mittel={},
               vergleiche={}, wanderung={})
    for z in C.L_ZEILEN:
        out["gap"][z] = {str(L): [[_r(gap[((z, L), jj)][i]) for jj in range(nst)] for i in range(len(inst))] for L in C.L_WERTE}
        out["mittel"][z] = {str(L): [_r(sum(gap[((z, L), jj)]) / len(inst)) for jj in range(nst)] for L in C.L_WERTE}
        out["wanderung"][z] = {str(L): [{k: (_r(v, 3) if k == "wsum" else v) for k, v in zaehl[((z, L), jj)].items()} for jj in range(nst)] for L in C.L_WERTE}
        if z != "rand":
            out["vergleiche"][z] = {str(L): [_vergleich_dict(gap[(("rand", L), jj)], gap[((z, L), jj)], 1) for jj in range(nst)] for L in C.L_WERTE}
    return out


def bau_ende(roh):
    """Mittel über alle Läufe (180 Instanzen x 6 Zufalls-Seeds): letzte über der besten Tour am Ende, Annahmen, strenge Verbesserungen, Gewinn gegen die Startlösung."""
    summe = {}
    for _inst, out in roh["ergebnis"]:
        for akz, laeufe in out.items():
            z = summe.setdefault(akz, dict(end_gap=0.0, steps=0, accd=0, succ=0, gewinn=0.0, laeufe=0))
            for r in laeufe:
                z["end_gap"] += r["end_gap"]
                z["steps"] += r["steps"]
                z["accd"] += r["accd"]
                z["succ"] += r["succ"]
                z["gewinn"] += r["gewinn"]
                z["laeufe"] += 1
    return {akz: dict(end_gap=_r(z["end_gap"] / z["laeufe"], 4), steps=z["steps"], accd=z["accd"], succ=z["succ"], gewinn=_r(z["gewinn"] / z["laeufe"], 4), laeufe=z["laeufe"])
            for akz, z in summe.items()}


def auswertungen_gesamt() -> dict:
    """Gerechnete Auswertungen je Reihe (aus dem Plan der Läufe: Läufe x Budget)."""
    ta = 0
    for _f, n, _i in instanzen(C.TAFEL_START, C.TAFEL_INSTANZEN):
        ta += C.TAFEL_LAEUFE * len(C.ZEILEN) * (len(AKZ_EIN_LAUF) * 200 * n + len(AKZ_JE_STUFE) * 250 * n) + C.TAFEL_LAEUFE * 200 * n
    bu = sum(C.BUDGET_LAEUFE * len(C.ZEILEN) * (len(C.BUDGETFREI) * 800 * n + len(AKZ_JE_STUFE) * sum(C.STUFEN_BUDGET) * n)
             for _f, n, _i in instanzen(C.BUDGET_START, C.BUDGET_INSTANZEN))
    lr = sum(C.LREIHE_LAEUFE * len(C.L_ZEILEN) * len(C.L_WERTE) * 400 * n for _f, n, _i in instanzen(C.LREIHE_START, C.LREIHE_INSTANZEN))
    en = sum(C.TAFEL_LAEUFE * (len(C.AKZ6) + 1) * 50 * n for _f, n, _i in instanzen(C.TAFEL_START, C.TAFEL_INSTANZEN))
    return dict(tafel=ta, budget=bu, lreihe=lr, ende=en, gesamt=ta + bu + lr + en)


def bauen() -> None:
    meta = dict(schema=SCHEMA, zufall="SplitMix64 (aka_rng, aka_rngblock)", python=platform.python_version(), system=platform.system(),
                datum=time.strftime("%Y-%m-%d"), akzeptanzen=list(C.AKZ6), zeilen=list(C.ZEILEN), stufen_tafel=list(C.STUFEN_TAFEL),
                tafel_laeufe=C.TAFEL_LAEUFE, budget_laeufe=C.BUDGET_LAEUFE, lreihe_laeufe=C.LREIHE_LAEUFE,
                bootstrap_ziehungen=C.BOOTSTRAP_OFFLINE, permutationen=C.PERMUTATIONEN, tafel_start=C.TAFEL_START, budget_start=C.BUDGET_START,
                lreihe_start=C.LREIHE_START, referenz="Minimum aus aka_refs.json und allen Läufen der Reihe")
    teile, sek = {}, {}
    for name, bau in (("tafel", bau_tafel), ("budget", bau_budget), ("lreihe", bau_lreihe), ("ende", bau_ende)):
        roh = _lade(name)
        teile[name] = bau(roh)
        sek[name] = round(roh["sekunden"])
    meta["sekunden"] = sek
    meta["auswertungen"] = auswertungen_gesamt()
    daten = dict(meta=meta, tafel=teile["tafel"], budget=teile["budget"], lreihe=teile["lreihe"], ende=teile["ende"], vormessung=VORMESSUNG)
    AUSGABE.write_text(json.dumps(daten, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"geschrieben: {AUSGABE} ({AUSGABE.stat().st_size / 1024:.0f} KB), Auswertungen {meta['auswertungen']['gesamt']:,}")


def check() -> None:
    d = json.loads(AUSGABE.read_text(encoding="utf-8"))
    ok = 0
    proben = (("gleich", 30, 100), ("cluster", 60, 101), ("gitter", 30, 102))
    inst = [tuple(x) for x in d["tafel"]["instanzen"]]
    for familie, n, idx in proben:
        i = inst.index((familie, n, idx))
        ref = d["tafel"]["ref"][i]
        for zeile, akz in (("rand", "ob"), ("cf", "la"), ("s2", "rr")):
            g = [ST.gap(A.run(familie, n, idx, lauf, zeile, akz, 50 * n)["best"], ref) for lauf in range(C.TAFEL_LAEUFE)]
            neu = sum(g) / len(g)
            alt = d["tafel"]["stufen"]["lo"]["gap"][akz][zeile][i]
            band = max(0.05, 3 * (d["tafel"]["stufen"]["lo"]["var"][akz][zeile][i] / C.TAFEL_LAEUFE) ** 0.5)
            gut = abs(neu - alt) <= band
            print(f"{familie} {n} {idx} {zeile:5s} {akz:3s} alt {alt:8.4f} neu {neu:8.4f} Band {band:.3f}", "ok" if gut else "ABWEICHUNG")
            ok += gut
    print(f"{ok} von 9 im Band")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("befehl", nargs="?", choices=("messen", "bauen"))
    ap.add_argument("--teil", choices=tuple(TEILE))
    ap.add_argument("--procs", type=int, default=2)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        check()
    elif a.befehl == "messen":
        messen(a.teil, a.procs)
    elif a.befehl == "bauen":
        bauen()
    else:
        ap.print_help()
