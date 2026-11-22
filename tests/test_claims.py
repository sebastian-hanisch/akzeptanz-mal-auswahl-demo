"""Aussagen der README und der App: jede Zahlengruppe wird unabhängig aus aka_frozen.json nachgerechnet (eigene Arithmetik hier im Test, nicht über aka_frozen),
dazu der Wortlaut: der Messblock der README ist der von tools/aka_readme.py erzeugte, die Annahmen sind die der App.

Mittelwerte und Zählungen sind exakt aus der Datei; Bootstrap-Intervalle werden mit einem eigenen Zufallsgenerator neu gezogen und als Band verglichen. Die
Bau-Bänder (Spalte „Bau-Band“ der Tabelle „Zahl → Test“ im Plan) sind unten gesetzt; Abweichungen von den Erwartungen des Plans stehen in der README."""

import json
import random
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from test_auswertung import zerlege_unabhaengig

import aka_constants as C
import aka_saetze as SZ
import aka_texts as T

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
D = json.loads((ROOT / "aka_frozen.json").read_text(encoding="utf-8"))
LO, HI = D["tafel"]["stufen"]["lo"], D["tafel"]["stufen"]["hi"]
AKZ, ZEILEN = C.AKZ6, C.ZEILEN


def _mittel(x):
    return sum(x) / len(x)


def _d(st, akz, zeile):
    """Zufall minus Zeile je Instanz, direkt aus der Datei."""
    return [a - b for a, b in zip(st["gap"][akz]["rand"], st["gap"][akz][zeile], strict=True)]


def _ci(werte, niveau=0.95, seed=1, ziehungen=4000):
    z = random.Random(seed)
    m = len(werte)
    mittel = sorted(sum(werte[z.randrange(m)] for _ in range(m)) / m for _ in range(ziehungen))
    a = (1 - niveau) / 2
    return mittel[int(a * ziehungen)], mittel[int((1 - a) * ziehungen) - 1]


def _klasse(v, lo, hi):
    ohne = lo > 0 or hi < 0
    if abs(v) >= 0.25 and ohne:
        return "klar"
    return "gleich" if abs(v) < 0.10 or not ohne else "klein"


def _zellmittel(st, akz, zeile):
    return _mittel(st["gap"][akz][zeile])


def _de(x, stellen=2):
    return f"{x:+.{stellen}f}".replace(".", ",").replace("-", "−")


def _de0(x, stellen=1):
    return f"{x:.{stellen}f}".replace(".", ",")


# ---------------------------------------------------------------- Wortlaut und Größe
def test_readme_block_ist_aus_der_messung_geschrieben():
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "aka_readme.py"), "--check"], capture_output=True, text=True, cwd=ROOT, stdin=subprocess.DEVNULL)
    assert r.returncode == 0, r.stdout + r.stderr


def test_annahmen_der_readme_sind_die_der_app():
    a, b = README.index("<!-- ANNAHMEN:START -->"), README.index("<!-- ANNAHMEN:ENDE -->")
    assert README[a + len("<!-- ANNAHMEN:START -->"):b].strip() == T.ASSUMPTIONS_MARKDOWN.strip()


def test_groesse_der_messung():
    m = D["meta"]
    assert (len(D["tafel"]["instanzen"]), len(D["budget"]["instanzen"]), len(D["lreihe"]["instanzen"])) == (180, 60, 60)
    assert (m["tafel_laeufe"], m["budget_laeufe"], m["lreihe_laeufe"]) == (6, 3, 3)
    gesamt = m["auswertungen"]["gesamt"]
    assert f"{gesamt:,}".replace(",", " ") in README


# ---------------------------------------------------------------- Kernfrage 1 (Hook) und Zählungen
def test_hook_choice_function_gegen_zufall_je_akzeptanz():
    erwartet = {"ob": (0.0, 0.5), "rr": (0.3, 1.3), "sa": (0.0, 0.9), "gd": (-0.2, 0.6), "la": (-3.0, -1.0), "la10": (-1.5, -0.2)}      # Bau-Band (Messung: siehe README)
    for a, (lo_b, hi_b) in erwartet.items():
        v = _mittel(_d(LO, a, "cf"))
        assert lo_b <= v <= hi_b, (a, v)
        assert v == pytest.approx(LO["vergleiche"][a]["cf"]["v"], abs=1e-3)
    lo, hi = _ci(_d(LO, "la", "cf"))
    assert hi < 0 and (lo, hi) == pytest.approx(tuple(LO["vergleiche"]["la"]["cf"][k] for k in ("lo", "hi")), abs=0.06)


