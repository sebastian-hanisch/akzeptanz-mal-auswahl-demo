"""App-Tests mit AppTest: jedes Preset, jede Regel unter jeder Akzeptanz, Permalink, Live-Knöpfe, Hinweise statt leerer Vergleiche, Zeitgrenze am Reglermaximum."""

import time
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import aka_constants as C

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _app(**kw) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=300)
    for k, v in kw.items():
        at.session_state[k] = v
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texte(at) -> str:
    return " ".join(e.value for kind in (at.info, at.warning, at.success) for e in kind)


def test_standard_laedt_ohne_fehler_und_zeigt_die_faktenzeile():
    at = _app()
    assert any(e.value.startswith("Beste Tour") for e in at.info)
    assert len(at.metric) >= 5
    assert at.sidebar.selectbox(key="regel_select").value == "cf" and at.sidebar.selectbox(key="akz_select").value == "ob"


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_jedes_preset_laeuft_ohne_skriptfehler(name):
    at = _app()
    at.sidebar.button(key=f"preset_{name}").click().run()
    assert not at.exception, [str(e) for e in at.exception]
    assert any(e.value.startswith("Beste Tour") for e in at.info)
    for key, wert in C.PRESETS[name].items():
        state = {"familie": "familie_select", "n": "n_select", "budget": "budget_select", "instanz": "instanz_input", "lauf": "lauf_input",
                 "regel": "regel_select", "akz": "akz_select", "laenge": "laenge_slider"}[key]
        assert at.session_state[state] == wert, (name, key)


@pytest.mark.parametrize("regel", C.APP_REGELN)
@pytest.mark.parametrize("akz", C.AKZ_APP)
def test_jede_regel_unter_jeder_akzeptanz(regel, akz):
    at = _app()
    at.sidebar.selectbox(key="regel_select").set_value(regel).run()
    at.sidebar.selectbox(key="akz_select").set_value(akz).run()
    assert not at.exception, [str(e) for e in at.exception]
    assert any(e.value.startswith("Beste Tour") for e in at.info)


def test_alle_zuege_annehmen_zeigt_die_letzte_tour_weit_ueber_der_besten():
    at = _app()
    at.sidebar.button(key="preset_Alle Züge annehmen (Gegenprobe)").click().run()
    zeile = next(e.value for e in at.info if e.value.startswith("Beste Tour"))
    assert "100,0 % der Anwendungen angenommen" in zeile
    gap = float(zeile.split("liegt ")[1].split(" %")[0].replace(",", ".").replace("−", "-"))
    assert gap >= 100.0                                                    # Band des Plans: mindestens 100 % über der besten Tour


def test_standardfall_letzte_tour_ist_die_beste():
    at = _app()
    zeile = next(e.value for e in at.info if e.value.startswith("Beste Tour"))
    assert "liegt 0,00 % über der besten" in zeile                          # „nur besser“ ist monoton


def test_permalink_wird_uebernommen_und_begrenzt():
    at = AppTest.from_file(APP, default_timeout=300)
    at.query_params["akz"] = "la"
    at.query_params["laenge"] = "10"
    at.query_params["regel"] = "s2"
    at.query_params["budget"] = "100"
    at.query_params["n"] = "60"
    at.query_params["lauf"] = "999"
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    s = at.session_state
    assert (s["akz_select"], s["laenge_slider"], s["regel_select"], s["budget_select"], s["n_select"], s["lauf_input"]) == ("la", 10, "s2", 100, 60, C.LAUF_MAX)
    assert at.sidebar.slider(key="laenge_slider").disabled is False


def test_schritt_slider_aendert_die_karte_ohne_fehler():
    at = _app()
    at.slider(key="schritt_slider").set_value(35).run()
    assert not at.exception
    assert any("Gezeigt: Tour nach Anwendung" in c.value for c in at.caption)


def test_experiment_1_hinweis_bei_zufall_und_live_rechnung_bei_einer_zeile():
    at = _app()
    at.sidebar.selectbox(key="regel_select").set_value("rand").run()
    assert "Zufall selbst" in _texte(at) and not [b for b in at.button if b.key == "e1_button"]
    at.sidebar.selectbox(key="regel_select").set_value("cf").run()
    at.button(key="e1_button").click().run()
    assert not at.exception, [str(e) for e in at.exception]
    t = _texte(at)
    assert "Choice Function gegen Zufall, Budget 50·n, 15 Instanzen × 2 Zufalls-Seeds" in t
    assert any("Kleine Stichprobe (15 Instanzen × 2 Zufalls-Seeds)" in c.value for c in at.caption)


def test_experiment_1_bei_n_60_nutzt_die_kleinere_stichprobe():
    at = _app()
    at.sidebar.selectbox(key="n_select").set_value(60).run()
    at.button(key="e1_button").click().run()
    assert not at.exception, [str(e) for e in at.exception]
    assert "6 Instanzen × 2 Zufalls-Seeds" in _texte(at)


def test_experiment_5_hinweis_bei_fester_zugart_und_live_bei_lernregel():
    at = _app()
    at.sidebar.selectbox(key="regel_select").set_value("s7").run()
    assert "braucht eine lernende Auswahlregel" in _texte(at) and not [b for b in at.button if b.key == "e5_button"]
    at.sidebar.selectbox(key="regel_select").set_value("laut").run()
    at.button(key="e5_button").click().run()
    assert not at.exception, [str(e) for e in at.exception]
    assert any("Anwendungen" in e.value and "2opt_b5" in e.value for kind in (at.info, at.warning) for e in kind)


def test_eingefrorene_experimente_wechsel_der_regler():
    at = _app()
    at.radio(key="e2_stufe_radio").set_value(200).run()
    assert not at.exception and "Stufe 200·n" in _texte(at)
    at.radio(key="e2_niveau_radio").set_value("je Vergleich").run()
    assert not at.exception
    for s in C.STUFEN_L:
        at.select_slider(key="e3_stufe_select").set_value(s).run()
        assert not at.exception, s
    at.multiselect(key="e3_zeilen_multi").set_value([]).run()
    assert "Mindestens eine Auswahlzeile wählen" in _texte(at)
    at.multiselect(key="e3_zeilen_multi").set_value(["rand"]).run()
    assert not at.exception
    for a in ("ob", "rr", "la", "sa", "gd"):
        at.selectbox(key="e4_akz_select").set_value(a).run()
        assert not at.exception, a


def test_worst_case_am_reglermaximum_mit_zeitgrenze():
    at = _app()
    t = time.time()
    at.sidebar.selectbox(key="n_select").set_value(60).run()
    at.sidebar.select_slider(key="budget_select").set_value(200).run()
    at.sidebar.selectbox(key="akz_select").set_value("la").run()
    at.sidebar.selectbox(key="regel_select").set_value("ucb").run()
    assert not at.exception
    at.button(key="e1_button").click().run()
    at.button(key="e5_button").click().run()
    assert not at.exception, [str(e) for e in at.exception]
    assert time.time() - t < 300


@pytest.mark.parametrize("wert", [C.L_MIN, C.L_MAX])
def test_listenlaenge_am_rand_unter_late_acceptance(wert):
    at = _app()
    at.sidebar.selectbox(key="akz_select").set_value("la").run()
    at.sidebar.slider(key="laenge_slider").set_value(wert).run()
    assert not at.exception, [str(e) for e in at.exception]
    assert any(e.value.startswith("Beste Tour") for e in at.info)
