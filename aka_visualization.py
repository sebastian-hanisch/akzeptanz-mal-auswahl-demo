"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange) und haben feste Bereiche (keine automatische Skalierung: sie hat in Stück 1 bis 3 der Linie
Konsolenmeldungen mit „-Infinity“ ausgelöst), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import math

import plotly.graph_objects as go

import aka_constants as C

KLASSE_FARBE = {"vorteil": C.COLOR_GUT, "nachteil": C.COLOR_SCHLECHT, "unentschieden": "#9aa0a6"}
KLASSE_NAME = {"vorteil": "Vorteil", "nachteil": "Nachteil", "unentschieden": "unentschieden"}


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _bereich(werte, rand=0.08, mindest=1.0):
    """Fester Achsenbereich (unten, oben) aus endlichen Werten; nie leer, nie unendlich."""
    w = [x for x in werte if x is not None and math.isfinite(x)]
    if not w:
        return (0.0, 1.0)
    lo, hi = min(w), max(w)
    spanne = max(hi - lo, mindest)
    return (lo - rand * spanne, hi + rand * spanne)


# ---------------------------------------------------------------- Experiment 0
def _tour_xy(punkte, tour):
    xs = [punkte[c][0] for c in tour] + [punkte[tour[0]][0]]
    ys = [punkte[c][1] for c in tour] + [punkte[tour[0]][1]]
    return xs, ys


def build_karte(punkte, start, tour, height=420):
    """Karte: Starttour blass, Tour nach der gewählten Anwendung farbig."""
    fig = go.Figure()
    xs, ys = _tour_xy(punkte, start)
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color="#c8c8c8", width=1.2, dash="dot"), name="Starttour", hoverinfo="skip"))
    xs, ys = _tour_xy(punkte, tour)
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_REGEL, width=2.5), name="Tour nach der Anwendung", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[p[0] for p in punkte], y=[p[1] for p in punkte], mode="markers", marker=dict(size=7, color="#333333"), name="Orte",
                             hovertemplate="Ort %{pointNumber}<extra></extra>"))
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.08), plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(visible=False, range=[-60, 1060])
    fig.update_yaxes(visible=False, range=[-60, 1060])
    return lock_axes(fig)


def build_verlauf(spur, start: float, budget: int, marke: int | None = None, height=340):
    """Aktuelle Länge (Treppe) und Bestwert über die Auswertungen; angenommene Verlängerungen als Punkte; senkrechte Marke bei `marke` Auswertungen."""
    xs, aktuell, best = [0], [start], [start]
    worse_x, worse_y = [], []
    for used, _h, _mv, delta, cost, b, _k in spur:
        xs.append(used)
        aktuell.append(cost)
        best.append(b)
        if delta > C.EPS:
            worse_x.append(used)
            worse_y.append(cost)
    xs.append(budget)
    aktuell.append(aktuell[-1])
    best.append(best[-1])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=aktuell, mode="lines", line=dict(color=C.COLOR_REGEL, width=1.6, shape="hv"), name="aktuelle Tour"))
    fig.add_trace(go.Scatter(x=xs, y=best, mode="lines", line=dict(color=C.COLOR_BEST, width=2, shape="hv", dash="dash"), name="beste Tour"))
    if worse_x:
        fig.add_trace(go.Scatter(x=worse_x, y=worse_y, mode="markers", marker=dict(size=5, color=C.COLOR_SCHLECHT), name="angenommene Verlängerung"))
    lo, hi = _bereich(aktuell + best + [start], mindest=1.0)
    fig.update_xaxes(range=[0, budget], title_text="Auswertungen")
    fig.update_yaxes(range=[lo, hi], title_text="Länge der Tour")
    if marke is not None:
        fig.add_trace(go.Scatter(x=[marke, marke], y=[lo, hi], mode="lines", line=dict(color="#888888", width=1, dash="dot"), name="gezeigte Anwendung", hoverinfo="skip"))
    return _base(fig, height)


