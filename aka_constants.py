"""Konstanten: Zugarten, Familien, Stufen, Akzeptanzregeln, Auswahlzeilen, Marken der Verdikte, Regler-Grenzen, Farben, Presets.

Der obere Teil (Zugarten, Instanzen, Zwecke der Zufalls-Seeds, Akzeptanz, Marken, Parameter der Auswahlregeln) führt dieselben Namen und Werte
wie die Vorgänger der Linie (hyperheuristik-demo, zugmenge-demo, auswahlregeln-demo): die kopierten Module (aka_scenario, aka_moves, aka_accept,
aka_stats, aka_select, aka_regeln, aka_belohnung) lesen sie hier."""

# ---------------------------------------------------------------- Zugarten (Reihenfolge und Index sind Schnittstelle der Linie)
HNAMEN = ("swap", "insert", "2opt", "2opt_lokal", "oropt2", "oropt3", "dbridge", "2opt_b5")
K = 8
KOSTEN = (1, 1, 1, 1, 1, 1, 1, 5)          # Auswertungen je Anwendung; 2opt_b5 am Budgetrand weniger (aka_moves.cost_of)
H_2OPT, H_2OPT_B5 = 2, 7
ALLE_ZUGARTEN = tuple(range(K))
B5_STICHPROBEN = 5
LOKAL_LMAX = 8                              # 2opt_lokal: Segmentlänge höchstens min(8, n - 2)
HNAMEN_ANZEIGE = {
    "swap": "Tausch", "insert": "Einfügen", "2opt": "2-opt", "2opt_lokal": "2-opt lokal", "oropt2": "Or-opt 2", "oropt3": "Or-opt 3",
    "dbridge": "Doppelbrücke", "2opt_b5": "2-opt, beste von 5",
}

# ---------------------------------------------------------------- Instanzen
FAMILIEN = ("gleich", "cluster", "gitter")  # Index = Schlüssel der Zufalls-Seeds
FAMILIE_HAND = "hand"
FAMILIEN_ANZEIGE = {"gleich": "gleichverteilt", "cluster": "Gruppen", "gitter": "Gitter"}
N_GEMESSEN = (30, 60)                       # nur dort liegt die eingefrorene Messung vor; die App bietet nur diese beiden
SEITE = 1000.0                              # Quadrat 1000 x 1000 (Einheiten, keine Kilometer)
CLUSTER_ZAHL, CLUSTER_SIGMA = 5, 40.0
GITTER_FAKTOR, GITTER_RAUSCHEN = 1.5, 0.1
INSTANZEN_REF = 200                         # Instanzen 0 bis 199 je Familie und n haben einen Referenzwert (aka_refs.json)

# Zwecke der Zufalls-Seeds (aka_scenario.derive): je Zweck ein eigener Strom
ZWECK_INSTANZ, ZWECK_START, ZWECK_LAUF, ZWECK_BOOT = 11, 33, 24, 7
ZWECK_PERM = 41                             # Vertauschungen des Permutationstests

# ---------------------------------------------------------------- Messreihen (eingefroren): Instanzen je Familie und n, Läufe (Zufalls-Seeds)
TAFEL_START, TAFEL_INSTANZEN, TAFEL_LAEUFE = 100, 30, 6        # M-A: Instanzen 100 bis 129 je Familie und n = 180 Instanzen
BUDGET_START, BUDGET_INSTANZEN, BUDGET_LAEUFE = 130, 10, 3     # M-B: Instanzen 130 bis 139 = 60 Instanzen
LREIHE_START, LREIHE_INSTANZEN, LREIHE_LAEUFE = 140, 10, 3     # M-C: Instanzen 140 bis 149 = 60 Instanzen
STUFEN_TAFEL = (50, 200)                    # klein (lo), groß (hi): Auswertungen = Faktor mal n
STUFEN_NAMEN = {50: "klein", 200: "groß"}
STUFEN_BUDGET = (50, 100, 200, 400, 800)
STUFEN_L = (50, 100, 200, 400)
L_WERTE = (1, 2, 5, 10, 20, 30, 50, 75, 100, 200)
PERMUTATIONEN, BOOTSTRAP_OFFLINE = 2000, 40000
BOOTSTRAP_LIVE = 4000
BOOTSTRAP_ZIEHUNGEN = 4000

