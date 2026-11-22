"""Akzeptanz mal Auswahl: wer entscheidet in einer Hyperheuristik? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Vierte Demo der Linie „Hyperheuristiken erklärt“: sechs Auswahlzeilen und sechs Akzeptanzregeln auf der Rundtour, Zerlegung der Streuung,
Listenlänge von Late Acceptance, Budgetreihe, Zugart-Anteile. Aufbau nach DEMO-PLAYBOOK.md (§2): fester Kopf, Presets in der Seitenleiste,
Kernfragen mit Rechnung und Verdikt, Annahmen, Formeln.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import aka_algorithm as A
import aka_constants as C
import aka_evaluation as E
import aka_experiments as X
import aka_frozen as F
import aka_presets as P
import aka_saetze as SZ
import aka_texts as T
import aka_visualization as V
import modul_frisch
from aka_layout import dunkles_design, kopf_css

modul_frisch.aktualisieren(__file__)

st.set_page_config(page_title=T.SEITENTITEL, layout="wide")
de = E.de


@st.cache_data(show_spinner=False)
def _ablauf(familie, n, idx, lauf, regel, akz, faktor, laenge):
    """Experiment 0: ein Lauf mit Spur (alle Eingaben stehen im Schlüssel)."""
    r = X.ablauf(familie, n, idx, lauf, regel, akz, faktor, laenge)
    pkte, _ = A.instance(familie, n, idx)
    return dict(r, punkte=pkte)


@st.cache_data(show_spinner=False)
def _tabelle(name, *args):
    return getattr(SZ, name)(*args)


def zeige(verdikt):
    art, text = verdikt
    getattr(st, art)(text)


# ---------------------------------------------------------------- Kopf und Einleitung
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title(T.TITEL)
st.markdown(T.INTRO)

P.load_permalink_settings()
P.init_session_state_defaults()

with st.expander("💬 In einfachen Worten"):
    st.markdown(T.EINFACH)

with st.expander("So funktioniert eine Hyperheuristik mit getrennter Akzeptanz", expanded=True):
    st.markdown(T.ABLAUF)
    st.markdown("**Die sechs Auswahlzeilen**")
    st.markdown(T.REGEL_TABELLE)
    st.markdown("**Die Akzeptanzregeln**")
    st.markdown(T.AKZEPTANZ_TABELLE)
    st.markdown("**Die acht Zugarten**")
    st.markdown(T.ZUGART_TABELLE)

# ---------------------------------------------------------------- Seitenleiste
with st.sidebar:
    P.sidebar_presets()
    st.header("⚙️ Hyperheuristik")
    regel = st.selectbox("Auswahlregel", P.options("regel_select"), key="regel_select", format_func=C.ZEILEN_ANZEIGE.get,
                         help="Wer die Zugart wählt: Zufall, eine Lernregel oder eine feste Zugart. Benutzt von Kernfrage 0, 1 und 5.")
    akz = st.selectbox("Akzeptanzregel", P.options("akz_select"), key="akz_select", format_func=C.AKZ_KURZ.get,
                       help="Wer entscheidet, ob ein Vorschlag bleibt. Benutzt nur von Kernfrage 0; die Kernfragen 1 bis 4 vergleichen die Regeln selbst.")
    laenge = st.slider("Listenlänge L (nur Late Acceptance)", *P.bounds("laenge_slider"), key="laenge_slider", disabled=akz != "la",
                       help="Länge der Liste von Late Acceptance in Anwendungen; nur bei dieser Akzeptanzregel wirksam, sonst gesperrt. Benutzt nur von Kernfrage 0.")
    st.header("🗺️ Aufgabe")
    familie = st.selectbox("Familie der Städte", P.options("familie_select"), key="familie_select", format_func=C.FAMILIEN_ANZEIGE.get,
                           help="Wie die Städte erzeugt werden: gleichverteilt, in fünf Gruppen oder auf einem gestörten Gitter. Benutzt nur von Kernfrage 0.")
    n = st.selectbox("Städte n", P.options("n_select"), key="n_select", help="Nur die zwei Größen der eingefrorenen Messung. Benutzt von Kernfrage 0, 1 und 5.")
    faktor = st.select_slider("Budget (Auswertungen je Stadt)", P.options("budget_select"), key="budget_select",
                              help="Eine Auswertung ist ein bewerteter Vorschlag; 2opt_b5 kostet bis zu fünf. Benutzt von Kernfrage 0 und 5 (Kernfrage 1 rechnet immer 50·n).")
    idx = st.number_input("Instanz", *P.bounds("instanz_input"), key="instanz_input", step=1,
                          help="Nummer der erzeugten Rundtour. Benutzt nur von Kernfrage 0.")
    lauf = st.number_input("Zufalls-Seed des Laufs", *P.bounds("lauf_input"), key="lauf_input", step=1,
                           help="Bestimmt Starttour und Zufallsstrom. Benutzt nur von Kernfrage 0.")
    st.button("🎲 Neue Instanz", on_click=P.randomize_instance, width="stretch", key="zufall_button")

P.sync_query_params({"familie_select": familie, "n_select": n, "budget_select": faktor, "instanz_input": idx, "lauf_input": lauf, "regel_select": regel,
                     "akz_select": akz, "laenge_slider": laenge})

regel_name = C.ZEILEN_ANZEIGE[regel]
akz_name = C.AKZ_KURZ[akz] if akz != "la" else f"Late Acceptance (L = {int(laenge)})"
meta = F.meta()
n_inst = F.tafel_instanzen()

# ---------------------------------------------------------------- Kernfrage 0: die Suche Schritt für Schritt
st.subheader("🔬 Kernfrage 0: Wie sieht eine Suche aus, und was geschieht mit den angenommenen Verschlechterungen?")
st.caption("Benutzt die Seitenleiste: Auswahlregel, Akzeptanzregel, Listenlänge, Familie, Städte, Budget, Instanz und Zufalls-Seed. Faktenabschnitt: ein Einzellauf, kein Vergleich.")
st.markdown(f"Ein Lauf mit **{regel_name}** und Akzeptanz **{akz_name}**, {faktor * n} Auswertungen auf der Instanz {int(idx)} ({C.FAMILIEN_ANZEIGE[familie]}, n = {n}), Zufalls-Seed {int(lauf)}.")
r0 = _ablauf(familie, n, int(idx), int(lauf), regel, akz, faktor, int(laenge))
kz = r0["kennzahlen"]
prozent = st.slider("Lauf zeigen bis (Prozent der Anwendungen)", 5, 100, 100, step=5, key="schritt_slider")
k_bis = max(1, r0["steps"] * prozent // 100)
bis_spur = [s for s in r0["trace"] if s[6] <= k_bis]
marke = bis_spur[-1][0] if bis_spur else 0
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("beste Tour", de(r0["best"], 1))
c2.metric("Gewinn gegen Start", f"{de(kz['gain'], 1)} %", help="Verbesserung der besten Tour gegenüber der Startlösung.")
c3.metric("angenommen", "keine" if kz["acc_pct"] is None else f"{de(kz['acc_pct'], 1)} %", help="Anteil der Anwendungen, deren Vorschlag blieb.")
c4.metric("letzte über beste", f"{de(kz['end_gap'], 2)} %", help="Länge der letzten Tour über der besten gefundenen Tour.")
c5.metric("Anwendungen", E.tsd(r0["steps"]), help="Zweite Zähleinheit: gleiche Auswertungen, verschieden viele Anwendungen (2opt_b5 kostet bis zu fünf).")
links, rechts = st.columns(2)
links.plotly_chart(V.build_karte(r0["punkte"], r0["t0"], X.tour_nach(r0, k_bis)), key=f"fig_karte_{prozent}", config={"displayModeBar": False})
rechts.plotly_chart(V.build_verlauf(r0["trace"], r0["start"], faktor * n, marke if prozent < 100 else None), key=f"fig_verlauf_{prozent}", config={"displayModeBar": False})
st.caption(f"Gezeigt: Tour nach Anwendung {E.tsd(k_bis)} von {E.tsd(r0['steps'])}. Die Marke im Verlauf steht beim letzten angenommenen Zug bis dahin.")
a_apps, a_evals = A.shares(r0["apps"], r0["evals"])
st.plotly_chart(V.build_zugart_balken(a_apps, a_evals), key="fig_zugart", config={"displayModeBar": False})
zeige(E.verdict_ablauf(r0["best"], kz["gain"], r0["used"], r0["steps"], kz["acc_pct"], kz["nonimp_pct"], kz["end_gap"]))
st.markdown(SZ.satz_wanderung())

# ---------------------------------------------------------------- Kernfrage 1: dieselbe Auswahl, sechs Akzeptanzregeln (live)
st.subheader("🔬 Kernfrage 1: Schlägt dieselbe Auswahlregel Zufall, wenn die Akzeptanzregel wechselt?")
st.caption("Benutzt die Seitenleiste: Auswahlregel und Städte. Das Budget ist fest 50·n. Live mit kleiner Stichprobe; die eingefrorene Messung steht daneben.")
if regel == "rand":
    st.info("Gewählt ist Zufall selbst: er ist der Maßstab. Eine andere Auswahlregel wählen, um sie unter den sechs Akzeptanzregeln mit Zufall zu vergleichen.")
else:
    kosten1 = E.live_cost_e1(n, C.E1_BUDGET, regel)
    assert kosten1 <= C.LIVE_MAX_EVALS
    schluessel1 = (regel, n)
    st.markdown(f"**{regel_name} gegen Zufall** unter jeder Akzeptanzregel, Budget {C.E1_BUDGET}·n ({E.tsd(C.E1_BUDGET * n)} Auswertungen je Lauf), "
                f"gleiche Starttouren und Zufallszahlen je Instanz und Zufalls-Seed (gepaart).")
    if st.button(f"Live rechnen ({E.tsd(kosten1)} Auswertungen)", key="e1_button"):
        with st.spinner(f"Rechne {E.tsd(kosten1)} Auswertungen …"):
            st.session_state["e1_ergebnis"] = (schluessel1, X.e1_messen(regel, n))
    g = st.session_state.get("e1_ergebnis")
    if g and g[0] == schluessel1:
        res = g[1]
        marken = [F.vergleich(C.E1_BUDGET, a, regel)["v"] for a in C.AKZ6]
        zeige(E.verdict_gegen_zufall(regel_name, res["zeilen"], res["n_inst"], res["n_laeufe"]))
        st.plotly_chart(V.build_gegen_zufall(res["zeilen"], marken), key="fig_e1", config={"displayModeBar": False})
        st.dataframe(SZ.tab_e1(res["zeilen"], marken), hide_index=True, width="stretch")
        st.caption(SZ.live_caption(res["n_inst"], res["n_laeufe"]))
    else:
        st.caption("Noch nicht gerechnet für diese Einstellung. " + SZ.satz_live_klein())
    st.markdown(SZ.satz_hook())

# ---------------------------------------------------------------- Kernfrage 2: Kreuztafel
st.subheader("🔬 Kernfrage 2: Wie viel der Streuung erklärt die Akzeptanz, wie viel die Auswahl?")
st.caption("Eingefroren, kein Regler der Seitenleiste. Eigene Regler: Stufe und Intervallniveau.")
e2a, e2b = st.columns(2)
stufe2 = e2a.radio("Stufe", C.STUFEN_TAFEL, key="e2_stufe_radio", horizontal=True, format_func=lambda s: f"{C.STUFEN_NAMEN[s]} ({s}·n)")
niveau2 = e2b.radio("Intervalle", ("korrigiert", "je Vergleich"), key="e2_niveau_radio", horizontal=True,
                    format_func=lambda x: "korrigiert für 30 Vergleiche" if x == "korrigiert" else "95 % je Vergleich")
tf = F.tafel(stufe2)
korr = niveau2 == "korrigiert"
zeil = tf["zaehlung"]["30" if korr else "95"]
zeige(E.verdict_tafel(stufe2, tf["zerlegung"]["alle"], tf["zerlegung"]["ohne_la"], tf["umkehr"]["la"], tf["umkehr"]["la10"], *zeil))
st.plotly_chart(V.build_heatmap(tf["mittel"]), key=f"fig_heat_{stufe2}", config={"displayModeBar": False})
st.markdown("**Streuungsanteile** (Abstand je Instanz zentriert, Zellmittel über die Zufalls-Seeds)")
st.dataframe(_tabelle("tab_streuung", stufe2), hide_index=True, width="stretch")
st.markdown("**Rangfolge der Auswahlzeilen je Akzeptanzregel** (1 = kleinster mittlerer Abstand) und **Rangkorrelation** (Spearman)")
st.dataframe(_tabelle("tab_rang", stufe2), hide_index=True, width="stretch")
st.dataframe(_tabelle("tab_spearman", stufe2), hide_index=True, width="stretch")
st.markdown("**Die 30 gepaarten Vergleiche gegen Zufall** (Unterschied „Zufall minus Zeile“ in Prozentpunkten, positiv = Zeile besser)")
st.dataframe(_tabelle("tab_vergleiche", stufe2, korr), hide_index=True, width="stretch")
st.markdown(SZ.satz_spannweite(stufe2))
st.markdown("**Anwendungen je Lauf** (zweite Zähleinheit; gleiche Auswertungen, verschieden viele Anwendungen)")
st.dataframe(_tabelle("tab_anwendungen", stufe2), hide_index=True, width="stretch")
st.caption(SZ.mess_caption(stufe2) + " Fall-Schwellen des Verdikts (gesetzt, nicht abgeleitet): Akzeptanz mindestens doppelt so groß wie die Auswahl, ohne Late Acceptance unter 25 %, Differenz der beiden Anteile mindestens 25 Punkte.")
st.markdown(SZ.satz_zerlegung())

# ---------------------------------------------------------------- Kernfrage 3: Listenlänge
st.subheader("🔬 Kernfrage 3: Bei welcher Listenlänge kippt die Auswahl?")
st.caption("Eingefroren, kein Regler der Seitenleiste. Eigene Regler: Stufe und Auswahlzeilen.")
e3a, e3b = st.columns(2)
stufe3 = e3a.select_slider("Budget", C.STUFEN_L, value=C.STUFEN_L[0], key="e3_stufe_select", format_func=lambda s: f"{s}·n")
zeilen3 = e3b.multiselect("Auswahlzeilen", C.L_ZEILEN, default=["rand", "cf", "s2"], key="e3_zeilen_multi", format_func=C.ZEILEN_ANZEIGE.get)
j3 = C.STUFEN_L.index(stufe3)
if not zeilen3:
    st.info("Mindestens eine Auswahlzeile wählen.")
else:
    st.plotly_chart(V.build_l_abstand({z: F.l_mittel(z, j3) for z in zeilen3}), key=f"fig_l_abstand_{stufe3}", config={"displayModeBar": False})
    gegen = [z for z in zeilen3 if z != "rand"]
    if gegen:
        st.plotly_chart(V.build_l_diff({z: [F.l_vergleich(z, L, j3) for L in C.L_WERTE] for z in gegen}), key=f"fig_l_diff_{stufe3}", config={"displayModeBar": False})
        for z in gegen:
            zeige(E.verdict_listenlaenge(C.ZEILEN_ANZEIGE[z], stufe3, F.l_ausgaenge(z, j3)))
    else:
        st.caption("Zufall ist der Maßstab der Unterschiede: für den Unterschied zu Zufall eine weitere Zeile wählen.")
    for z in zeilen3:
        st.markdown(f"**{C.ZEILEN_ANZEIGE[z]}, {stufe3}·n**")
        st.dataframe(_tabelle("tab_l", z, j3), hide_index=True, width="stretch")
st.caption(SZ.mess_caption_l(stufe3))
st.markdown(SZ.satz_l())
st.markdown(SZ.satz_link_abkuehlen())

# ---------------------------------------------------------------- Weitere Experimente (Kernfrage 4 und 5)
with st.expander("🔬 Weitere Experimente"):
    st.subheader("Kernfrage 4: Bleibt das bei größerem Budget?")
    st.caption("Eingefroren. Eigener Regler: Akzeptanzregel (nicht der der Seitenleiste).")
    akz4 = st.selectbox("Akzeptanzregel", ("ob", "rr", "la", "sa", "gd"), key="e4_akz_select", format_func=lambda a: C.AKZ_KURZ[a])
    bz = F.budget_zaehlung(akz4)
    zeige(E.verdict_budget(C.AKZ_KURZ[akz4], bz[0], bz[1]))
    stufen4 = F.load()["budget"]["stufen"]
    st.plotly_chart(V.build_budget_abstand({z: F.budget_mittel(akz4, z) for z in C.ZEILEN}, stufen4), key=f"fig_b_abstand_{akz4}", config={"displayModeBar": False})
    st.plotly_chart(V.build_budget_diff({z: [F.budget_vergleich(akz4, z, j) for j in range(len(stufen4))] for z in C.LERN_ZEILEN_FUENF}, stufen4),
                    key=f"fig_b_diff_{akz4}", config={"displayModeBar": False})
    st.dataframe(_tabelle("tab_budget", akz4), hide_index=True, width="stretch")
    st.caption(SZ.mess_caption_budget())

    st.subheader("Kernfrage 5: Was lernt die Auswahl unter welcher Akzeptanz?")
    st.caption("Benutzt die Seitenleiste: Auswahlregel, Städte und Budget. Live mit kleiner Stichprobe.")
    if regel not in C.LERN_REGELN_APP:
        st.info("Dieser Abschnitt braucht eine lernende Auswahlregel (UCB, Choice Function oder Lernautomat); bei Zufall und den festen Zugarten gibt es nichts zu lernen.")
    else:
        kosten5 = E.live_cost_e5(n, faktor, regel)
        assert kosten5 <= C.LIVE_MAX_EVALS
        schluessel5 = (regel, n, faktor)
        st.markdown(f"**{regel_name}** unter „nur besser“, Rekord-zu-Rekord und Late Acceptance (L = 50), Budget {faktor}·n, Standardbelohnung.")
        if st.button(f"Live rechnen ({E.tsd(kosten5)} Auswertungen)", key="e5_button"):
            with st.spinner(f"Rechne {E.tsd(kosten5)} Auswertungen …"):
                st.session_state["e5_ergebnis"] = (schluessel5, X.e5_messen(regel, n, faktor))
        g5 = st.session_state.get("e5_ergebnis")
        if g5 and g5[0] == schluessel5:
            res5 = g5[1]["akz"]
            live = {a: res5[a]["b5"] for a in C.E5_AKZ}
            fest = {a: F.anteil_b5(C.STUFEN_TAFEL[1], a, regel) for a in C.E5_AKZ} if faktor == 200 else None
            b_ob, b_la = res5["ob"]["b5"], res5["la"]["b5"]
            zeige(E.verdict_zugart(regel_name, b_ob[0], b_la[0], b_ob[1], b_la[1]))
            st.plotly_chart(V.build_anteile_je_akzeptanz(live, fest), key="fig_e5", config={"displayModeBar": False})
            st.dataframe(SZ.tab_e5(res5, regel), hide_index=True, width="stretch")
            st.caption(SZ.live_caption(g5[1]["n_inst"], g5[1]["n_laeufe"]))
        else:
            st.caption("Noch nicht gerechnet für diese Einstellung. " + SZ.satz_live_klein())
        st.markdown(SZ.satz_zugart())

# ---------------------------------------------------------------- Annahmen, Formeln, Footer
st.subheader("🚧 Wo die Annahmen enden")
st.markdown(T.ASSUMPTIONS_MARKDOWN)
st.markdown(T.NACHBARN)

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(T.LESEHILFE)
    for titel, formel in T.FORMELN:
        st.markdown(f"**{titel}**")
        st.markdown(f"$$\n{formel}\n$$")
    st.markdown(T.FORMEL_NACHSATZ)

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Hyperheuristiken: Auswählen und Erzeugen](https://sebastianhanisch.net/konzepte-hyperheuristiken.html)."
)