def build_zugart_balken(anteil_apps, anteil_evals, height=300):
    """Anteile der Zugarten an Anwendungen und Auswertungen (Prozent); Gleichverteilung der Anwendungen als Linie."""
    namen = [C.HNAMEN[h] for h in range(C.K)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=namen, y=[100 * a for a in anteil_apps], name="Anwendungen", marker_color=C.COLOR_REGEL))
    fig.add_trace(go.Bar(x=namen, y=[100 * e for e in anteil_evals], name="Auswertungen", marker_color="#b0b0b0"))
    fig.add_trace(go.Scatter(x=namen, y=[100.0 / C.K] * C.K, mode="lines", line=dict(color=C.COLOR_SCHLECHT, dash="dot"), name="Gleichverteilung der Anwendungen"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(range=[0, 100], title_text="Prozent")
    return _base(fig, height)


# ---------------------------------------------------------------- Experiment 1: Zufall minus Zeile je Akzeptanz
def build_gegen_zufall(zeilen, marken=None, height=340):
    """Balken „Zufall minus Zeile“ (positiv = Zeile besser) je Akzeptanzregel mit Intervall; Marke = Wert der eingefrorenen Messung (180 Instanzen)."""
    namen = [z["akz"] for z in zeilen]
    v = [z["v"] for z in zeilen]
    fehler_oben = [(z["hi"] - z["v"]) if z["hi"] is not None else 0.0 for z in zeilen]
    fehler_unten = [(z["v"] - z["lo"]) if z["lo"] is not None else 0.0 for z in zeilen]
    farben = [KLASSE_FARBE[z["ausgang"]] for z in zeilen]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=namen, y=v, marker_color=farben, name="Live, kleine Stichprobe", error_y=dict(type="data", symmetric=False, array=fehler_oben, arrayminus=fehler_unten)))
    alle = v + [z["lo"] for z in zeilen if z["lo"] is not None] + [z["hi"] for z in zeilen if z["hi"] is not None]
    if marken:
        fig.add_trace(go.Scatter(x=namen, y=marken, mode="markers", marker=dict(symbol="diamond", size=11, color="#222222"), name="eingefroren (180 Instanzen)"))
        alle += list(marken)
    lo, hi = _bereich(alle + [0.0], mindest=2.0)
    fig.update_yaxes(range=[lo, hi], title_text="Zufall minus Zeile (Prozentpunkte)", zeroline=True)
    fig.update_xaxes(tickangle=-20)
    return _base(fig, height)


# ---------------------------------------------------------------- Experiment 2: Heatmap
def build_heatmap(matrix, height=360):
    """Heatmap der mittleren Abstände (Zeilen: Auswahl, Spalten: Akzeptanz), Zahlen als Beschriftung."""
    namen_x = [C.AKZ_KURZ[a] for a in C.AKZ6]
    namen_y = [C.ZEILEN_ANZEIGE[z] for z in C.ZEILEN]
    flach = [x for row in matrix for x in row]
    fig = go.Figure(go.Heatmap(z=matrix, x=namen_x, y=namen_y, colorscale="YlOrRd", zmin=min(flach), zmax=max(flach), showscale=True, colorbar=dict(title="Abstand %")))
    for i, row in enumerate(matrix):
        for j, val in enumerate(row):
            fig.add_annotation(x=namen_x[j], y=namen_y[i], text=f"{val:.2f}".replace(".", ","), showarrow=False, font=dict(size=11, color="#111111"))
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(tickangle=-20)
    return _base(fig, height)


# ---------------------------------------------------------------- Experiment 3: Listenlänge
def _l_tick():
    return dict(tickmode="array", tickvals=[math.log10(L) for L in C.L_WERTE], ticktext=["1 (nur besser)" if L == 1 else str(L) for L in C.L_WERTE])


def build_l_abstand(reihen, height=340):
    """Mittlerer Abstand gegen die Listenlänge L (logarithmisch), eine Linie je Auswahlzeile. reihen: {zeile: [Abstände in der Reihenfolge C.L_WERTE]}."""
    fig = go.Figure()
    alle = []
    for z, ys in reihen.items():
        fig.add_trace(go.Scatter(x=[math.log10(L) for L in C.L_WERTE], y=ys, mode="lines+markers", name=C.ZEILEN_ANZEIGE[z], line=dict(color=C.FARBE_ZEILE[z])))
        alle += list(ys)
    lo, hi = _bereich(alle, mindest=2.0)
    fig.update_xaxes(range=[-0.1, 2.4], title_text="Listenlänge L von Late Acceptance", **_l_tick())
    fig.update_yaxes(range=[lo, hi], title_text="mittlerer Abstand (%)")
    return _base(fig, height)


