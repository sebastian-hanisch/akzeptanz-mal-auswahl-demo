"""Layout (DEMO-PLAYBOOK §2): fester Kopf, Schnellstart oben in der Seitenleiste, aktives Beispiel hervorgehoben.

Die Hervorhebung ist zustandslos (`aktives_preset` vergleicht jeden Regler aus SETTING_SPECS mit dem Beispiel). Der Test unten stellt
sicher, dass wirklich JEDER Regler der Seitenleiste dort steht: sonst bliebe das Beispiel trotz Änderung markiert."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import aka_constants as C
import aka_presets as P

APP = str(Path(__file__).resolve().parent.parent / "app.py")
REGLER_ARTEN = ("slider", "number_input", "select_slider", "selectbox", "radio", "toggle", "checkbox", "text_input")


def _app() -> AppTest:
    at = AppTest.from_file(APP, default_timeout=300)
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _typen(at) -> dict:
    """Button-Typ je Beispiel-Name (die Schnellstart-Buttons der Seitenleiste)."""
    return {b.label: b.proto.type for b in at.sidebar.button if b.label in C.PRESETS}


def _regler(at, key):
    for art in REGLER_ARTEN:
        try:
            return getattr(at.sidebar, art)(key=key)
        except KeyError:
            continue
    raise AssertionError(f"Regler {key} steht nicht in der Seitenleiste")


def _anderer_wert(spec, wert):
    if spec.options is not None:
        return next(o for o in spec.options if o != wert)
    return spec.hi if wert != spec.hi else spec.lo


def test_presets_stehen_in_der_seitenleiste_und_nicht_im_hauptbereich():
    at = _app()
    assert [b.label for b in at.sidebar.button][: len(C.PRESETS)] == list(C.PRESETS)  # die ersten Buttons der Seitenleiste
    assert not [b for b in at.main.button if b.label in C.PRESETS]
    assert at.sidebar.button[-1].label == "🎲 Neue Instanz"                # der Zufalls-Button ist das letzte Element


def test_titel_steht_im_festen_kopf():
    at = _app()
    assert "st-key-kopf" in " ".join(h.proto.body for h in at.get("html"))  # das Stylesheet setzt an der Klasse des Containers an
    assert at.title[0].value == "🎚️ Akzeptanz mal Auswahl: wer entscheidet in einer Hyperheuristik?"
    for wort in ("Konfiguration", "Parameterwahl", "Verfahrenswahl", "Wahlregeln"):
        assert wort not in at.title[0].value


def test_beim_start_ist_genau_das_standard_preset_hervorgehoben():
    typen = _typen(_app())
    assert [name for name, typ in typen.items() if typ == "primary"] == [next(iter(C.PRESETS))]


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_angeklicktes_preset_ist_hervorgehoben_und_bleibt_es_im_naechsten_lauf(name):
    at = _app()
    at.sidebar.button(key=f"preset_{name}").click().run()
    assert not at.exception, [str(e) for e in at.exception]
    assert [n for n, typ in _typen(at).items() if typ == "primary"] == [name]
    at.run()
    assert [n for n, typ in _typen(at).items() if typ == "primary"] == [name]


def test_jeder_regler_der_seitenleiste_steht_in_setting_specs():
    at = _app()
    schluessel = {w.key for art in REGLER_ARTEN for w in getattr(at.sidebar, art) if w.key}
    assert schluessel == set(P.SETTING_SPECS)


def test_jeder_regler_der_app_hat_einen_schluessel_und_die_grenzen_aus_dem_presets_modul():
    at = _app()
    bekannt = set(P.SETTING_SPECS) | {"schritt_slider", "e2_stufe_radio", "e2_niveau_radio", "e3_stufe_select", "e3_zeilen_multi", "e4_akz_select"}
    for art in REGLER_ARTEN + ("multiselect",):
        for w in getattr(at, art):
            assert w.key in bekannt, (art, w.label)
    regler = at.sidebar.slider(key="laenge_slider")
    assert (regler.min, regler.max, regler.value) == (*P.bounds("laenge_slider"), P.SETTING_SPECS["laenge_slider"].default)
    for key in ("instanz_input", "lauf_input"):
        feld = at.sidebar.number_input(key=key)
        assert (feld.min, feld.max) == P.bounds(key)
    for key in ("familie_select", "n_select", "akz_select", "regel_select"):
        assert len(at.sidebar.selectbox(key=key).options) == len(P.options(key))
    assert len(at.sidebar.select_slider(key="budget_select").options) == len(P.options("budget_select"))


def test_listenlaenge_ist_nur_unter_late_acceptance_wirksam_und_sonst_gesperrt():
    at = _app()
    assert at.sidebar.selectbox(key="akz_select").value == "ob" and at.sidebar.slider(key="laenge_slider").disabled
    at.sidebar.selectbox(key="akz_select").set_value("la").run()
    assert not at.exception and not at.sidebar.slider(key="laenge_slider").disabled
    at.sidebar.selectbox(key="akz_select").set_value("rr").run()
    assert at.sidebar.slider(key="laenge_slider").disabled


@pytest.mark.parametrize("state_key", list(P.SETTING_SPECS))
def test_jede_aenderung_eines_reglers_hebt_die_hervorhebung_auf(state_key):
    at = _app()
    spec = P.SETTING_SPECS[state_key]
    if state_key == "laenge_slider":          # die Liste zählt nur unter Late Acceptance: dort mit dem Beispiel beginnen, das sie nutzt
        at.sidebar.button(key="preset_Late Acceptance: die Auswahl schadet").click().run()
    regler = _regler(at, state_key)
    regler.set_value(_anderer_wert(spec, regler.value)).run()
    assert not at.exception
    name = next(iter(C.PRESETS))
    if state_key == "laenge_slider":
        name = "Late Acceptance: die Auswahl schadet"
    typen = _typen(at)
    assert typen[name] != "primary"                                  # das Standard-Beispiel ist nicht mehr markiert
    assert list(typen.values()).count("primary") <= 1                # höchstens ein anderes, das genau diese Einstellung ist (z. B. andere Akzeptanz)
    at.sidebar.button(key=f"preset_{name}").click().run()            # erneutes Anklicken markiert wieder
    assert _typen(at)[name] == "primary"


def test_expander_und_kernfragen_in_der_vorgesehenen_reihenfolge():
    at = _app()
    titel = [e.label for e in at.expander]
    for name in ("💬 In einfachen Worten", "So funktioniert eine Hyperheuristik mit getrennter Akzeptanz", "🔬 Weitere Experimente", "📐 Mathematische Formulierung"):
        assert name in titel
    assert titel.index("💬 In einfachen Worten") == 0 and titel[-1] == "📐 Mathematische Formulierung"
    assert titel.index("🔬 Weitere Experimente") < titel.index("📐 Mathematische Formulierung")
    kopf = [s.value for s in at.subheader]
    assert [k[:15] for k in kopf[:4]] == [f"🔬 Kernfrage {i}: "[:15] for i in (0, 1, 2, 3)]
    assert "🚧 Wo die Annahmen enden" in kopf


def test_jeder_abschnitt_nennt_welche_regler_er_benutzt():
    at = _app()
    texte = [c.value for c in at.caption]
    for i in range(5):
        assert any(t.startswith(("Benutzt die Seitenleiste", "Eingefroren")) for t in texte), i
    assert sum(t.startswith("Benutzt die Seitenleiste") for t in texte) >= 2 and sum(t.startswith("Eingefroren") for t in texte) >= 3