# ---------------------------------------------------------------- Akzeptanz
EPS = 1e-9
RHO = 0.01                                  # Rekord-zu-Rekord: Kandidat <= (1 + RHO) * Bestwert
LA_LEN, LA_LEN_KURZ = 50, 10                # Late Acceptance: Länge der Historie in Anwendungen
GD_END = 0.80                               # Sintflut: Endpegel (Anteil der Startlänge)
SA_T0, SA_T1 = 0.3, 0.003                   # Annealing: Anfangs- und Endtemperatur in mittleren Kantenlängen der Starttour
AKZ6 = ("ob", "rr", "sa", "gd", "la", "la10")                  # die sechs Spalten der Kreuztafel
AKZ_APP = ("ob", "rr", "sa", "gd", "la", "am")                 # Akzeptanz-Regler der App (am = alle Züge annehmen, Gegenprobe)
BUDGETFREI = ("ob", "rr", "la")             # Ergebnis bis zu einer Auswertungszahl hängt nicht am Gesamtbudget (Stufen aus einem Lauf)
AKZ_ANZEIGE = {"ob": "nur besser", "rr": "Rekord-zu-Rekord", "sa": "Annealing-Akzeptanz", "gd": "Sintflut", "la": "Late Acceptance (L = 50)",
               "la10": "Late Acceptance (L = 10)", "am": "alle Züge annehmen (Gegenprobe)"}
AKZ_KURZ = {"ob": "„nur besser“", "rr": "Rekord-zu-Rekord", "sa": "Annealing", "gd": "Sintflut", "la": "Late Acceptance (L = 50)",
            "la10": "Late Acceptance (L = 10)", "am": "alle Züge annehmen"}
AKZ_LA_EIGENNAME = ("la", "la10")
LIVE_L = 50

# ---------------------------------------------------------------- Auswahlzeilen
ZEILEN = ("rand", "ucb", "cf", "laut", "s2", "s7")             # sechs Zeilen der Kreuztafel
ZEILEN_ARME = {"rand": None, "ucb": None, "cf": None, "laut": None, "s2": (H_2OPT,), "s7": (H_2OPT_B5,)}
ZEILEN_REGEL = {"rand": "rand", "ucb": "ucb", "cf": "cf", "laut": "laut"}
ZEILEN_ANZEIGE = {"rand": "Zufall", "ucb": "UCB", "cf": "Choice Function", "laut": "Lernautomat", "s2": "nur 2-opt", "s7": "nur 2-opt (bester von 5)"}
LERNZEILEN = ("ucb", "cf", "laut")
FESTE_ZEILEN = ("s2", "s7")
LERN_ZEILEN_FUENF = ("ucb", "cf", "laut", "s2", "s7")          # alle außer Zufall: die fünf Vergleiche gegen Zufall je Akzeptanz
L_ZEILEN = ("rand", "ucb", "cf", "s2", "s7")                   # Zeilen der L-Reihe (der Lernautomat entfällt, Rechenlast)
CF_ALPHA, CF_PHI0, CF_PHI_ERFOLG, CF_PHI_SCHRITT, CF_PHI_MIN, CF_ZEITFENSTER, CF_RAUSCHEN = 0.9, 0.5, 0.99, 0.01, 0.01, 50, 1e-9
LAUT_A, LAUT_BODEN = 0.05, 0.01
Q_EPS, Q_ALPHA, Q_GAMMA = 0.1, 0.1, 0.5
UCB_C, UCB_GAMMA = 0.2, 0.995
PARAMETER = {"cf": ("alpha", CF_ALPHA, 0.5, 0.99), "ucb": ("c", UCB_C, 0.05, 1.0), "laut": ("a", LAUT_A, 0.02, 0.15), "q": ("alpha", Q_ALPHA, 0.03, 0.3)}
BELOHNUNGEN = ("r2", "best", "r1", "rank", "ma")
RANK_FENSTER = 30
MA_ALPHA = 0.05
APP_REGELN = ("rand", "ucb", "cf", "laut", "s2", "s7")         # Auswahl-Regler der App = die Zeilen der Tafel
LERN_REGELN_APP = ("ucb", "cf", "laut")