def build_l_diff(zeilen_daten, height=340):
    """Zufall minus Zeile gegen L mit Intervall; Punkte nach Klasse gefärbt. zeilen_daten: {zeile: [dict(v, lo, hi, ausgang) je L]}."""
    fig = go.Figure()
    alle = [0.0]
    for z, rows in zeilen_daten.items():
        xs = [math.log10(L) for L in C.L_WERTE]
        fig.add_trace(go.Scatter(
            x=xs, y=[r["v"] for r in rows], mode="lines+markers", name=C.ZEILEN_ANZEIGE[z], line=dict(color=C.FARBE_ZEILE[z], width=1.5),
            marker=dict(size=9, color=[KLASSE_FARBE[r["ausgang"]] for r in rows], line=dict(width=1.5, color=C.FARBE_ZEILE[z])),
            error_y=dict(type="data", symmetric=False, array=[r["hi"] - r["v"] for r in rows], arrayminus=[r["v"] - r["lo"] for r in rows], thickness=1)))
        alle += [r["lo"] for r in rows] + [r["hi"] for r in rows]
    lo, hi = _bereich(alle, mindest=2.0)
    fig.update_xaxes(range=[-0.1, 2.4], title_text="Listenlänge L von Late Acceptance", **_l_tick())
    fig.update_yaxes(range=[lo, hi], title_text="Zufall minus Zeile (Prozentpunkte)", zeroline=True)
    return _base(fig, height)


# ---------------------------------------------------------------- Experiment 4: Budget
def _budget_ticks(stufen):
    return dict(tickmode="array", tickvals=list(range(len(stufen))), ticktext=[f"{s}·n" for s in stufen])


def build_budget_abstand(reihen, stufen, height=340):
    fig = go.Figure()
    alle = []
    for z, ys in reihen.items():
        fig.add_trace(go.Scatter(x=list(range(len(stufen))), y=ys, mode="lines+markers", name=C.ZEILEN_ANZEIGE[z], line=dict(color=C.FARBE_ZEILE[z])))
        alle += list(ys)
    lo, hi = _bereich(alle, mindest=1.0)
    fig.update_xaxes(range=[-0.2, len(stufen) - 0.8], title_text="Budget (Auswertungen je Stadt)", **_budget_ticks(stufen))
    fig.update_yaxes(range=[lo, hi], title_text="mittlerer Abstand (%)")
    return _base(fig, height)


def build_budget_diff(zeilen_daten, stufen, height=340):
    fig = go.Figure()
    alle = [0.0]
    for z, rows in zeilen_daten.items():
        fig.add_trace(go.Scatter(
            x=list(range(len(stufen))), y=[r["v"] for r in rows], mode="lines+markers", name=C.ZEILEN_ANZEIGE[z], line=dict(color=C.FARBE_ZEILE[z], width=1.5),
            marker=dict(size=9, color=[KLASSE_FARBE[r["ausgang_k"]] for r in rows], line=dict(width=1.5, color=C.FARBE_ZEILE[z])),
            error_y=dict(type="data", symmetric=False, array=[r["hi_k"] - r["v"] for r in rows], arrayminus=[r["v"] - r["lo_k"] for r in rows], thickness=1)))
        alle += [r["lo_k"] for r in rows] + [r["hi_k"] for r in rows]
    lo, hi = _bereich(alle, mindest=2.0)
    fig.update_xaxes(range=[-0.2, len(stufen) - 0.8], title_text="Budget (Auswertungen je Stadt)", **_budget_ticks(stufen))
    fig.update_yaxes(range=[lo, hi], title_text="Zufall minus Zeile (Prozentpunkte)", zeroline=True)
    return _base(fig, height)


# ---------------------------------------------------------------- Experiment 5: Zugart-Anteile je Akzeptanz
def build_anteile_je_akzeptanz(live, eingefroren, height=340):
    """Anteil von 2opt_b5 an Anwendungen und Auswertungen unter ob, rr, la: live (kleine Stichprobe) und eingefroren."""
    namen = [C.AKZ_KURZ[a] for a in C.E5_AKZ]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=namen, y=[live[a][0] for a in C.E5_AKZ], name="live: Anwendungen", marker_color=C.COLOR_REGEL))
    fig.add_trace(go.Bar(x=namen, y=[live[a][1] for a in C.E5_AKZ], name="live: Auswertungen", marker_color="#8fbab5"))
    if eingefroren:
        fig.add_trace(go.Scatter(x=namen, y=[eingefroren[a][0] for a in C.E5_AKZ], mode="markers", marker=dict(symbol="diamond", size=11, color="#222222"),
                                 name="eingefroren: Anwendungen"))
    fig.add_trace(go.Scatter(x=namen, y=[C.GLEICHVERTEILUNG_B5_APPS] * len(namen), mode="lines", line=dict(color=C.COLOR_SCHLECHT, dash="dot"),
                             name="Gleichverteilung (Anwendungen)"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(range=[0, 100], title_text="Anteil von 2opt_b5 (%)")
    return _base(fig, height)
