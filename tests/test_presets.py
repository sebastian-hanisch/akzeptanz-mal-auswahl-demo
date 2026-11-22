"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, erwartete Verdikt-Zeile je Preset als Band (Klassen als Menge).

Die Live-Stichprobe von Kernfrage 1 ist klein (15 Instanzen × 2 Zufalls-Seeds bei n = 30, Intervalle nach Bonferroni für 6 Vergleiche): die Presets nehmen deshalb
die erlaubten Klassen als Menge, nicht eine einzelne. Der Unterschied zur eingefrorenen Messung (180 Instanzen) ist der Zweck der Warnung in der App."""

import pytest

import aka_constants as C
import aka_evaluation as E
import aka_experiments as X
import aka_frozen as F
import aka_presets as P


def test_jedes_preset_hat_hilfe_und_alle_schluessel():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name] and "Kein Preset nimmt ein Ergebnis vorweg" in C.PRESET_HELP[name]


def test_preset_werte_liegen_in_den_reglergrenzen():
    for name, p in C.PRESETS.items():
        assert p["familie"] in C.FAMILIEN and p["n"] in C.N_GEMESSEN and p["budget"] in C.BUDGET_LIVE, name
        assert p["regel"] in C.APP_REGELN and p["akz"] in C.AKZ_APP and C.L_MIN <= p["laenge"] <= C.L_MAX, name
        assert 0 <= p["instanz"] <= C.INSTANZ_MAX and 0 <= p["lauf"] <= C.LAUF_MAX, name


def test_standard_preset_ist_die_erste_zeile_und_gleich_den_standardwerten():
    erstes = C.PRESETS[next(iter(C.PRESETS))]
    assert erstes == {"familie": C.DEFAULT_FAMILIE, "n": C.DEFAULT_N, "budget": C.DEFAULT_BUDGET, "instanz": C.DEFAULT_INSTANZ, "lauf": C.DEFAULT_LAUF,
                      "regel": C.DEFAULT_REGEL, "akz": C.DEFAULT_AKZ, "laenge": C.LA_LEN}


def test_setting_specs_decken_jeden_preset_schluessel_ab():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


@pytest.mark.parametrize("wert,erwartet", [(5, 5), (0, 1), (999, 200), (1, 1)])
def test_clamp_der_listenlaenge(wert, erwartet):
    assert P.clamp(P.SETTING_SPECS["laenge_slider"], wert) == erwartet


def test_clamp_rastet_auswahlwerte_ein():
    assert P.clamp(P.SETTING_SPECS["n_select"], 58) == 60 and P.clamp(P.SETTING_SPECS["budget_select"], 120) == 100
    assert P.clamp(P.SETTING_SPECS["akz_select"], "xx") is None and P.clamp(P.SETTING_SPECS["akz_select"], "la") == "la"


# ---------------------------------------------------------------- erwartete Verdikt-Zeile je Preset (Band)
def _e0(preset):
    p = C.PRESETS[preset]
    return X.ablauf(p["familie"], p["n"], p["instanz"], p["lauf"], p["regel"], p["akz"], p["budget"], p["laenge"])


def test_preset_standardfall_letzte_tour_ist_die_beste():
    r = _e0("Standardfall: Choice Function, nur besser")
    assert r["kennzahlen"]["end_gap"] == pytest.approx(0.0, abs=1e-9) and r["kennzahlen"]["nonimp_pct"] == 0.0


def test_preset_late_acceptance_zeigt_annahme_und_wanderung():
    r = _e0("Late Acceptance: die Auswahl schadet")
    k = r["kennzahlen"]
    ob = _e0("Standardfall: Choice Function, nur besser")["kennzahlen"]
    assert k["acc_pct"] > ob["acc_pct"] and k["nonimp_pct"] > 20.0 and k["end_gap"] > 0.5      # Band der Messung: ab etwa 40 % ohne strenge Verbesserung


def test_preset_kurze_liste_nimmt_weniger_verschlechterungen_an_als_l_50():
    kurz = _e0("Kurze Liste (L = 10)")["kennzahlen"]
    lang = _e0("Late Acceptance: die Auswahl schadet")["kennzahlen"]
    assert kurz["acc_pct"] < lang["acc_pct"] and kurz["end_gap"] < lang["end_gap"] + 1e-9


def test_preset_alle_zuege_annehmen_letzte_tour_weit_ueber_der_besten():
    r = _e0("Alle Züge annehmen (Gegenprobe)")
    k = r["kennzahlen"]
    assert k["acc_pct"] == pytest.approx(100.0) and k["end_gap"] >= 100.0 and k["gain"] < 5.0


def test_preset_late_acceptance_cf_live_klassen_als_menge():
    r = X.e1_messen("cf", 30)
    erlaubt = {"nachteil", "unentschieden"}
    la = next(z for z in r["zeilen"] if z["akz_key"] == "la")
    assert la["ausgang"] in erlaubt and r["kosten"] == 540_000 and r["n_inst"] == 15
    assert all(z["ausgang"] in {"vorteil", "nachteil", "unentschieden"} for z in r["zeilen"])


def test_preset_feste_2opt_wahl_live_klassen_als_menge():
    r = X.e1_messen("s2", 30)
    la = next(z for z in r["zeilen"] if z["akz_key"] == "la")
    assert la["ausgang"] in {"vorteil", "unentschieden"} and la["v"] > 0.0                    # live Vorzeichen wie in der eingefrorenen Messung


def test_preset_grosses_budget_zugart_anteil_unter_late_acceptance():
    p = C.PRESETS["Großes Budget"]
    r = X.e5_messen(p["regel"], p["n"], p["budget"])["akz"]
    assert r["la"]["b5"][0] >= 40.0 and r["ob"]["b5"][0] <= 35.0 and r["la"]["b5"][0] - r["ob"]["b5"][0] >= C.ZUGART_DIFF       # Band; Plan: la >= 45, ob <= 30
    art, text = E.verdict_zugart("Choice Function", r["ob"]["b5"][0], r["la"]["b5"][0], r["ob"]["b5"][1], r["la"]["b5"][1])
    assert art == "warning"


def test_eingefrorene_gegenstuecke_der_presets():
    """Die eingefrorene Messung zeigt, was die kleine Live-Stichprobe nur andeutet (180 Instanzen)."""
    assert F.vergleich(50, "la", "cf")["ausgang"] == "nachteil" and F.vergleich(50, "la", "s2")["ausgang"] == "vorteil"
