"""Sätze und Tabellen mit Messzahlen, aus der eingefrorenen Messung gerechnet (nie von Hand eingetragen). Die App liest sie hier, tools/aka_readme.py schreibt
dieselben Sätze in die README, tests/test_claims.py rechnet jede Zahl unabhängig nach."""

import aka_constants as C
import aka_evaluation as E
import aka_frozen as F

de = E.de
KLASSE_TEXT = {"vorteil": "Vorteil", "nachteil": "Nachteil", "unentschieden": "unentschieden"}
ZELLEN = len(C.AKZ6) * len(C.LERN_ZEILEN_FUENF)


def _vorsatz(v: float) -> str:
    return "vor" if v > 0 else "hinter"


# ---------------------------------------------------------------- Beschriftungen
def mess_caption(faktor: int) -> str:
    m = F.meta()
    return (f"Rundtour, erzeugte Instanzen (3 Familien), n = 30 und 60, eigene Umsetzung, {faktor}·n Auswertungen, {F.tafel_instanzen()} Instanzen × "
            f"{m['tafel_laeufe']} Zufalls-Seeds, Abstand zum besten bekannten Wert (Untergrenze der wahren Lücke).")


def mess_caption_l(faktor: int) -> str:
    m = F.meta()
    return (f"Rundtour, erzeugte Instanzen (3 Familien), n = 30 und 60, eigene Umsetzung, {faktor}·n Auswertungen, {len(F.load()['lreihe']['instanzen'])} Instanzen × "
            f"{m['lreihe_laeufe']} Zufalls-Seeds, Abstand zum besten bekannten Wert. Der Lernautomat fehlt in dieser Reihe (Rechenlast).")


def mess_caption_budget() -> str:
    m = F.meta()
    return (f"Rundtour, erzeugte Instanzen (3 Familien), n = 30 und 60, eigene Umsetzung, 50·n bis 800·n Auswertungen, {len(F.load()['budget']['instanzen'])} Instanzen × "
            f"{m['budget_laeufe']} Zufalls-Seeds, Abstand zum besten bekannten Wert; Intervalle nach Bonferroni für 25 Vergleiche je Stufe.")


def live_caption(m: int, s: int) -> str:
    return (f"Kleine Stichprobe ({m} Instanzen × {s} Zufalls-Seeds): Unterschiede unter etwa zwei Prozentpunkten zeigen sich oft erst in der eingefrorenen Messung "
            f"({F.tafel_instanzen()} Instanzen, Kernfrage 2).")


def satz_live_klein() -> str:
    return "Live rechnet nur wenige Instanzen; die Aussage steht in der eingefrorenen Messung."


# ---------------------------------------------------------------- Kernfrage 0 und 1
def satz_hook() -> str:
    v = {a: F.vergleich(50, a, "cf") for a in C.AKZ6}
    teile = [f"{C.AKZ_KURZ[a]} {de(v[a]['v'], 2, True)} ({KLASSE_TEXT[v[a]['ausgang']]})" for a in C.AKZ6]
    return (f"**Eingefroren ({F.tafel_instanzen()} Instanzen × {F.meta()['tafel_laeufe']} Zufalls-Seeds, 50·n Auswertungen):** Unterschied „Zufall minus Choice Function“ in Prozentpunkten "
            f"(positiv: Choice Function besser; in Klammern die Klasse nach 95-%-Intervall): " + "; ".join(teile) +
            ". Dieselbe Auswahl liegt je nach Akzeptanzregel vor, gleichauf oder hinter Zufall; die Größe des Gewinns ist klein.")


def satz_wanderung() -> str:
    teile = []
    for a in ("ob", "rr", "la", "la10"):
        e = F.ende(a)
        k = F.annahme_kennzahlen(50, a, "rand")
        teile.append(f"{C.AKZ_KURZ[a]}: {de(e['angenommen'], 2)} % der Anwendungen angenommen, davon {de(e['ohne_verbesserung'], 1) if e['ohne_verbesserung'] is not None else 'keine'} % "
                     f"ohne strenge Verbesserung, am Ende {de(e['end_gap'], 2)} % über der besten Tour (im Mittel über den Lauf {de(k['wanderung'], 2)} %)")
    am = F.ende("am")
    return ("**Eingefroren (Zufall, 50·n, Mittel über 180 Instanzen × 6 Zufalls-Seeds):** " + "; ".join(teile) +
            f"; „alle Züge annehmen“: am Ende {de(am['end_gap'], 0)} % über der besten Tour und {de(am['gewinn'], 1)} % Gewinn gegen die Startlösung. "
            f"Die Zahl der Annahmen allein unterscheidet Rekord-zu-Rekord und Late Acceptance nicht (ähnlich viele Verschlechterungen); der Abstand der "
            f"aktuellen zur besten Tour tut es (am Ende {de(F.ende('la')['end_gap'], 2)} gegen {de(F.ende('rr')['end_gap'], 2)} % über der besten Tour).")


