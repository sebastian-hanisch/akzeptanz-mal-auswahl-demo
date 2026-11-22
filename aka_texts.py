"""Texte der App: Einleitung, Erklärtabellen, Annahmen, Formelblock. Sätze mit Messzahlen stehen in aka_saetze (aus der eingefrorenen Messung gerechnet).

ASSUMPTIONS_MARKDOWN steht wortgleich in der README (tests/test_claims.py vergleicht)."""

import aka_constants as C

TITEL = "🎚️ Akzeptanz mal Auswahl: wer entscheidet in einer Hyperheuristik?"
SEITENTITEL = "Akzeptanz mal Auswahl – Sebastian Hanisch"

INTRO = """
Eine **Hyperheuristik** besteht hier aus zwei getrennten Bausteinen: Die **Auswahlregel** entscheidet in jedem Schritt, welche einfache Änderung
(**Zugart**) der Rundtour ausprobiert wird, die **Akzeptanzregel** entscheidet, ob die Änderung bleibt, auch wenn sie die Tour verlängert. Die Demo
kreuzt beide auf erzeugten Rundtouren mit derselben Zahl **bewerteter Kandidaten (Auswertungen)** und fragt nicht, welcher Baustein im Allgemeinen
zählt, sondern **wann eine ungünstige Akzeptanzregel den Gewinn einer Lernregel gegenüber Zufall zerstört**. Das ist die vierte Demo der Reihe „Hyperheuristiken
erklärt“; unten stehen die Kernfragen 0 bis 3, der Expander **🔬 Weitere Experimente**, die Grenzen der Annahmen (🚧) und die Formeln (📐).
"""

EINFACH = """
Stell dir vor, die Tour eines Lieferwagens wird Schritt für Schritt umgebaut: zwei Orte tauschen, ein Stück der Strecke umdrehen, einen Ort
umsetzen. Zwei Fragen entscheiden, wie gut das gelingt. Erstens: Welche Art von Umbau probiert man als Nächstes? Das ist die Auswahl, man kann sie
würfeln, aus Erfahrung lernen oder fest vorgeben. Zweitens: Behält man einen Umbau, der die Tour verlängert, in der Hoffnung, später etwas
Besseres zu finden? Das ist die Akzeptanz. Die Demo probiert viele Kombinationen und zeigt: Eine Auswahl, die in einem Fall hilft, kann in einem
anderen schaden; woran das liegt, ist hier nicht geklärt (Verdacht: die Akzeptanz bestimmt mit, was die Auswahl als Erfolg lernt).
"""

ABLAUF = """
1. **Auswahl:** die **Auswahlregel** bestimmt die Zugart der nächsten Anwendung: Zufall, UCB, Choice Function, Lernautomat oder eine feste Zugart.
2. **Vorschlag:** die Zugart schlägt eine Änderung der Tour vor; ihre Längenänderung Δ folgt in O(1) aus den entfernten und neuen Kanten. Das ist eine
   **Auswertung** (`2opt_b5` bewertet bis zu fünf Vorschläge und nimmt den besten).
3. **Akzeptanz:** die **Akzeptanzregel** entscheidet, ob der Vorschlag bleibt. Jede Regel nimmt strenge Verkürzungen immer an und unterscheidet sich
   nur darin, wann sie auch Verlängerungen annimmt.
4. **Rückmeldung:** die Auswahlregel bekommt als Belohnung die Verkürzung der aktuellen Tour je Auswertung (Standardform wie in der Demo
   „Wer belohnt wen?“; andere Formen sind dort Thema). Das Budget endet nach einer festen Zahl von Auswertungen.

Einordnung: „heuristic selection“ und „move acceptance“ gelten in der Literatur als zwei getrennte Komponenten einer Hyperheuristik (Burke u. a.
2013, Stufe V; Bilgin u. a. 2007 und Özcan u. a. 2008, Stufe V); die Linie „Hyperheuristiken erklärt“ besetzt davon zwei von vier Feldern.
Namen: **Zugart** = Nachbarschaftsoperation der Rundtour, **Zugmenge** = die Menge der Zugarten, **Auswertung** = ein bewerteter Kandidat,
**Zufalls-Seed** = Startwert des Zufallsstroms. Late Acceptance und Rekord-zu-Rekord stehen hier in **eigenen, kleineren Fassungen** (Bausteine im
Hyperheuristik-Rahmen), nicht als Code der Demo zu simuliertem Abkühlen.
"""

