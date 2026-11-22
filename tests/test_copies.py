"""Kopier-Tests: die Rundtour-Module und die Auswahlregeln sind wörtliche Kopien aus auswahlregeln-demo (Stück 3 der Linie), diese wiederum aus
hyperheuristik-demo und zugmenge-demo; die Zufallsvorlage kommt aus dem Website-Repo. Jeweils bis auf das Präfix (QUERENTSCHEIDUNGEN Q2).

Fehlt der Nachbarordner (CI), werden die Tests übersprungen. Eine Korrektur gehört in die Quelle und wird neu kopiert, nicht in die Kopie.
`aka_search.py` ist keine Kopie (eigene Fassung mit Listenlänge L, „alle Züge“ und Zählständen): `tests/quelle_search.py` ist die Kopie der Quelle, und
der Gleichwertigkeitstest unten prüft Bitgleichheit der gemeinsamen Akzeptanzregeln."""

from pathlib import Path

import pytest

import aka_constants as C
from aka_rngblock import BlockSplitMix64

ROOT = Path(__file__).resolve().parent.parent
QUELLE = ROOT.parent / "auswahlregeln-demo"
VORLAGE = ROOT.parent / "sebastianhanisch-website" / "tools" / "templates" / "rng_splitmix64_exact.py"
KOPIEN = ("rng", "rngblock", "scenario", "moves", "accept", "stats", "select", "regeln", "belohnung")
GLEICHE_KONSTANTEN = (
    "HNAMEN", "K", "KOSTEN", "H_2OPT", "H_2OPT_B5", "ALLE_ZUGARTEN", "B5_STICHPROBEN", "LOKAL_LMAX", "FAMILIEN", "FAMILIE_HAND", "SEITE",
    "CLUSTER_ZAHL", "CLUSTER_SIGMA", "GITTER_FAKTOR", "GITTER_RAUSCHEN", "ZWECK_INSTANZ", "ZWECK_START", "ZWECK_LAUF", "ZWECK_BOOT", "EPS",
    "RHO", "LA_LEN", "LA_LEN_KURZ", "GD_END", "SA_T0", "SA_T1", "MARKE_KLAR", "MARKE_GLEICH", "BOOTSTRAP_ZIEHUNGEN",
    "CF_ALPHA", "CF_PHI0", "CF_PHI_ERFOLG", "CF_PHI_SCHRITT", "CF_PHI_MIN", "CF_ZEITFENSTER", "CF_RAUSCHEN", "LAUT_A", "LAUT_BODEN", "Q_EPS", "Q_ALPHA",
    "Q_GAMMA", "UCB_C", "UCB_GAMMA", "PARAMETER", "BELOHNUNGEN", "RANK_FENSTER", "MA_ALPHA", "INSTANZEN_REF",
)


def _text(pfad: Path) -> str:
    return pfad.read_text(encoding="utf-8").replace("\r\n", "\n")


def _konstanten(pfad: Path) -> dict:
    namen: dict = {}
    exec(compile(_text(pfad), str(pfad), "exec"), namen)   # nur Zuweisungen von Konstanten
    return namen


@pytest.mark.parametrize("suffix", KOPIEN)
def test_kopie_stimmt_mit_der_quelle_ueberein_falls_vorhanden(suffix):
    quelle = QUELLE / f"asw_{suffix}.py"
    if not quelle.exists():
        pytest.skip("Quelle nicht vorhanden (CI ohne den Nachbarordner)")
    assert _text(ROOT / f"aka_{suffix}.py") == _text(quelle).replace("asw_", "aka_")


def test_zufallsvorlage_ist_bytegleich_falls_vorhanden():
    if not VORLAGE.exists():
        pytest.skip("Vorlage nicht vorhanden (CI ohne das Website-Repo)")
    assert _text(ROOT / "aka_rng.py") == _text(VORLAGE)


def test_referenzwerte_sind_die_aus_stueck_3_falls_vorhanden():
    quelle = QUELLE / "asw_refs.json"
    if not quelle.exists():
        pytest.skip("Quelle nicht vorhanden (CI ohne den Nachbarordner)")
    assert _text(ROOT / "aka_refs.json") == _text(quelle)


def test_konstanten_der_kopien_haben_die_werte_der_quelle_falls_vorhanden():
    quelle = QUELLE / "asw_constants.py"
    if not quelle.exists():
        pytest.skip("Quelle nicht vorhanden (CI ohne den Nachbarordner)")
    namen = _konstanten(quelle)
    for name in GLEICHE_KONSTANTEN:
        assert getattr(C, name) == namen[name], name


def test_quelle_der_suche_ist_die_kopie_aus_stueck_3_falls_vorhanden():
    quelle = QUELLE / "asw_search.py"
    if not quelle.exists():
        pytest.skip("Quelle nicht vorhanden (CI ohne den Nachbarordner)")
    assert _text(ROOT / "tests" / "quelle_search.py") == _text(quelle).replace("asw_", "aka_")


@pytest.mark.parametrize("akz", ["ob", "rr", "la", "la10", "gd", "sa"])
@pytest.mark.parametrize("zeile", ["rand", "cf", "s7"])
def test_eigene_suche_ist_bitgleich_zur_kopie_fuer_die_gemeinsamen_regeln(akz, zeile):
    import aka_algorithm as A
    import aka_scenario as S
    import quelle_search as Q
    from aka_search import run_search

    for familie in C.FAMILIEN:
        _, D = A.instance(familie, 30, 5)
        t0 = S.start_tour(D, familie, 30, 5, 1)
        gemeinsam = ("best", "final", "used", "steps", "apps", "succ", "accd", "evals", "ck", "best_used", "tour")
        sel_a = A.selector_of(zeile, S.tour_cost(D, t0), 30)
        sel_b = A.selector_of(zeile, S.tour_cost(D, t0), 30)
        arms = A.arms_of(zeile)
        a = run_search(D, t0, 1500, arms, akz, BlockSplitMix64(8), checkpoints=(500, 1000), trace=True, selector=sel_a)
        b = Q.run_search(D, t0, 1500, arms, akz, BlockSplitMix64(8), checkpoints=(500, 1000), trace=True, selector=sel_b)
        for k in gemeinsam:
            assert a[k] == b[k], (akz, zeile, k)
        assert [s[:6] for s in a["trace"]] == b["trace"]
