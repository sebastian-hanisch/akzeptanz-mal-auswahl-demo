# Akzeptanz mal Auswahl: wer entscheidet in einer Hyperheuristik? – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-akzeptanz-mal-auswahl-demo.streamlit.app/)** -->

Vierte Demo der Reihe **„Hyperheuristiken erklärt“** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Vorgänger ist „Wer belohnt wen?“ (`auswahlregeln-demo`), die Kante heißt `fix`: Stück 3 vergleicht Auswahlregeln unter einer festgehaltenen Akzeptanzregel, und sein Satz „keine gelernte Regel schlägt Zufall“ gilt bei beiden Budgets unter Late Acceptance und bei 200·n mit der Standardbelohnung auch unter „nur besser“ und Rekord-zu-Rekord (bei 50·n liegen dort unter Rekord-zu-Rekord vier von fünf Regeln vor Zufall). Hier wechselt die **Akzeptanzregel**, und die Demo fragt, wann eine ungünstige Akzeptanzregel den Gewinn einer Auswahlregel zerstört. Nachfolger ist Stück 9 („Lohnt die Meta-Ebene?“), das die Tafel als Material liest.

Das Fahrzeug ist wie in der ganzen Linie eine erzeugte Rundtour (Städte in der Ebene, kürzeste geschlossene Tour gesucht; ein Modell, kein Datensatz). Instanzen, Zugarten, Akzeptanzregeln, Zufallsströme und die Auswahlregeln sind aus den Vorgängern kopiert (Kopier-Tests); eigen sind die Suche mit allen Akzeptanzregeln und Listenlängen, die Zerlegung der Streuung, die Messreihen und die App.

**Keine Neuheitsaussage:** Auswahl und Akzeptanz als zwei getrennte Bausteine einer Hyperheuristik sind Literaturstandard (Burke u. a. 2013, Stufe V; Bilgin u. a. 2007 und Özcan u. a. 2008, Stufe V: der Unterschied zwischen Auswahlverfahren sei weniger deutlich als der zwischen Akzeptanzregeln, die Akzeptanz beeinflusse die Leistung signifikant; Sobotka u. a., arXiv 2509.02782, Stufe V, Vorabdruck, nicht begutachtet: gleichverteilte Zufallsauswahl erreicht erst mit Umbau der Akzeptanz, der Wiederholung und der Störungsstärke Rang 2 der CHeSC-Wertung, Einstellungen auf derselben Benchmark gewählt; Razali u. a. 2025, Stufe V*, nur die ersten 100 000 von 259 000 Zeichen gelesen: Zugakzeptanz mit starkem Effekt, Schlüsse nur assoziativ, nicht kausal). Late Acceptance: Burke und Bykov 2008 und 2017 (Stufe A); Sintflut und Rekord-zu-Rekord: Dueck 1993 (A/S). Neu ist nur die kleine, ganz durchrechenbare Kreuzung mit eigenen Umsetzungen und gleicher Zähleinheit.

## Kernfrage

Hilft eine gelernte Auswahlregel gegen Zufall, schadet sie oder ändert sie nichts, wenn die Akzeptanzregel darunter wechselt, und wie viel der Streuung der Ergebnisse erklärt die Akzeptanz im Vergleich zur Auswahl?

**Befund als Aufhänger:** dieselbe Auswahl, sechs Akzeptanzregeln, drei Vorzeichen (der Satz mit den Zahlen steht unter „Befunde“). Die Aussage des Stücks heißt nicht „Akzeptanz zählt immer mehr“, sondern **„eine ungünstige Akzeptanzregel zerstört bei den Lernregeln Choice Function und Lernautomat den Gewinn gegenüber Zufall“**, mit diesen Voraussetzungen: Rundtour, n = 30 und 60, 50·n Auswertungen, eigene Umsetzungen, und „ungünstig“ heißt hier Late Acceptance mit L = 50 und mit L = 10, nicht Rekord-zu-Rekord; eine feste 2-opt-Wahl liegt unter Late Acceptance (L = 50) dagegen vorn (Tafel, Kernfrage 2). Der Gewinn selbst ist klein, und bei 200·n ist er in keinem der 30 Vergleiche belegt. Das passt zu den Vorgängern der Reihe: unter Rekord-zu-Rekord liegen bei kleinem Budget Choice Function und Lernautomat vor Zufall (UCB nach Korrektur für die Zahl der Vergleiche ohne belegten Unterschied), unter Late Acceptance liegen sie dahinter.