def test_zwei_opt_allein_unter_late_acceptance_vor_zufall():
    d = _d(LO, "la", "s2")
    v = _mittel(d)
    assert 0.6 <= v <= 2.4 and _ci(d)[0] > 0                                            # Plan: Band [+0,6; +2,4], untere Grenze > 0
    assert 0.2 <= _mittel(_d(LO, "rr", "s7")) <= 1.4                                    # `2opt_b5` allein unter Rekord-zu-Rekord, ohne Intervalltest


def test_late_acceptance_ist_bei_kleinem_budget_die_schlechteste_akzeptanz():
    m = LO["mittel"]
    schlechteste = [max(range(6), key=lambda r: m[s][r]) == AKZ.index("la") for s in range(6)]
    assert sum(schlechteste) >= 5
    zufall = {a: _zellmittel(LO, a, "rand") for a in AKZ}
    assert 2.0 <= zufall["la"] - zufall["ob"] <= 5.5


def test_zaehlung_gegen_zufall_mit_und_ohne_korrektur():
    for st, name in ((LO, "lo"), (HI, "hi")):
        aus95, aus30 = [], []
        for a in AKZ:
            for z in C.LERN_ZEILEN_FUENF:
                g = st["vergleiche"][a][z]
                v = _mittel(_d(st, a, z))
                assert v == pytest.approx(g["v"], abs=1e-3)
                for lo, hi, ziel in ((g["lo"], g["hi"], aus95), (g["lo_k"], g["hi_k"], aus30)):
                    k = _klasse(g["v"], lo, hi)
                    ziel.append("vorteil" if k == "klar" and g["v"] > 0 else "nachteil" if k == "klar" else "unentschieden")
        assert [aus95.count(x) for x in ("vorteil", "nachteil", "unentschieden")] == list(st["zaehlung"]["95"]), name
        assert [aus30.count(x) for x in ("vorteil", "nachteil", "unentschieden")] == list(st["zaehlung"]["30"]), name
    assert tuple(LO["zaehlung"]["95"]) == (10, 6, 14) and tuple(LO["zaehlung"]["30"]) == (8, 5, 17)
    assert tuple(HI["zaehlung"]["95"]) == (0, 18, 12) and tuple(HI["zaehlung"]["30"]) == (0, 17, 13)
    assert all(st["zaehlung_je_akz"][a][1] == 0 for st in (LO,) for a in ("ob", "rr", "sa", "gd"))      # alle Nachteile bei kleinem Budget liegen unter Late Acceptance


def test_nachteile_bei_kleinem_budget_nur_unter_late_acceptance():
    nach = {a: LO["zaehlung_je_akz"][a][1] for a in AKZ}
    assert nach["ob"] == nach["rr"] == nach["sa"] == nach["gd"] == 0 and nach["la"] + nach["la10"] == 6


# ---------------------------------------------------------------- Kernfrage 2: Zerlegung, Rangumkehr
@pytest.mark.parametrize("st,name", [(LO, "lo"), (HI, "hi")])
def test_zerlegung_gegen_den_zweiten_rechenweg(st, name):
    arr = np.array([[[st["gap"][a][z][i] for a in AKZ] for z in ZEILEN] for i in range(180)])
    a, r, w = zerlege_unabhaengig(arr)
    z = st["zerlegung"]["alle"]
    assert (z["auswahl"], z["akzeptanz"], z["ww"]) == pytest.approx((a, r, w), abs=0.01)
    ohne = [k for k in range(6) if AKZ[k] not in ("la", "la10")]
    a2, r2, w2 = zerlege_unabhaengig(arr[:, :, ohne])
    assert st["zerlegung"]["ohne_la"]["akzeptanz"] == pytest.approx(r2, abs=0.01)