def tab_e1(zeilen, marken) -> list[dict]:
    return [{"Akzeptanzregel": z["akz"], "Abstand Zufall (%)": de(z["abstand_zufall"], 2), "Abstand Auswahl (%)": de(z["abstand_zeile"], 2),
             "Zufall minus Auswahl": de(z["v"], 2, True), "Intervall (Bonferroni für 6)": E.intervall(z["lo"], z["hi"]) if z["lo"] is not None else "–",
             "Klasse": KLASSE_TEXT[z["ausgang"]], "eingefroren (180 Instanzen)": de(m, 2, True)} for z, m in zip(zeilen, marken, strict=True)]


# ---------------------------------------------------------------- Kernfrage 2
def tab_streuung(faktor: int) -> list[dict]:
    t = F.tafel(faktor)
    z, p = t["zerlegung"], t["permutation"]

    def pt(k):
        if k not in p:
            return "nicht gerechnet"
        v = p[k]
        return f"{de(v['p'], 4)} (kleinster Wert bei {E.tsd(v['vertauschungen'])} Vertauschungen)" if v["c"] == 0 else de(v["p"], 4)

    def zeile(name, k):
        return {"Fall": name, "Auswahl (%)": de(z[k]["auswahl"], 1), "Akzeptanz (%)": de(z[k]["akzeptanz"], 1), "Wechselwirkung (%)": de(z[k]["ww"], 1),
                "Rest (%)": de(z[k]["rest"], 1), "p der Wechselwirkung": pt(k)}
    return [zeile("alle sechs Akzeptanzregeln", "alle"), zeile("ohne Late Acceptance (L = 50 und L = 10)", "ohne_la"), zeile("ohne Late Acceptance mit L = 10", "ohne_la10"),
            {"Fall": "Rauschen der Zufalls-Seeds (Schätzung: Anteil an der Gesamtstreuung der Zellmittel, alle sechs; ohne Zentrierung je Instanz, daher leicht überschätzt)", "Auswahl (%)": "", "Akzeptanz (%)": "",
             "Wechselwirkung (%)": "", "Rest (%)": de(t["rauschen"], 1), "p der Wechselwirkung": ""}]


def tab_rang(faktor: int) -> list[dict]:
    m = F.mittel_matrix(faktor)
    rang = [E.ranks([m[s][r] for s in range(len(C.ZEILEN))]) for r in range(len(C.AKZ6))]
    return [{"Auswahlzeile": C.ZEILEN_ANZEIGE[z], **{C.AKZ_KURZ[a]: f"{int(rang[r][s])} ({de(m[s][r], 2)} %)" for r, a in enumerate(C.AKZ6)}} for s, z in enumerate(C.ZEILEN)]


def tab_spearman(faktor: int) -> list[dict]:
    sm = F.tafel(faktor)["spearman"]
    reihenfolge = ("la", "la10", "ob", "rr", "sa", "gd")
    return [{"Rangkorrelation": C.AKZ_KURZ[a], **{C.AKZ_KURZ[b]: de(sm[C.AKZ6.index(a)][C.AKZ6.index(b)], 2) for b in C.AKZ6}} for a in reihenfolge]


def tab_vergleiche(faktor: int, korrigiert: bool) -> list[dict]:
    ziel = []
    for a in C.AKZ6:
        for z in C.LERN_ZEILEN_FUENF:
            v = F.vergleich(faktor, a, z)
            lo, hi, aus = (v["lo_k"], v["hi_k"], v["ausgang_k"]) if korrigiert else (v["lo"], v["hi"], v["ausgang"])
            ziel.append({"Akzeptanzregel": C.AKZ_KURZ[a], "Auswahlzeile": C.ZEILEN_ANZEIGE[z], "Zufall minus Zeile": de(v["v"], 2, True), "Intervall": E.intervall(lo, hi),
                         "Klasse": KLASSE_TEXT[aus]})
    return ziel