Die Rundtouren sind erzeugt; es gibt keine reale Datenquelle, und in den gelesenen Quellen gab es keine Messung, ob eine solche Auswahl- oder Akzeptanzregel in Logistik, Lager oder Fertigung bessere Entscheidungen liefert. Gezählt werden Auswertungen (bewertete Kandidaten); gleiche Auswertungszahl ist nicht gleiche Rechenzeit (Branke u. a. 2016, Stufe V), die Demo zeigt deshalb Anwendungen je Lauf als zweite Zähleinheit und nie Sekunden als Befund. Die Regeln sind eigene, vereinfachte Umsetzungen mit nicht abgestimmten Parametern.

**Klassenregel.** Diese Demo führt die Klassenregel von Stück 1 der Reihe (`klasse` aus `hhw_stats.py`, Marken 0,25 und 0,10 Prozentpunkte): „klar“ ab einem Unterschied von 0,25 mit Intervall ohne 0, „gleich“ unter 0,10 oder mit Intervall über 0, sonst „klein“; **Vorteil** heißt klar besser als Zufall, **Nachteil** klar schlechter. Stück 2 zählt mit ±0,25 und Stück 3 mit +0,25 und −0,10: Zählungen der drei Demos sind deshalb nicht dieselbe Einheit und können voneinander abweichen.

## Befunde und Korrekturen gegenüber der Vormessung

Die Planung stützte sich auf eine Vormessung mit dem Zufallsgenerator von numpy (180 Instanzen × 6 Zufalls-Seeds, andere Instanzen) und eine Planungsprobe mit SplitMix64 (30 Instanzen). Der Bau hat mit den Zufallsströmen der App (SplitMix64) neu gemessen und die Reihen M-A bis M-C selbst erzeugt (Instanzen 100 bis 149, nicht die der Vorgänger). **Größe der Messung:** 835 110 000 Auswertungen (Tafel 388 800 000, Budgetreihe 267 300 000, Listenlängen 162 000 000, Ende des Laufs 17 010 000), aus dem Lauf-Plan berechnet, nicht aus den Läufen gezählt; gerechnet mit 2 Prozessen in 690, 447, 298 und 22 Sekunden (Rechenzeit ist kein Befund, die Sekunden sind nicht nachgeprüft). Die Planung sah rund 800 Millionen Auswertungen vor; verkleinert wurde nichts, nur die Langläufe der Reihe M-D (Referenzen der Live-Instanzen) entfallen, weil `aka_refs.json` aus Stück 3 schon 200 Referenzwerte je Familie und n enthält. Die Spalte links ist die Erwartung der Planung (nicht im Test), rechts steht die Neumessung (im Test, `tests/test_claims.py`).