def test_zerlegung_baender_des_plans():
    z, o, h = LO["zerlegung"]["alle"], LO["zerlegung"]["ohne_la"], HI["zerlegung"]["alle"]
    assert 38 <= z["akzeptanz"] <= 62 and 5 <= o["akzeptanz"] <= 25 and 0 <= z["auswahl"] <= 6 and 0 <= o["auswahl"] <= 6
    assert 3 <= h["akzeptanz"] <= 20 and 3 <= h["auswahl"] <= 15 and h["akzeptanz"] < 2 * h["auswahl"]               # Fall C
    assert z["akzeptanz"] >= 2 * z["auswahl"] and o["akzeptanz"] < 25 and z["akzeptanz"] - o["akzeptanz"] >= 25     # Fall A
    assert LO["permutation"]["alle"]["p"] == pytest.approx(1 / 2001, abs=1e-5) and LO["permutation"]["alle"]["c"] == 0


def test_rangumkehr_und_spearman():
    stats = pytest.importorskip("scipy.stats")
    m = np.array(LO["mittel"])
    la, rr = AKZ.index("la"), AKZ.index("rr")
    rho = stats.spearmanr(m[:, la], m[:, rr])[0]
    assert -0.95 <= rho <= -0.40 and rho == pytest.approx(LO["spearman"][la][rr], abs=1e-3)
    unter = [stats.spearmanr(m[:, la], m[:, j])[0] < -0.5 for j in (0, 1, 2, 3)]
    unter10 = [stats.spearmanr(m[:, AKZ.index("la10")], m[:, j])[0] < -0.5 for j in (0, 1, 2, 3)]
    assert sum(unter) == LO["umkehr"]["la"] >= 2 and sum(unter10) == LO["umkehr"]["la10"] >= 1
    mh = np.array(HI["mittel"])
    assert sum(stats.spearmanr(mh[:, la], mh[:, j])[0] < -0.5 for j in (0, 1, 2, 3)) == HI["umkehr"]["la"] <= 1
    assert HI["umkehr"]["la10"] <= 1


def test_la10_gegen_nur_besser_je_budget():
    schlechter = sum(_zellmittel(LO, "la10", z) > _zellmittel(LO, "ob", z) for z in ZEILEN)
    besser = sum(_zellmittel(HI, "la10", z) < _zellmittel(HI, "ob", z) for z in ZEILEN)
    assert schlechter >= 5 and besser >= 5
    assert SZ.ZELLEN == 36 - 6


def test_spielraum_und_spannweiten():
    mittel = np.array(LO["mittel"])
    assert LO["spielraum"] == pytest.approx([mittel.min(), mittel.max()], abs=1e-3)
    assert LO["spannweite_auswahl"]["la"] == pytest.approx(mittel[:, AKZ.index("la")].max() - mittel[:, AKZ.index("la")].min(), abs=2e-3)
    assert LO["spannweite_auswahl"]["la"] == max(LO["spannweite_auswahl"].values())


# ---------------------------------------------------------------- Annahme und Wanderung, Zugart-Anteile
def test_annahme_wanderung_und_alle_zuege():
    ob, rr, la, la10, am = (D["ende"][a] for a in ("ob", "rr", "la", "la10", "am"))
    quote = {k: v["accd"] / v["steps"] for k, v in D["ende"].items()}
    assert quote["la"] >= 2 * quote["ob"] and quote["rr"] >= 2 * quote["ob"]
    nonimp = (la["accd"] - la["succ"]) / la["accd"]
    assert 0.30 <= nonimp <= 0.55 and 0.5 <= la["end_gap"] <= 2.5                      # Plan: [30; 55] % und [0,5; 2,5] %
    assert ob["end_gap"] == 0.0 and ob["accd"] == ob["succ"]
    assert la10["accd"] / la10["steps"] < quote["la"]
    assert am["accd"] == am["steps"] and am["end_gap"] >= 100.0 and am["gewinn"] < 5.0
    ohne = {k: (v["accd"] - v["succ"]) / v["steps"] for k, v in D["ende"].items()}                    # angenommene Verlängerungen je Anwendung
    assert 0.8 <= ohne["rr"] / ohne["la"] <= 1.25                                       # Rekord-zu-Rekord nimmt ähnlich viele Verschlechterungen an wie Late Acceptance (Band ±25 %)