REGEL_TABELLE = """
| Auswahlregel | Was sie tut (eigene, vereinfachte Umsetzung) | feste Einstellung |
|---|---|---|
| Zufall | wählt jede Zugart gleich oft, beachtet keinen Erfolg | keine |
| UCB | Mittelwert der Belohnung plus ein Bonus für selten gewählte Zugarten; ältere Anwendungen zählen weniger | c = 0,2, γ = 0,995 |
| Choice Function | wertet je Zugart die jüngsten Belohnungen (allein und nach dem Vorgänger) und die Wartezeit; nimmt die höchste Wertung (hat Gedächtnis) | Vergessen α = 0,9 |
| Lernautomat | hält je Zugart eine Wahrscheinlichkeit und erhöht sie nach jedem Erfolg (Linear Reward-Inaction) | Schrittweite a = 0,05, Boden 0,01 |
| nur 2-opt | feste Zugart ohne Zufall und Lernen | keine |
| nur 2-opt (bester von 5) | feste Zugart `2opt_b5` | keine |
"""

AKZEPTANZ_TABELLE = """
| Akzeptanzregel | Ein Vorschlag bleibt, wenn er … | Einstellung |
|---|---|---|
| nur besser | die Tour streng verkürzt | keine |
| Rekord-zu-Rekord | nicht verlängert oder die neue Länge höchstens 1 % über dem Bestwert liegt | ρ = 0,01 |
| Annealing-Akzeptanz | nicht verlängert, sonst mit Wahrscheinlichkeit e^(−Δ/T); T fällt geometrisch mit den verbrauchten Auswertungen | T von 0,3 auf 0,003 mittlere Kantenlängen |
| Sintflut | nicht verlängert oder unter einem Pegel bleibt, der linear mit den verbrauchten Auswertungen fällt | Pegel von 100 % auf 80 % der Startlänge |
| Late Acceptance | nicht verlängert oder die neue Länge höchstens so groß ist wie die Länge vor L Anwendungen | L = 50 (Regler: 1 bis 200), L = 10 in der Tafel |
| alle Züge annehmen | immer (Gegenprobe, als Suche wertlos) | keine |
"""

ZUGART_TABELLE = """
| Zugart | Was sie ändert | Auswertungen |
|---|---|---|
| `swap` | zwei Städte tauschen die Plätze | 1 |
| `insert` | eine Stadt wird an eine andere Stelle gesetzt | 1 |
| `2opt` | ein Stück der Tour wird umgedreht | 1 |
| `2opt_lokal` | ein kurzes Stück (höchstens 8 Städte) wird umgedreht | 1 |
| `oropt2`, `oropt3` | zwei bzw. drei aufeinanderfolgende Städte wandern gemeinsam | 1 |
| `dbridge` | die Tour wird an drei Stellen geschnitten und über Kreuz verbunden (Doppelbrücke) | 1 |
| `2opt_b5` | fünf 2-opt-Vorschläge, der beste wird angewandt | bis 5 |
"""