<!-- KORREKTUREN:START -->
| Aussage der Planung (Vormessung und Planungsprobe) | Neumessung |
|---|---|
| Choice Function gegen Zufall bei 50·n: nur besser +0,29, Rekord-zu-Rekord +0,74, Annealing +0,42, Sintflut +0,34, Late Acceptance −1,97, Late Acceptance mit L = 10 −0,66 | +0,11, +0,75, +0,37, +0,17, −1,77, −0,75; gleiche Vorzeichen, unter „nur besser“ und Sintflut kein belegter Unterschied |
| Die Akzeptanz erklärt bei 50·n 51,5 % der Streuung der Zellmittel (alle sechs Akzeptanzregeln), ohne Late Acceptance 13,4 %; die Auswahl 1,3 % und 1,5 % | 53,7 % und 15,3 %; Auswahl 1,1 % und 1,1 % |
| Bei 200·n erklärt die Akzeptanz 11,2 %, die Auswahl 8,5 % | 10,6 % und 10,5 %: kein Faktor 2, der Rest ist Rauschen und Streuung zwischen Instanz und Zelle |
| Rangkorrelation von Late Acceptance gegen nur besser, Rekord-zu-Rekord, Annealing, Sintflut: −0,37 / −0,83 / −0,60 / −0,66, mit L = 10: −0,20 / −0,71 / −0,54 / −0,49 (der Wert −0,94 des Zuschnitts stammt aus anderen sechs Zeilen und fünf Akzeptanzregeln) | −0,31 / −0,83 / −0,77 / −0,71; mit L = 10: −0,14 / −0,71 / −0,60 / −0,54; Rangumkehr (unter −0,5) gegen 3 und 3 von 4 Akzeptanzregeln, bei 200·n gegen 0 und 0 |
| Zählung gegen Zufall in 30 Vergleichen (Vorteile / Nachteile / unentschieden, je Vergleich 95 %): 50·n 14 / 6 / 10, 200·n 0 / 16 / 14; mit Korrektur 8 / 6 / 16 und 0 / 16 / 14 | 50·n 10 / 6 / 14, 200·n 0 / 18 / 12; mit Korrektur 8 / 5 / 17 und 0 / 17 / 13: weniger Vorteile unter „nur besser“ und Sintflut, alle Nachteile bei kleinem Budget weiter unter Late Acceptance |
| Late Acceptance mit L = 10 ist bei 50·n in 6 von 6 Auswahlzeilen schlechter als „nur besser“, bei 200·n in 6 von 6 besser | bei 50·n schlechter in 6 von 6, bei 200·n besser in 5 von 6 (Auswahlzeilen, Zellmittel) |
| Unter Rekord-zu-Rekord gewinnen bei 50·n Choice Function +1,14 und Lernautomat +0,84 gegen Zufall (Stücke 2 und 3, 120 Instanzen × 3 Läufe, andere Instanzen) | Choice Function +0,75, Lernautomat +0,64, UCB +0,31: gleiches Vorzeichen, kleinere Beträge als in den Vorgängern (andere Instanzen, 6 statt 3 Zufalls-Seeds, 180 statt 120 Instanzen) |
| Anteil der Anwendungen auf `2opt_b5` bei der Choice Function unter Late Acceptance / Rekord-zu-Rekord / „nur besser“: 63,6 / 51,6 / 17,7 % (bis 200·n) | 61,5 / 51,6 / 17,7 % |
| Late Acceptance nimmt 4,00 % der Anwendungen an, davon 42,3 % ohne strenge Verbesserung; die letzte Tour liegt 1,19 % über der besten (Probe, 120 Läufe) | 4,06 % angenommen, davon 42,2 % ohne strenge Verbesserung, am Ende 1,20 % über der besten Tour (Zufall, 50·n, 1 080 Läufe) |
| „Alle Züge annehmen“: Abstand zum besten bekannten Wert 21,7 %, unter Late Acceptance 10,2 % (Mittel über sechs Zellen, Vormessung) | Abstand zum besten bekannten Wert 21,1 %, unter Late Acceptance 9,8 % (Zufall, 50·n, 180 Instanzen) |
| Kipp-Länge der Choice Function gegen Zufall: bei 50·n zwischen L = 2 und 5, bei 200·n zwischen L = 20 und 50 (Probe, 30 Instanzen, ohne Intervalle) | bei 50·n: Vorteil bei keinem L, Nachteil ab L = 10; bei 200·n: Vorteil bei keinem L, Nachteil ab L = 30 (60 Instanzen, Klasse nach 95-%-Intervall) |
| Budgetreihe: unter „nur besser“ und Rekord-zu-Rekord bei 50·n Vorteil bei 1 und 4 von 5 Auswahlzeilen, bei 200·n bei 0 | bei 50·n 0 und 3 von 5 (Late Acceptance 1), bei 200·n 0, 0 und 0 (Intervalle nach Bonferroni für 25 Vergleiche je Stufe) |
| Ein Messlauf unterbot die Langläufe der Referenz in 49 von 180 Instanzen | in 55 von 180 Instanzen |
| Der p-Wert der Wechselwirkung 0,0005 ist der kleinste Wert bei 2 000 Vertauschungen | bestätigt: kein Treffer in 2 000 Vertauschungen bei 50·n und bei 200·n |
<!-- KORREKTUREN:ENDE -->