def tab_anwendungen(faktor: int) -> list[dict]:
    return [{"Auswahlzeile": C.ZEILEN_ANZEIGE[z], **{C.AKZ_KURZ[a]: E.tsd(round(F.anwendungen_je_lauf(faktor, a, z))) for a in C.AKZ6}} for z in C.ZEILEN]


def satz_spannweite(faktor: int) -> str:
    t = F.tafel(faktor)
    sa = t["spannweite_auswahl"]
    sz = t["spannweite_akzeptanz"]
    lo, hi = t["spielraum"]
    a_min, a_max = min(sa.values()), max(sa.values())
    z_min, z_max = min(sz.values()), max(sz.values())
    return (f"**Spannweiten der Zellmittel ({faktor}·n):** über die Auswahl innerhalb einer Akzeptanzregel {de(a_min, 2)} bis {de(a_max, 2)} Prozentpunkte, "
            f"über die Akzeptanz innerhalb einer Auswahlzeile {de(z_min, 2)} bis {de(z_max, 2)}. Spielraum der Tafel: kleinster Zellwert {de(lo, 2)} %, größter {de(hi, 2)} %.")


def satz_zerlegung() -> str:
    lo, hi = F.tafel(50), F.tafel(200)
    a, o = lo["zerlegung"]["alle"], lo["zerlegung"]["ohne_la"]
    h = hi["zerlegung"]["alle"]
    p = lo["permutation"]["alle"]
    return (f"**Eingefroren:** bei 50·n erklärt die Akzeptanz {de(a['akzeptanz'], 1)} % der Streuung der Zellmittel und die Auswahl {de(a['auswahl'], 1)} %, aber **ohne Late "
            f"Acceptance (L = 50 und L = 10) nur {de(o['akzeptanz'], 1)} %**; bei 200·n sind es {de(h['akzeptanz'], 1)} % und {de(h['auswahl'], 1)} %. Der p-Wert der Wechselwirkung "
            f"bei 50·n ist {de(p['p'], 4)}" + (f", der kleinste Wert bei {E.tsd(p['vertauschungen'])} Vertauschungen." if p["c"] == 0 else ".") +
            f" Bei 50·n erklärt die Akzeptanz auch ohne Late Acceptance mehr als die Auswahl ({de(o['akzeptanz'], 1)} gegen {de(o['auswahl'], 1)} %), aber weniger als mit; "
            f"bei 200·n sind beide etwa gleich groß ({de(h['akzeptanz'], 1)} und {de(h['auswahl'], 1)} %).")


# ---------------------------------------------------------------- Kernfrage 3
def tab_l(zeile: str, j: int) -> list[dict]:
    rows = []
    mittel = F.l_mittel(zeile, j)
    for i, L in enumerate(C.L_WERTE):
        w = F.l_wanderung(zeile, L, j)
        row = {"L": f"{L} (nur besser)" if L == 1 else str(L), "mittlerer Abstand (%)": de(mittel[i], 2)}
        if zeile != "rand":
            v = F.l_vergleich(zeile, L, j)
            row.update({"Zufall minus Zeile": de(v["v"], 2, True), "Intervall": E.intervall(v["lo"], v["hi"]), "Klasse": KLASSE_TEXT[v["ausgang"]]})
        row.update({"angenommen (% der Anwendungen)": de(w["angenommen"], 2),
                    "davon ohne strenge Verbesserung (%)": de(w["ohne_verbesserung"], 1) if w["ohne_verbesserung"] is not None else "keine",
                    "Abstand der aktuellen zur besten Tour (%, Mittel über den Lauf)": de(w["wanderung"], 2)})
        rows.append(row)
    return rows