ASSUMPTIONS_MARKDOWN = """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| Erzeugte Rundtour, n = 30 und 60, 50 bis 800 Auswertungen je Stadt | Größere n und Budgets sind nicht gemessen. In der Demo zu simuliertem Abkühlen (200 000 Vorschläge, 60 Stopps) kippt Late Acceptance erst bei viel längeren Listen: anderes Regime, kein Widerspruch, Zahlen nicht vergleichbar | Verweis `simulated-annealing-demo` |
| Die Parameter der Akzeptanzregeln sind gesetzt, nicht abgestimmt (ρ = 1 %, Temperaturen, Endpegel, L) | Die Listenlänge allein verschiebt das Ergebnis stark (Experiment 3); die Rangfolge der Akzeptanzregeln gilt nur für diese Einstellungen | Einstellungen wählen: nicht Teil dieser Demo |
| Eigene Umsetzungen der Auswahlregeln mit festen Parametern; die Choice Function misst hier Auswertungen, nicht Zeit | Die Originale (Cowling u. a.) wurden nicht gelesen; die Zahlen gelten für diese Fassungen | Demo „Wer belohnt wen?“ |
| Referenz = bester bekannter Wert | Kein Optimum für n = 30 bis 60: Abstände sind Untergrenzen der wahren Lücken; gepaarte Unterschiede sind davon nur über den Nenner betroffen (der Unterschied wird durch die Referenz geteilt) | keiner |
| Gleiche Auswertungszahl = gleicher Aufwand | Nicht in der Rechenzeit (Branke u. a. 2016, Stufe V): die Demo zeigt Anwendungen je Lauf als zweite Zähleinheit und nie Sekunden als Befund | Stück 9 der Reihe |
| Die Live-Stichproben sind klein | Kleine Unterschiede (unter etwa zwei Prozentpunkten; Halbbreite des Intervalls bei der Choice Function 1,0 bis 2,5) streuen von Stichprobe zu Stichprobe; große bleiben. Die Aussage steht in der eingefrorenen Messung | Experiment 2 |
| Die Deutung „Late Acceptance entfernt sich vom Rekord“ oder „Kreditzuweisung“ ist nicht isoliert | Annahmequote und Entfernung vom Rekord werden gezeigt, die Ursache nicht behauptet; Rekord-zu-Rekord nimmt fast so viele Verschlechterungen an wie Late Acceptance und schadet dem Gewinn der Auswahl bei 50·n in dieser Messung nicht | Demo „Wer belohnt wen?“, zustandsabhängige Auswahl |
| Acht Zugarten, eine Familie (2-opt) dominiert | Ohne `2opt_b5` ändert sich der Gewinn der Lernregeln unter Late Acceptance (Demo „Die Zugmenge entscheidet“); die Wechselwirkung hängt auch an der Menge | Demo „Die Zugmenge entscheidet“ |
| Klassenregel und Marken (0,25 und 0,10 Prozentpunkte) | Die Klassenregel dieser Demo folgt der ersten Demo der Reihe; die Demo zur Zugmenge zählt mit ±0,25, die zu den Auswahlregeln mit +0,25 und −0,10: Zählungen der Demos sind nicht dieselbe Einheit | Demos 1 bis 3 der Reihe |
| Rundtour als einziges Fahrzeug | Einplanung und Packen sind nicht gemessen | Stücke 5 bis 8 der Reihe |
| **Nutzen im Betrieb** | **Keine Aussage über Nutzen in Logistik, Lager oder Fertigung** (nicht belegt) | keiner |
"""

NACHBARN = """
**Nachbarn.** Die einzelnen Akzeptanzregeln erklärt und kalibriert die [Demo zum simulierten Abkühlen](https://sebastianhanisch-simulated-annealing-demo.streamlit.app/)
(Abkühlpläne, Größenabhängigkeit, Late Acceptance mit langen Listen); hier stehen sie nur als Bausteine im Hyperheuristik-Rahmen mit anderer Zähleinheit
(Auswertungen je Anwendung statt Vorschläge), anderer Normierung und anderem Budget: **Zahlen beider Demos sind nicht vergleichbar**. Die Mechanik der
Lernregeln steht in der [Bandit-Demo](https://sebastianhanisch-bandit-demo.streamlit.app/), die Zugarten in den Demos zu Nachbarschaften. Die vorherigen Demos der Reihe: „Heuristiken auswählen statt
Lösungen“, „Die Zugmenge entscheidet“ und „Wer belohnt wen?“.
"""

LESEHILFE = """
**Lesehilfe.** Gegeben sind $n$ Orte, acht Zugarten und eine Folge von Auswahl- und Akzeptanzentscheidungen; gesucht ist, mit höchstens $B$
Auswertungen eine möglichst kurze Rundtour zu finden. Verglichen werden Paare aus Auswahl- und Akzeptanzregel. Der Block ist ein vollständiges Modell
der Suche, der Akzeptanzregeln und der Zerlegung; die Auswahlregeln stehen ausdrücklich nur als **Skizze** (ihr vollständiges Modell gehört zur Demo
„Wer belohnt wen?“).

| Symbol | Bedeutung |
|---|---|
| $n$, $d_{ij}$ | Zahl der Orte, Abstand $\\lVert p_i-p_j\\rVert_2$ (Quadrat 1000 × 1000, keine Kilometer) |
| $\\pi$, $c(\\pi)$ | Tour (Permutation), Länge $c(\\pi)=\\sum_k d(\\pi_k,\\pi_{k+1 \\bmod n})$ |
| $h\\in\\{1,\\dots,8\\}$, $\\kappa_h$ | Zugart, Auswertungen einer Anwendung ($\\kappa=1$ außer $\\kappa_8\\le 5$) |
| $t$, $\\pi_t$, $c_t$ | Nummer der Anwendung, Tour und Länge vor Anwendung $t$; $c_0$ = Länge der Startlösung (Nächster Nachbar) |
| $\\Delta_t$ | Längenänderung des Vorschlags der Anwendung $t$ |
| $u_t$, $B$ | verbrauchte Auswertungen, Budget ($B=f\\cdot n$, $f\\in\\{50,100,200,400,800\\}$) |
| $c^{*}_t$ | Bestwert vor Anwendung $t$, $c^{*}_0=c_0$ |
| $\\varepsilon$, $\\rho$, $\\gamma$, $L$, $\\bar\\ell$ | Toleranz $10^{-9}$, Rekord-Spielraum 0,01, Endpegel der Sintflut 0,8, Listenlänge, mittlere Kantenlänge $c_0/n$ der Startlösung |
| $T_0$, $T_1$, $U_t$ | Anfangs- und Endtemperatur $0{,}3\\bar\\ell$ und $0{,}003\\bar\\ell$, gleichverteilte Zufallszahl (nur gezogen, wenn $\\Delta_t>\\varepsilon$) |
| $g$, $\\bar g_{isr}$ | Abstand $100(c^{*}_B-c_{\\mathrm{ref}})/c_{\\mathrm{ref}}$; Mittel über die Zufalls-Seeds für Instanz $i$, Auswahlzeile $s$, Akzeptanzspalte $r$ |
| $s\\in\\{1,\\dots,S\\}$, $r\\in\\{1,\\dots,R\\}$ | Auswahlzeile ($S=6$), Akzeptanzspalte ($R=6$) |
"""