## Modell

Eine Suche startet mit der Nächster-Nachbar-Tour. In jeder Anwendung wählt die **Auswahlregel** eine Zugart, die Zugart bewertet einen zufälligen Vorschlag (eine Auswertung; `2opt_b5` bis zu fünf), die **Akzeptanzregel** entscheidet, ob er bleibt, und die Auswahlregel bekommt die Standardbelohnung (Verkürzung der aktuellen Tour je Auswertung). Das Budget ist eine Zahl von Auswertungen (50·n bis 800·n). Die Formeln (Suche, sechs Akzeptanzregeln, Invarianten, Zerlegung der Streuung, Permutationstest, Rangkorrelation; die Auswahlregeln als Skizze) stehen im Expander „📐 Mathematische Formulierung“ der App. Das Zerlegungsmodell ist vollständig, die Auswahlregeln nicht: ihr vollständiges Modell gehört zu „Wer belohnt wen?“.

## Methodik

* **Acht Zugarten** (wie in der Linie): `swap`, `insert`, `2opt`, `2opt_lokal`, `oropt2`, `oropt3`, `dbridge`, `2opt_b5`.
* **Sechs Auswahlzeilen:** Zufall, UCB (c = 0,2, γ = 0,995), Choice Function (α = 0,9), Lernautomat (a = 0,05), nur 2-opt, nur `2opt_b5`; die Lernregeln mit der Standardbelohnung.
* **Sechs Akzeptanzregeln in der Tafel:** „nur besser“, Rekord-zu-Rekord (ρ = 1 %), Annealing-Akzeptanz (Temperatur von 0,3 auf 0,003 mittlere Kantenlängen), Sintflut (Pegel von 100 % auf 80 % der Startlänge), Late Acceptance mit L = 50 und mit L = 10; in der App zusätzlich Late Acceptance mit jedem L von 1 bis 200 und die Gegenprobe „alle Züge annehmen“.
* **Tafel (M-A):** 6 Auswahlzeilen × 6 Akzeptanzregeln × 2 Stufen (50·n und 200·n), 180 Instanzen (3 Familien × n = 30 und 60 × Instanzen 100 bis 129), 6 Zufalls-Seeds. „Nur besser“, Rekord-zu-Rekord und Late Acceptance rechnen die Stufe 50·n als Kontrollpunkt eines Laufs bis 200·n (ihr Ergebnis hängt bis auf die gekürzte letzte Anwendung von `2opt_b5` nicht am Gesamtbudget), Annealing und Sintflut als eigene Läufe je Stufe.
* **Budgetreihe (M-B):** dieselben 6 Zeilen, 5 Akzeptanzregeln, Stufen 50·n bis 800·n, 60 Instanzen (130 bis 139), 3 Zufalls-Seeds. **Listenlängen (M-C):** 5 Zeilen (ohne Lernautomat, Rechenlast), 10 Längen von 1 bis 200, Stufen 50·n bis 400·n, 60 Instanzen (140 bis 149), 3 Zufalls-Seeds, dazu Annahmequote, Anteil nicht streng verbessernder Annahmen und Abstand der aktuellen zur besten Tour im Mittel über den Lauf.
* **Vergleichszahl:** Abstand zum besten bekannten Wert je Instanz in Prozent (Minimum aus den Langläufen von `zugmenge-demo` und allen Läufen der Reihe). Unterschied = Abstand(Zufall) − Abstand(Zeile), gepaart je Instanz (gleiche Starttour, gleicher Zufallsstrom), Mittel über die Zufalls-Seeds; Intervall = Bootstrap über die Instanzen (40 000 Ziehungen, SplitMix64), je Vergleich 95 % oder korrigiert nach Bonferroni für die Zahl der Vergleiche je Tafel (30, in der Budgetreihe 25).
* **Zerlegung:** Abstand je Instanz zentriert, Quadratsummen von Auswahl, Akzeptanz, Wechselwirkung und Rest (Formeln in der App); das Rauschen der Zufalls-Seeds wird gesondert ausgewiesen. **Permutationstest** der Wechselwirkung mit 2 000 Vertauschungen: der kleinste mögliche p-Wert ist 1/2001 = 0,0005, kein gemessener Wert.
* **Live (Kernfrage 1 und 5):** kleine Stichproben (15 Instanzen × 2 Zufalls-Seeds bei n = 30, 6 × 2 bei n = 60), höchstens 600 000 Auswertungen je Klick (Zählung vor dem Start), Intervalle nach Bonferroni für 6 Vergleiche. **Die Live-Stichprobe ist zu klein für Unterschiede unter etwa zwei Prozentpunkten** (Halbbreite des Intervalls bei der Choice Function 1,0 bis 2,5): die Demo stellt die eingefrorene Zahl daneben.

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen dieses Abschnitts: eingefrorene Messung (`aka_frozen.json`), erzeugte Rundtouren mit 30 oder 60 Städten aus drei Familien, Abstand zum besten bekannten Wert, eigene Umsetzungen mit festen Parametern. Unterschiede in Prozentpunkten des Abstands. Die Sätze werden von `tools/aka_readme.py` aus derselben Quelle geschrieben wie die Texte der App.