# ---------------------------------------------------------------- Verdikte (gesetzt, nicht abgeleitet)
MARKE_KLAR, MARKE_GLEICH = 0.25, 0.10       # Klassenregel von Stück 1: „klar“ ab |v| >= 0,25 mit Intervall ohne 0, „gleich“ unter 0,10 oder Intervall mit 0
FAKTOR_AKZEPTANZ = 2.0                      # E2: Akzeptanz erklärt mindestens das Doppelte der Auswahl
ANTEIL_OHNE_LA = 25.0                       # E2 Fall A: Akzeptanzanteil ohne Late Acceptance unter 25 Prozent ...
DIFF_ANTEILE = 25.0                         # ... und die beiden Akzeptanzanteile unterscheiden sich um mindestens 25 Prozentpunkte
SPEARMAN_GRENZE, SPEARMAN_MINDEST = -0.5, 2  # Rangumkehr: Rangkorrelation unter -0,5 gegen mindestens 2 von 4 anderen Akzeptanzregeln
ZUGART_DIFF = 20.0                          # E5: Differenz der Anteile auf 2opt_b5 in Prozentpunkten
GLEICHVERTEILUNG_B5_APPS = 100.0 / 8        # Anteil der Anwendungen auf 2opt_b5 bei Gleichverteilung (12,5 %)
FENSTER_RELATIV = 0.05                      # Intervall des Spielraums

# ---------------------------------------------------------------- Live-Rechnung (Zählung der Auswertungen vor dem Start)
LIVE_MAX_EVALS = 600_000
E1_INSTANZEN = {30: 5, 60: 2}               # je Familie, idx 0 bis m - 1
E1_LAEUFE = 2
E5_INSTANZEN = {30: 3, 60: 2}
E5_LAEUFE = 2
E5_AKZ = ("ob", "rr", "la")
E1_BUDGET = 50                              # Faktor mal n, fest

# ---------------------------------------------------------------- Regler
DEFAULT_FAMILIE, DEFAULT_N, DEFAULT_BUDGET, DEFAULT_AKZ, DEFAULT_REGEL = "gleich", 30, 50, "ob", "cf"
BUDGET_LIVE = (50, 100, 200)
INSTANZ_MAX, DEFAULT_INSTANZ = 29, 0
LAUF_MAX, DEFAULT_LAUF = 99, 0
L_MIN, L_MAX = 1, 200

# ---------------------------------------------------------------- Farben
FARBE_ZUGART = ("#9d755d", "#f58518", "#4c78a8", "#72b7b2", "#b279a2", "#ff9da6", "#bab0ac", "#e45756")
COLOR_REGEL = "#2F6B65"
COLOR_ZUFALL = "#888888"
COLOR_BEST = "#4c78a8"
COLOR_SCHLECHT = "#e45756"
COLOR_GUT = "#54a24b"
FARBE_ZEILE = {"rand": "#888888", "ucb": "#b279a2", "cf": "#2F6B65", "laut": "#f58518", "s2": "#4c78a8", "s7": "#e45756"}

# ---------------------------------------------------------------- Presets (jedes legt alle Regler fest)
_BASIS = {"familie": "gleich", "n": 30, "budget": 50, "instanz": 0, "lauf": 0, "regel": "cf", "akz": "ob", "laenge": LA_LEN}


def _preset(**kw):
    p = dict(_BASIS)
    p.update(kw)
    return p


PRESETS = {
    "Standardfall: Choice Function, nur besser": _preset(),
    "Late Acceptance: die Auswahl schadet": _preset(akz="la"),
    "Late Acceptance: feste 2-opt-Wahl": _preset(akz="la", regel="s2"),
    "Kurze Liste (L = 10)": _preset(akz="la", laenge=LA_LEN_KURZ),
    "Großes Budget": _preset(akz="la", budget=200),
    "Alle Züge annehmen (Gegenprobe)": _preset(akz="am", regel="rand"),
}
PRESET_HELP: dict[str, str] = {}             # wird in aka_texts gefüllt

# ---------------------------------------------------------------- Namen der kopierten Auswahlregeln (aka_regeln, aka_select) und Kürzel der Kopien
REGELN = ("rand", "rg", "cf", "ucb", "laut", "q")
LERNREGELN = ("cf", "ucb", "laut", "q")
DREI_REGELN = ("cf", "laut", "q")
REGEL_ANZEIGE = {"rand": "Zufall", "rg": "Zufallsgradient", "cf": "Choice Function", "ucb": "UCB", "laut": "Lernautomat", "q": "Q-Lernen",
                 "cfv": "Choice Function, verdünnt"}
AKZEPTANZEN = ("ob", "rr", "la")
STUFEN = STUFEN_TAFEL