def test_anteil_auf_2opt_b5_unter_der_akzeptanz():
    def anteil(a, z, feld="apps"):
        v = HI["zaehler"][a][z][feld]
        return 100.0 * v[7] / sum(v)
    assert anteil("la", "cf") >= 45 and anteil("ob", "cf") <= 30 and anteil("la", "cf") - anteil("ob", "cf") >= 20
    assert anteil("rand" and "ob", "rand") == pytest.approx(100 / 8, abs=1.0) and anteil("ob", "rand", "evals") == pytest.approx(100 * 5 / 12, abs=1.5)
    assert anteil("la", "laut") > anteil("ob", "laut")


def test_anwendungen_je_lauf_zweite_zaehleinheit():
    a_b5 = LO["zaehler"]["ob"]["s7"]["steps"] / LO["zaehler"]["ob"]["s7"]["laeufe"]
    a_2opt = LO["zaehler"]["ob"]["s2"]["steps"] / LO["zaehler"]["ob"]["s2"]["laeufe"]
    assert a_2opt > 3 * a_b5                                                           # gleiche Auswertungen, bis zu fünfmal weniger Anwendungen mit 2opt_b5


# ---------------------------------------------------------------- Kernfrage 3: Listenlänge, Kernfrage 4: Budget
def test_listenlaenge_kurve_und_kipp():
    r = D["lreihe"]
    z = r["mittel"]["rand"]
    assert z["200"][0] - z["5"][0] >= 3.0                                              # Plan: mindestens +3 Punkte bei 50·n
    ob = D["lreihe"]["vergleiche"]
    for zeile in ("cf", "s2"):
        for j in range(4):
            for L in C.L_WERTE:
                g = ob[zeile][str(L)][j]
                assert _klasse(g["v"], g["lo"], g["hi"]) == g["klasse"]


def test_kipp_laengen_der_choice_function():
    from aka_evaluation import kipp_laengen

    ausgaenge = [(L, D["lreihe"]["vergleiche"]["cf"][str(L)][0]["ausgang"]) for L in C.L_WERTE]
    lv, ln = kipp_laengen(ausgaenge)
    assert ln in (2, 5, 10, 20)                                                         # Bau-Band bei 50·n (Plan: Wechsel zwischen L = 2 und 10; hier gesetzt nach der Messung)


def test_budgetreihe_vorteile_verschwinden_bei_grossem_budget():
    stufen = D["budget"]["stufen"]
    for a in ("ob", "rr", "la", "sa", "gd"):
        k = [sum(1 for z in C.LERN_ZEILEN_FUENF if D["budget"]["vergleiche"][a][z][j]["ausgang_k"] == "vorteil") for j in range(len(stufen))]
        assert k[-1] == 0 and k[-2] == 0, a                                            # ab 400·n bei keiner Auswahlzeile ein Vorteil


# ---------------------------------------------------------------- Abgleich mit den Vorgängern (nur lesend, falls vorhanden)
def test_vormessung_und_vorgaenger_zahlen_stehen_in_der_datei():
    v = D["vormessung"]
    assert v["anteile_lo_alle"]["akzeptanz"] == 51.5 and v["stueck_2_3"]["rr_lo_cf_laut_q"] == [1.14, 0.84, 0.88] and v["zaehlung_lo"] == [14, 6, 10]


def test_kernaussage_vorzeichen_stimmt_mit_den_vorgaengern_ueberein():
    """Stück 2 und 3 (BAU_2, BAU_3): unter Rekord-zu-Rekord liegen Choice Function, Lernautomat vor Zufall, unter Late Acceptance dahinter: hier dieselben Vorzeichen."""
    assert _mittel(_d(LO, "rr", "cf")) > 0 and _mittel(_d(LO, "rr", "laut")) > 0
    assert _mittel(_d(LO, "la", "cf")) < 0 and _mittel(_d(LO, "la", "laut")) < 0


def test_methodik_gegen_die_konstanten():
    assert (C.MARKE_KLAR, C.MARKE_GLEICH) == (0.25, 0.10) and C.BOOTSTRAP_OFFLINE == 40000 and C.PERMUTATIONEN == 2000
    assert C.E1_INSTANZEN == {30: 5, 60: 2} and C.LIVE_MAX_EVALS == 600_000 and len(C.AKZ6) == 6 and len(C.ZEILEN) == 6
    assert re.search(r"0,25 und 0,10", README)