<!-- MESSUNG:START -->
**Kernfrage 1: Schlägt dieselbe Auswahlregel Zufall, wenn die Akzeptanzregel wechselt?** **Eingefroren (180 Instanzen × 6 Zufalls-Seeds, 50·n Auswertungen):** Unterschied „Zufall minus Choice Function“ in Prozentpunkten (positiv: Choice Function besser; in Klammern die Klasse nach 95-%-Intervall): „nur besser“ +0,11 (unentschieden); Rekord-zu-Rekord +0,75 (Vorteil); Annealing +0,37 (Vorteil); Sintflut +0,17 (unentschieden); Late Acceptance (L = 50) −1,77 (Nachteil); Late Acceptance (L = 10) −0,75 (Nachteil). Dieselbe Auswahl liegt je nach Akzeptanzregel vor, gleichauf oder hinter Zufall; die Größe des Gewinns ist klein.

**Kernfrage 0: Annahme und Wanderung** **Eingefroren (Zufall, 50·n, Mittel über 180 Instanzen × 6 Zufalls-Seeds):** „nur besser“: 0,94 % der Anwendungen angenommen, davon 0,0 % ohne strenge Verbesserung, am Ende 0,00 % über der besten Tour (im Mittel über den Lauf 0,00 %); Rekord-zu-Rekord: 3,60 % der Anwendungen angenommen, davon 45,3 % ohne strenge Verbesserung, am Ende 0,53 % über der besten Tour (im Mittel über den Lauf 0,51 %); Late Acceptance (L = 50): 4,06 % der Anwendungen angenommen, davon 42,2 % ohne strenge Verbesserung, am Ende 1,20 % über der besten Tour (im Mittel über den Lauf 1,42 %); Late Acceptance (L = 10): 1,73 % der Anwendungen angenommen, davon 22,7 % ohne strenge Verbesserung, am Ende 0,22 % über der besten Tour (im Mittel über den Lauf 0,36 %); „alle Züge annehmen“: am Ende 262 % über der besten Tour und 0,1 % Gewinn gegen die Startlösung. Die Zahl der Annahmen allein unterscheidet Rekord-zu-Rekord und Late Acceptance nicht (ähnlich viele Verschlechterungen); der Abstand der aktuellen zur besten Tour tut es (am Ende 1,20 gegen 0,53 % über der besten Tour).