FORMELN = (
    ("Suche: Anwendung $t$ wählt $h_t$, schlägt $\\pi'_t$ mit Änderung $\\Delta_t$ vor, die Akzeptanz $a_t\\in\\{0,1\\}$ entscheidet",
     r"\pi_{t+1}=\begin{cases}\pi'_t & a_t=1\\ \pi_t & a_t=0\end{cases},\qquad \sum_t\kappa_{h_t}\le B,\qquad c^{*}_B=\min_t c(\pi_t)"),
    ("Akzeptanz „nur besser“ und Rekord-zu-Rekord", r"a_t^{\mathrm{ob}}=[\Delta_t<-\varepsilon],\qquad a_t^{\mathrm{rr}}=[\Delta_t\le\varepsilon]\ \vee\ [c_t+\Delta_t\le(1+\rho)\,c^{*}_t]"),
    ("Akzeptanz Late Acceptance (Liste $H$ der Länge $L$, anfangs $c_0$, nach jeder Anwendung $H_{t \\bmod L}\\leftarrow c_{t+1}$)",
     r"a_t^{\mathrm{la}}=[\Delta_t\le\varepsilon]\ \vee\ [c_t+\Delta_t\le H_{t \bmod L}]"),
    ("Akzeptanz Sintflut", r"a_t^{\mathrm{gd}}=[\Delta_t\le\varepsilon]\ \vee\ \Bigl[c_t+\Delta_t\le c_0\bigl(1-(1-\gamma)\,u_t/B\bigr)\Bigr]"),
    ("Akzeptanz Annealing-Akzeptanz", r"a_t^{\mathrm{sa}}=[\Delta_t\le\varepsilon]\ \vee\ \Bigl[U_t<e^{-\Delta_t/T(u_t)}\Bigr],\qquad T(u)=T_0\,(T_1/T_0)^{u/B}"),
    ("Gegenprobe", r"a_t^{\mathrm{am}}=1"),
    ("Invariante von Late Acceptance (aktuelle Länge höchstens Startlänge plus $t$ mal Toleranz $\\varepsilon$; Beweis: der Ring enthält anfangs nur $c_0$; jede Annahme erfüllt $\\Delta\\le\\varepsilon$ oder liegt unter dem ersetzten Eintrag)",
     r"c_t\le c_0+t\,\varepsilon\quad\text{für alle } t;\qquad L=1:\ a_t=[\Delta_t\le\varepsilon]\ \text{(besser oder gleich)}"),
    ("Auswahlregeln (Skizze; Belohnung $r_t$ = Verkürzung der aktuellen Tour je Auswertung, durch $\\bar\\ell$ normiert und auf $[0,1]$ gekappt)",
     r"r_t=\min\Bigl(1,\ \frac{\max(0,-\Delta_t)}{\kappa_{h_t}\,\bar\ell}\Bigr)"),
    ("Zerlegung der Streuung: je Instanz zentriert $\\tilde y_{isr}=\\bar g_{isr}-\\overline{\\bar g}_{i}$, $m_s$, $m_r$, $m_{sr}$ Mittel über Instanzen (und die andere Achse)",
     r"SS_{\mathrm{Auswahl}}=I\,R\sum_s(m_s-m)^2,\qquad SS_{\mathrm{Akzeptanz}}=I\,S\sum_r(m_r-m)^2"),
    ("Wechselwirkung, Gesamtstreuung und Rest", r"SS_{\mathrm{WW}}=I\sum_{s,r}(m_{sr}-m_s-m_r+m)^2,\qquad SS_{\mathrm{ges}}=\sum_{i,s,r}\tilde y_{isr}^2,\qquad SS_{\mathrm{Rest}}=SS_{\mathrm{ges}}-SS_{\mathrm{Auswahl}}-SS_{\mathrm{Akzeptanz}}-SS_{\mathrm{WW}}"),
    ("Rauschen der Zufalls-Seeds (Anteil an der Gesamtstreuung der Zellmittel; $s^2_{isr}$ Varianz über die Zufalls-Seeds, $Z$ ihre Zahl)", r"\frac{1}{SS_{\mathrm{ges}}}\sum_{i,s,r}\frac{s^2_{isr}}{Z}"),
    ("Gepaarter Vergleich mit Zufall ($d>0$: die Regel ist besser)", r"d_i(r,s)=\bar g_{i,\mathrm{Zufall},r}-\bar g_{i,s,r}"),
    ("Rangkorrelation zweier Akzeptanzspalten (Pearson-Korrelation der Ränge der Zeilenmittel; Rang 1 = kleinster Abstand)", r"\rho(r,r')=\operatorname{corr}\bigl(\operatorname{rang}(\bar g_{\cdot r}),\ \operatorname{rang}(\bar g_{\cdot r'})\bigr)"),
)