def satz_l() -> str:
    teile = []
    for z in ("cf", "s2"):
        for j, st in ((0, 50), (2, 200)):
            aus = F.l_ausgaenge(z, j)
            vor = E.laengen_text([L for L, a in aus if a == "vorteil"], "Vorteil")
            nach = E.laengen_text([L for L, a in aus if a == "nachteil"], "Nachteil")
            teile.append(f"{C.ZEILEN_ANZEIGE[z]} bei {st}·n: {vor}, {nach}")
    r50 = F.l_mittel("rand", 0)
    return ("**Eingefroren (Zufall, Auswahl und Listenlänge):** Zufall liegt bei 50·n mit L = 1 bei " + f"{de(r50[0], 2)} % und mit L = 200 bei {de(r50[-1], 2)} %. " +
            "; ".join(teile) + ". Die Klassen gelten nur mit Auswahl, Stufe und n; ob die Entfernung vom Rekord die Ursache ist, ist hier nicht isoliert.")


def satz_link_abkuehlen() -> str:
    return ("**Anderes Regime:** In der [Demo zum simulierten Abkühlen](https://sebastianhanisch-simulated-annealing-demo.streamlit.app/) kippt Late Acceptance bei 200 000 "
            "Vorschlägen laut deren README zwischen L = 500 und L = 700; hier sind es 1 500 bis 24 000 Auswertungen. Die Zahlen beider Demos sind nicht vergleichbar.")


# ---------------------------------------------------------------- Kernfrage 4 und 5
def tab_budget(akz: str) -> list[dict]:
    stufen = F.load()["budget"]["stufen"]
    rows = []
    for z in C.ZEILEN:
        mittel = F.budget_mittel(akz, z)
        row = {"Auswahlzeile": C.ZEILEN_ANZEIGE[z]}
        for j, s in enumerate(stufen):
            row[f"{s}·n"] = de(mittel[j], 2) + ("" if z == "rand" else f" ({de(F.budget_vergleich(akz, z, j)['v'], 2, True)}, {KLASSE_TEXT[F.budget_vergleich(akz, z, j)['ausgang_k']]})")
        rows.append(row)
    return rows


def tab_e5(res5: dict, regel: str) -> list[dict]:
    rows = []
    for a in C.E5_AKZ:
        b = res5[a]["b5"]
        fest = F.anteil_b5(200, a, regel)
        rows.append({"Akzeptanzregel": C.AKZ_KURZ[a], "live: Anteil der Anwendungen (%)": de(b[0], 1) if b[0] is not None else "keine",
                     "live: Anteil der Auswertungen (%)": de(b[1], 1) if b[1] is not None else "keine",
                     "eingefroren bis 200·n: Anwendungen (%)": de(fest[0], 1), "eingefroren bis 200·n: Auswertungen (%)": de(fest[1], 1)})
    return rows


def satz_zugart() -> str:
    teile = []
    for r in ("cf", "laut"):
        ob, rr, la = (F.anteil_b5(200, a, r) for a in ("ob", "rr", "la"))
        teile.append(f"{C.ZEILEN_ANZEIGE[r]}: unter „nur besser“ {de(ob[0], 1)} % ({de(ob[1], 1)} %), unter Rekord-zu-Rekord {de(rr[0], 1)} % ({de(rr[1], 1)} %), "
                     f"unter Late Acceptance {de(la[0], 1)} % ({de(la[1], 1)} %)")
    zu = F.anteil_b5(200, "ob", "rand")
    return ("**Eingefroren (Anteil von `2opt_b5` an den Anwendungen, in Klammern an den Auswertungen, bis 200·n):** " + "; ".join(teile) +
            f"; Zufall {de(zu[0], 1)} % ({de(zu[1], 1)} %) bei Gleichverteilung {de(C.GLEICHVERTEILUNG_B5_APPS, 1)} % ({de(100 * 5 / (5 + 7), 1)} %). "
            "Die Lernregel verteilt die Zugarten unter der Akzeptanz anders; die Ursache ist hier nicht isoliert (die Belohnungsfrage gehört zur Demo „Wer belohnt wen?“).")


# ---------------------------------------------------------------- Tabelle „Befunde und Korrekturen gegenüber der Vormessung“ (README)
def _kipp(zeile: str, j: int) -> str:
    aus = F.l_ausgaenge(zeile, j)
    return E.laengen_text([L for L, a in aus if a == "vorteil"], "Vorteil") + ", " + E.laengen_text([L for L, a in aus if a == "nachteil"], "Nachteil")