**Kernfrage 2: Wie viel der Streuung erklärt die Akzeptanz?** **Eingefroren:** bei 50·n erklärt die Akzeptanz 53,7 % der Streuung der Zellmittel und die Auswahl 1,1 %, aber **ohne Late Acceptance (L = 50 und L = 10) nur 15,3 %**; bei 200·n sind es 10,6 % und 10,5 %. Der p-Wert der Wechselwirkung bei 50·n ist 0,0005, der kleinste Wert bei 2 000 Vertauschungen. Bei 50·n erklärt die Akzeptanz auch ohne Late Acceptance mehr als die Auswahl (15,3 gegen 1,1 %), aber weniger als mit; bei 200·n sind beide etwa gleich groß (10,6 und 10,5 %).

**Kernfrage 2: Spannweiten** **Spannweiten der Zellmittel (50·n):** über die Auswahl innerhalb einer Akzeptanzregel 0,24 bis 3,61 Prozentpunkte, über die Akzeptanz innerhalb einer Auswahlzeile 2,60 bis 6,34. Spielraum der Tafel: kleinster Zellwert 5,72 %, größter 12,06 %. **Spannweiten der Zellmittel (200·n):** über die Auswahl innerhalb einer Akzeptanzregel 0,37 bis 2,21 Prozentpunkte, über die Akzeptanz innerhalb einer Auswahlzeile 0,87 bis 1,95. Spielraum der Tafel: kleinster Zellwert 2,77 %, größter 5,25 %.

**Kernfrage 3: Bei welcher Listenlänge kippt die Auswahl?** **Eingefroren (Zufall, Auswahl und Listenlänge):** Zufall liegt bei 50·n mit L = 1 bei 5,94 % und mit L = 200 bei 12,22 %. Choice Function bei 50·n: Vorteil bei keinem L, Nachteil ab L = 10; Choice Function bei 200·n: Vorteil bei keinem L, Nachteil ab L = 30; nur 2-opt bei 50·n: Vorteil ab L = 20, Nachteil bei keinem L; nur 2-opt bei 200·n: Vorteil bei L = 200, Nachteil bei L = 1, 2, 5, 10, 20, 30, 50. Die Klassen gelten nur mit Auswahl, Stufe und n; ob die Entfernung vom Rekord die Ursache ist, ist hier nicht isoliert.

**Kernfrage 5: Was lernt die Auswahl unter welcher Akzeptanz?** **Eingefroren (Anteil von `2opt_b5` an den Anwendungen, in Klammern an den Auswertungen, bis 200·n):** Choice Function: unter „nur besser“ 17,7 % (51,9 %), unter Rekord-zu-Rekord 51,6 % (84,2 %), unter Late Acceptance 61,5 % (88,9 %); Lernautomat: unter „nur besser“ 41,1 % (77,7 %), unter Rekord-zu-Rekord 68,3 % (91,5 %), unter Late Acceptance 72,8 % (93,1 %); Zufall 12,5 % (41,6 %) bei Gleichverteilung 12,5 % (41,7 %). Die Lernregel verteilt die Zugarten unter der Akzeptanz anders; die Ursache ist hier nicht isoliert (die Belohnungsfrage gehört zur Demo „Wer belohnt wen?“).
<!-- MESSUNG:ENDE -->

## Ehrliche Grenzen

<!-- ANNAHMEN:START -->
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
<!-- ANNAHMEN:ENDE -->