FORMEL_NACHSATZ = """
**Was die Formeln nicht zeigen.** Der Rest der Zerlegung enthält die Streuung zwischen Instanz und Zelle **und** das Rauschen der Zufalls-Seeds; beide
sind nicht trennbar, das Rauschen wird deshalb gesondert ausgewiesen, als Schätzung ohne Zentrierung je Instanz (sie kann leicht über dem Rest liegen). Der **Permutationstest** der Wechselwirkung vertauscht die Reste je Instanz unter den
36 Zellen (2000 Vertauschungen, p = (Treffer + 1) / 2001; der kleinste mögliche Wert ist deshalb 1/2001 = 0,0005). Die Intervalle der gepaarten
Vergleiche sind Bootstrap-Perzentile über die Instanzen (SplitMix64), 95 % je Vergleich oder korrigiert für die Zahl der Vergleiche je Tafel
(Bonferroni). Nicht in der Formel: das Lernen der Auswahl, die Wahl der Zugmenge und der Referenzwert als Optimum (er ist keines).
"""

PRESET_HILFE_KOPF = "Lädt Zugart-Auswahl, Akzeptanzregel, Rundtour und Budget. Kein Preset nimmt ein Ergebnis vorweg."

_NIE = " Kein Preset nimmt ein Ergebnis vorweg: die Verdikte rechnen aus den Läufen."
C.PRESET_HELP.update({
    "Standardfall: Choice Function, nur besser": "Choice Function und „nur besser“ auf 30 gleichverteilten Städten, 50·n Auswertungen. Verändert Kernfrage 0 (ein Einzellauf), 1 und 5." + _NIE,
    "Late Acceptance: die Auswahl schadet": "Choice Function und Late Acceptance (L = 50), sonst wie der Standardfall. Kernfrage 0 zeigt angenommene Verlängerungen und den Abstand der letzten zur besten Tour; Kernfrage 1 vergleicht dieselbe Auswahl live mit Zufall unter allen sechs Akzeptanzregeln." + _NIE,
    "Late Acceptance: feste 2-opt-Wahl": "Feste Zugart 2-opt statt einer Lernregel, Late Acceptance (L = 50). Kernfrage 1 vergleicht die feste Wahl live mit Zufall; Kernfrage 5 hat bei festen Zugarten nichts zu lernen." + _NIE,
    "Kurze Liste (L = 10)": "Choice Function und Late Acceptance mit der kurzen Liste L = 10. Kernfrage 0 zeigt, wie sich die Annahmen und der Abstand zur besten Tour gegenüber L = 50 ändern; Kernfrage 3 zeigt die ganze Kurve über L (eingefroren)." + _NIE,
    "Großes Budget": "Choice Function und Late Acceptance (L = 50) mit 200·n Auswertungen. Verändert Kernfrage 0 und 5 (Zugart-Anteile bei großem Budget); Kernfrage 4 zeigt die Budgetreihe eingefroren." + _NIE,
    "Alle Züge annehmen (Gegenprobe)": "Zufall und „alle Züge annehmen“: als Suche wertlos, weil die aktuelle Tour sich vom Rekord entfernt. Kernfrage 0 zeigt, wie weit die letzte Tour über der besten liegt." + _NIE,
})