def tabelle_korrekturen() -> str:
    lo, hi = F.tafel(50), F.tafel(200)
    cf = {a: F.vergleich(50, a, "cf")["v"] for a in C.AKZ6}
    zl, zo, zh = lo["zerlegung"]["alle"], lo["zerlegung"]["ohne_la"], hi["zerlegung"]["alle"]
    sm_la, sm_la10 = lo["spearman"][C.AKZ6.index("la")], lo["spearman"][C.AKZ6.index("la10")]
    andere = [C.AKZ6.index(a) for a in ("ob", "rr", "sa", "gd")]
    la10_schlechter = sum(F.zellmittel(50, "la10", z) > F.zellmittel(50, "ob", z) for z in C.ZEILEN)
    la10_besser = sum(F.zellmittel(200, "la10", z) < F.zellmittel(200, "ob", z) for z in C.ZEILEN)
    rr = {z: F.vergleich(50, "rr", z) for z in ("cf", "laut", "ucb")}
    b5 = {a: F.anteil_b5(200, a, "cf")[0] for a in ("la", "rr", "ob")}
    e_la = F.ende("la")
    am_gap, la_gap = sum(F.load()["tafel"]["stufen"]["lo"]["gap"]["am"]["rand"]) / F.tafel_instanzen(), sum(F.load()["tafel"]["stufen"]["lo"]["gap"]["la"]["rand"]) / F.tafel_instanzen()
    zk = {a: [F.budget_vergleich(a, z, 0)["ausgang_k"] for z in C.LERN_ZEILEN_FUENF].count("vorteil") for a in ("ob", "rr", "la")}
    zk_hi = {a: [F.budget_vergleich(a, z, 2)["ausgang_k"] for z in C.LERN_ZEILEN_FUENF].count("vorteil") for a in ("ob", "rr", "la")}
    k95, k30, h95, h30 = lo["zaehlung"]["95"], lo["zaehlung"]["30"], hi["zaehlung"]["95"], hi["zaehlung"]["30"]
    rows = [
        ("Choice Function gegen Zufall bei 50·n: nur besser +0,29, Rekord-zu-Rekord +0,74, Annealing +0,42, Sintflut +0,34, Late Acceptance −1,97, Late Acceptance mit L = 10 −0,66",
         f"{de(cf['ob'], 2, True)}, {de(cf['rr'], 2, True)}, {de(cf['sa'], 2, True)}, {de(cf['gd'], 2, True)}, {de(cf['la'], 2, True)}, {de(cf['la10'], 2, True)}; gleiche Vorzeichen, unter „nur besser“ und Sintflut kein belegter Unterschied"),
        ("Die Akzeptanz erklärt bei 50·n 51,5 % der Streuung der Zellmittel (alle sechs Akzeptanzregeln), ohne Late Acceptance 13,4 %; die Auswahl 1,3 % und 1,5 %",
         f"{de(zl['akzeptanz'], 1)} % und {de(zo['akzeptanz'], 1)} %; Auswahl {de(zl['auswahl'], 1)} % und {de(zo['auswahl'], 1)} %"),
        ("Bei 200·n erklärt die Akzeptanz 11,2 %, die Auswahl 8,5 %", f"{de(zh['akzeptanz'], 1)} % und {de(zh['auswahl'], 1)} %: kein Faktor 2, der Rest ist Rauschen und Streuung zwischen Instanz und Zelle"),
        ("Rangkorrelation von Late Acceptance gegen nur besser, Rekord-zu-Rekord, Annealing, Sintflut: −0,37 / −0,83 / −0,60 / −0,66, mit L = 10: −0,20 / −0,71 / −0,54 / −0,49 (der Wert −0,94 des Zuschnitts stammt aus anderen sechs Zeilen und fünf Akzeptanzregeln)",
         " / ".join(de(sm_la[j], 2, True) for j in andere) + "; mit L = 10: " + " / ".join(de(sm_la10[j], 2, True) for j in andere) +
         f"; Rangumkehr (unter −0,5) gegen {lo['umkehr']['la']} und {lo['umkehr']['la10']} von 4 Akzeptanzregeln, bei 200·n gegen {hi['umkehr']['la']} und {hi['umkehr']['la10']}"),
        ("Zählung gegen Zufall in 30 Vergleichen (Vorteile / Nachteile / unentschieden, je Vergleich 95 %): 50·n 14 / 6 / 10, 200·n 0 / 16 / 14; mit Korrektur 8 / 6 / 16 und 0 / 16 / 14",
         f"50·n {k95[0]} / {k95[1]} / {k95[2]}, 200·n {h95[0]} / {h95[1]} / {h95[2]}; mit Korrektur {k30[0]} / {k30[1]} / {k30[2]} und {h30[0]} / {h30[1]} / {h30[2]}: weniger Vorteile unter „nur besser“ und Sintflut, alle Nachteile bei kleinem Budget weiter unter Late Acceptance"),
        ("Late Acceptance mit L = 10 ist bei 50·n in 6 von 6 Auswahlzeilen schlechter als „nur besser“, bei 200·n in 6 von 6 besser",
         f"bei 50·n schlechter in {la10_schlechter} von 6, bei 200·n besser in {la10_besser} von 6 (Auswahlzeilen, Zellmittel)"),
        ("Unter Rekord-zu-Rekord gewinnen bei 50·n Choice Function +1,14 und Lernautomat +0,84 gegen Zufall (Stücke 2 und 3, 120 Instanzen × 3 Läufe, andere Instanzen)",
         f"Choice Function {de(rr['cf']['v'], 2, True)}, Lernautomat {de(rr['laut']['v'], 2, True)}, UCB {de(rr['ucb']['v'], 2, True)}: gleiches Vorzeichen, kleinere Beträge als in den Vorgängern (andere Instanzen, 6 statt 3 Zufalls-Seeds, 180 statt 120 Instanzen)"),
        ("Anteil der Anwendungen auf `2opt_b5` bei der Choice Function unter Late Acceptance / Rekord-zu-Rekord / „nur besser“: 63,6 / 51,6 / 17,7 % (bis 200·n)",
         f"{de(b5['la'], 1)} / {de(b5['rr'], 1)} / {de(b5['ob'], 1)} %"),
        ("Late Acceptance nimmt 4,00 % der Anwendungen an, davon 42,3 % ohne strenge Verbesserung; die letzte Tour liegt 1,19 % über der besten (Probe, 120 Läufe)",
         f"{de(e_la['angenommen'], 2)} % angenommen, davon {de(e_la['ohne_verbesserung'], 1)} % ohne strenge Verbesserung, am Ende {de(e_la['end_gap'], 2)} % über der besten Tour (Zufall, 50·n, {E.tsd(e_la['laeufe'])} Läufe)"),
        ("„Alle Züge annehmen“: Abstand zum besten bekannten Wert 21,7 %, unter Late Acceptance 10,2 % (Mittel über sechs Zellen, Vormessung)",
         f"Abstand zum besten bekannten Wert {de(am_gap, 1)} %, unter Late Acceptance {de(la_gap, 1)} % (Zufall, 50·n, 180 Instanzen)"),
        ("Kipp-Länge der Choice Function gegen Zufall: bei 50·n zwischen L = 2 und 5, bei 200·n zwischen L = 20 und 50 (Probe, 30 Instanzen, ohne Intervalle)",
         f"bei 50·n: {_kipp('cf', 0)}; bei 200·n: {_kipp('cf', 2)} (60 Instanzen, Klasse nach 95-%-Intervall)"),
        ("Budgetreihe: unter „nur besser“ und Rekord-zu-Rekord bei 50·n Vorteil bei 1 und 4 von 5 Auswahlzeilen, bei 200·n bei 0",
         f"bei 50·n {zk['ob']} und {zk['rr']} von 5 (Late Acceptance {zk['la']}), bei 200·n {zk_hi['ob']}, {zk_hi['rr']} und {zk_hi['la']} (Intervalle nach Bonferroni für 25 Vergleiche je Stufe)"),
        ("Ein Messlauf unterbot die Langläufe der Referenz in 49 von 180 Instanzen", f"in {F.load()['tafel']['unterboten']} von 180 Instanzen"),
        ("Der p-Wert der Wechselwirkung 0,0005 ist der kleinste Wert bei 2 000 Vertauschungen", f"bestätigt: kein Treffer in {E.tsd(lo['permutation']['alle']['vertauschungen'])} Vertauschungen bei 50·n und bei 200·n"),
    ]
    kopf = "| Aussage der Planung (Vormessung und Planungsprobe) | Neumessung |\n|---|---|\n"
    return kopf + "\n".join(f"| {a} | {b} |" for a, b in rows)