## Verifikation

* **Kern:** jede Zugart gegen die Mini-Instanz und die volle Neubewertung der Länge nach jedem angenommenen Zug; jede Akzeptanzregel an der Folge von Änderungen des Handbeispiels (angenommene Schritte und Endkosten von Hand gerechnet); die Spielzeugfolge der Kreditzuweisung (Belohnungssummen 17,0 und 13,5); jede Einheit abschaltbar mit Wirkung (je zwei Akzeptanzregeln weichen auf mindestens einer Instanz voneinander ab; Ausnahme: Late Acceptance mit L = 1 und „nur besser“ sind praktisch dieselbe Regel, bis auf Züge mit |Δ| ≤ 10⁻⁹).
* **Orakel (`tests/test_oracle_akzeptanz.py`):** exakte Wahrheit bei n = 8 und 9 (Aufzählung und Held-Karp als zwei Rechenwege), die Suche liegt nie darunter; Replay der Akzeptanz durch eine naive Neuimplementierung der Regeln aus den Formeln, die in jedem Schritt von 9 Akzeptanznamen dieselbe Entscheidung trifft; Zerlegung gegen eine Fassung mit Entwurfsmatrix und gegen die 2 × 2-Handrechnung; Rangkorrelation gegen `scipy.stats.spearmanr`; Permutationstest unter einer Tafel ohne Wechselwirkung; Bootstrap-Intervall.
* **Eigenschaften:** gleicher Zufalls-Seed gleiche Ausgabe; „nur besser“ ist monoton; Invariante von Late Acceptance (aktuelle Länge höchstens Startlänge plus t mal Toleranz ε); L = 1 und Rekord-zu-Rekord mit ρ = 0 bitgleich zu „nur besser“ (in den geprüften Läufen; Züge mit |Δ| ≤ 10⁻⁹ könnten abweichen); „alle Züge“ mit Annahmerate genau 1; Skalieren der Koordinaten mit 8 und Umnummerieren der Orte ändern nichts; Wiedergabe der angenommenen Züge gleich Neulauf bis Anwendung k; die Suche verbraucht genau das Budget.
* **Kopier-Tests:** neun Module bis auf das Präfix gleich den Quellen (Stück 3), Zufallsvorlage bytegleich, Konstanten gleich; die eigene Suche ist für die sechs gemeinsamen Akzeptanzregeln bitgleich zur Kopie.
* **Eingefrorene Messung (`tests/test_frozen.py`):** Schema, Größe, endliche Werte, Abstände nicht negativ; drei Instanzen mit allen Zufalls-Seeds neu gerechnet als Band (höchstens 3 Standardfehler, mindestens 0,05 Punkte); Zerlegung, Rangkorrelation, Permutationstest und Intervalle aus den gespeicherten Abständen neu gerechnet. Nicht bitgleich über Plattformen (`math.exp`, `math.log`); der Linux-Check (`demo_linux_check.py`) steht vor dem ersten Push aus.
* **Aussagen:** `tests/test_claims.py` rechnet jede Zahl der README aus der Messdatei nach, der Messblock der README ist der erzeugte; `tests/test_verdicts.py` prüft Schwellen und jede Zahl im Text der Verdikte mit Nullwächtern.
* **Presets, Layout, App:** vollständig, Werte innerhalb der Reglergrenzen, aktives Preset hervorgehoben, jede Regleränderung hebt die Markierung auf; AppTest für jedes Preset und jede Auswahlregel unter jeder Akzeptanzregel, Permalink, Live-Knöpfe, Hinweise statt leerer Vergleiche, Zeitgrenze am Reglermaximum; Footer und Laufzeit-Importe.