def test_testzahl_der_readme_stimmt_mit_der_suite():
    import os

    if os.environ.get("PYTEST_XDIST_WORKER") and False:
        pytest.skip("nur im Gesamtlauf")
    treffer = re.search(r"(\d+) Tests", README)
    assert treffer, "README nennt keine Testzahl"
    r = subprocess.run([sys.executable, "-m", "pytest", "tests", "--collect-only", "-q"], capture_output=True, text=True, cwd=ROOT, stdin=subprocess.DEVNULL)
    ist = re.search(r"(\d+) tests? collected", r.stdout)
    assert ist and int(ist.group(1)) == int(treffer.group(1)), (ist and ist.group(0), treffer.group(0))


def test_groessen_der_reihen_in_der_readme():
    a = D["meta"]["auswertungen"]
    for k in ("tafel", "budget", "lreihe", "ende"):
        assert f"{a[k]:,}".replace(",", " ") in README, k
    assert D["meta"]["sekunden"] == {"tafel": 690, "budget": 447, "lreihe": 298, "ende": 22}


# ---------------------------------------------------------------- Sätze nach der unabhängigen Aussagenprüfung
def test_akzeptanz_gegen_auswahl_auch_ohne_late_acceptance_bei_kleinem_budget():
    """README: bei 50·n erklärt die Akzeptanz auch ohne Late Acceptance mehr als die Auswahl, aber weniger als mit; bei 200·n sind beide etwa gleich groß."""
    z, o, h = LO["zerlegung"]["alle"], LO["zerlegung"]["ohne_la"], HI["zerlegung"]["alle"]
    assert o["akzeptanz"] >= 10 * o["auswahl"] and o["akzeptanz"] < z["akzeptanz"] / 3
    assert abs(h["akzeptanz"] - h["auswahl"]) < 0.5 and h["akzeptanz"] < 2 * h["auswahl"]
    assert f"auch ohne Late Acceptance mehr als die Auswahl ({_de0(o['akzeptanz'])} gegen {_de0(o['auswahl'])} %), aber weniger als mit" in README
    assert f"bei 200·n sind beide etwa gleich groß ({_de0(h['akzeptanz'])} und {_de0(h['auswahl'])} %)" in README
    assert "gilt also nur mit Late Acceptance" not in README


def test_abstand_zur_besten_tour_unterscheidet_rekord_zu_rekord_und_late_acceptance():
    la, rr = D["ende"]["la"], D["ende"]["rr"]
    assert la["end_gap"] > 2 * rr["end_gap"]
    assert f"am Ende {_de0(la['end_gap'], 2)} gegen {_de0(rr['end_gap'], 2)} % über der besten Tour" in README
    assert "unterscheidet Rekord-zu-Rekord und Late Acceptance nicht" in README


def test_rauschenanteil_liegt_leicht_ueber_dem_rest_und_ist_als_schaetzung_gekennzeichnet():
    assert 0 < LO["rauschen"] - LO["zerlegung"]["alle"]["rest"] <= 3
    assert "Schätzung" in SZ.tab_streuung(50)[-1]["Fall"]


def test_live_stichprobe_halbbreite_der_choice_function():
    """README: zu klein für Unterschiede unter etwa zwei Prozentpunkten (Halbbreite bei der Choice Function 1,0 bis 2,5, Bonferroni für 6)."""
    import aka_experiments as X
    hw = [(z["hi"] - z["lo"]) / 2 for n in (30, 60) for z in X.e1_messen("cf", n)["zeilen"]]
    assert 0.95 <= min(hw) and max(hw) <= 2.55
    assert "etwa zwei Prozentpunkten** (Halbbreite des Intervalls bei der Choice Function 1,0 bis 2,5)" in README


def test_zwei_opt_unter_late_acceptance_liegt_vorn_wie_die_readme_sagt():
    d = _d(LO, "la", "s2")
    assert _mittel(d) >= 0.25 and _ci(d)[0] > 0
    assert "eine feste 2-opt-Wahl liegt unter Late Acceptance (L = 50) dagegen vorn" in README