**Tests:** 667 Tests (`pytest tests`).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `app.py` | Streamlit-App (Gerüst nach DEMO-PLAYBOOK §2) |
| `aka_constants.py` | Zugarten, Instanzen, Stufen, Akzeptanzregeln, Auswahlzeilen, Marken, Regler-Grenzen, Farben, Presets |
| `aka_rng.py`, `aka_rngblock.py` | Zufallsgenerator SplitMix64 (Vorlage) und blockweise Fassung, bitgleich (Kopien) |
| `aka_scenario.py`, `aka_moves.py`, `aka_accept.py`, `aka_stats.py` | Instanzen, acht Zugarten, Akzeptanzregeln (nur besser, Rekord-zu-Rekord, Late Acceptance, Sintflut, Annealing), Klassenregel (Kopien aus Stück 3) |
| `aka_select.py`, `aka_regeln.py`, `aka_belohnung.py` | Auswahlregeln und Belohnungsformen (Kopien aus Stück 3) |
| `aka_search.py` | die Suche mit jeder Listenlänge von Late Acceptance, „alle Züge“ und Zählständen (eigene Fassung) |
| `aka_algorithm.py` | ein Lauf mit Auswahlzeile und Akzeptanzregel, Referenzwerte, Wiedergabe der Spur |
| `aka_experiments.py` | Live-Experimente mit Zählung der Auswertungen vor dem Start |
| `aka_evaluation.py` | Zerlegung, Permutationstest, Rangkorrelation, Bootstrap, Klassen, alle Verdikte |
| `aka_frozen.py`, `aka_frozen.json` | Lesen und Schemaprüfung der eingefrorenen Messung (Tafel, Budgetreihe, Listenlängen, Ende des Laufs) |
| `aka_refs.json` | beste bekannte Werte von 1 200 Instanzen (200 je Familie und n, Kopie aus Stück 3) |
| `aka_saetze.py`, `aka_texts.py` | Sätze und Tabellen mit Messzahlen (aus der Datei gerechnet), feste Texte, Formeln |
| `aka_presets.py`, `aka_layout.py`, `aka_visualization.py`, `modul_frisch.py` | Presets und Permalink, fester Kopf, Plotly-Abbildungen, Neuladen der Hilfsmodule |
| `tools/aka_make_frozen.py` | erzeugt `aka_frozen.json` (`messen`, `bauen`, `--check`) |
| `tools/aka_readme.py` | schreibt Messblock, Korrekturen und Annahmen in die README (`--check`) |
| `tests/` | Kern, Handbeispiele, Orakel, Eigenschaften, Kopien, eingefrorene Messung, Aussagen, Verdikte, Presets, Layout, App, Footer, Laufzeit-Importe |
| `requirements.txt` | Laufzeit-Bibliotheken (streamlit, numpy, plotly) |
| `requirements-dev.txt` | Laufzeit plus pytest und scipy (Gegenprobe der Rangkorrelation) |

## Bewusst nicht enthalten

* Belohnungsformen und Kreditzuweisung (Demo „Wer belohnt wen?“), die Wahl der Zugmenge (Demo „Die Zugmenge entscheidet“).
* Q-Lernen und Zufallsgradient als Auswahlzeilen (stehen in „Wer belohnt wen?“); Thompson-Sampling.
* Abstimmen der Parameter der Akzeptanzregeln oder von L, Lernen der Akzeptanzregel („Akzeptanz selbst als Auswahl“).
* Zustandsabhängige Auswahl; Erzeugen von Regeln; Sprachmodelle; HyFlex; irace.
* Budgets über 800·n, n über 60 oder unter 30; andere Fahrzeuge (Einplanung, Packen); Schranken und ein Optimum für n ≥ 30.
* Sekunden als Befund; Nutzen im Betrieb; die Ursache des Schadens von Late Acceptance (nur Hypothesen und Messungen daneben); „besser oder gleich“ als eigene Spalte (L = 1 ist praktisch dieselbe Regel wie „nur besser“).

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und numpy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Hyperheuristiken: Auswählen und Erzeugen](https://sebastianhanisch.net/konzepte-hyperheuristiken.html).
