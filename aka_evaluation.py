"""Auswertung: Zerlegung der Streuung, Permutationstest, Rangkorrelation, Bootstrap-Intervalle, Klassen und alle Verdikte der App als reine Funktionen.

Verdikte: `verdict_*(...) -> (Art, Text)`, die App ruft `getattr(st, Art)(Text)`. Jede Zahl im Text ist ein Argument (aus einer Rechnung oder der
eingefrorenen Messung), nie von Hand im Text. Die Schwellen stehen in aka_constants und sind gesetzt, nicht abgeleitet.

Klassenregel (Quelle: Stück 1 der Linie, `hhw_stats.klasse`, hier als Kopie `aka_stats.klasse`): „klar“ ab |Unterschied| >= 0,25 Prozentpunkte mit
Intervall ohne 0; „gleich“ unter 0,10 oder mit Intervall über 0; sonst „klein“. Vorteil = klar mit positivem Unterschied (Regel besser als Zufall),
Nachteil = klar mit negativem Unterschied, alles andere unentschieden."""

import numpy as np

import aka_constants as C
import aka_stats as ST
from aka_rngblock import uniform_block


# ---------------------------------------------------------------- Format
def de(x: float, stellen: int = 2, vz: bool = False) -> str:
    """Zahl mit Dezimalkomma; vz = Vorzeichen immer zeigen (Minuszeichen als U+2212)."""
    s = f"{x:+.{stellen}f}" if vz else f"{x:.{stellen}f}"
    return s.replace(".", ",").replace("-", "−")


def tsd(n: int) -> str:
    """Ganze Zahl mit schmalen Tausendergruppen: 600000 -> '600 000' (nur die Zahl, nie ein ganzer Satz)."""
    return f"{n:,}".replace(",", " ")


def intervall(lo: float, hi: float, stellen: int = 2) -> str:
    return f"[{de(lo, stellen, True)}; {de(hi, stellen, True)}]"


# ---------------------------------------------------------------- Bootstrap, Klassen
def bootstrap_interval(werte, seed: int, ziehungen: int = C.BOOTSTRAP_ZIEHUNGEN, niveau: float = 0.95):
    """Perzentil-Intervall des Mittels über die Instanzen (Ziehungen mit Zurücklegen, SplitMix64); None bei weniger als zwei Werten.

    niveau 0,95 gibt die Perzentile 2,5 und 97,5; für m Vergleiche je Tafel `1 - 0,05 / m` (Bonferroni)."""
    x = np.asarray(list(werte), dtype=np.float64)
    m = len(x)
    if m < 2:
        return None
    idx = (uniform_block(seed, 0, ziehungen * m) * m).astype(np.int32).reshape(ziehungen, m)
    mittel = x[idx].mean(axis=1)
    a = (1.0 - niveau) / 2.0 * 100.0
    return float(np.percentile(mittel, a)), float(np.percentile(mittel, 100.0 - a))


def vergleich_gegen_zufall(zufall, regel, seed: int = C.ZWECK_BOOT, ziehungen: int = C.BOOTSTRAP_ZIEHUNGEN, vergleiche: int = 1) -> dict:
    """Unterschied je Instanz d = Abstand(Zufall) - Abstand(Regel) (positiv = Regel besser), Mittel, Intervall (korrigiert für `vergleiche`), Klasse."""
    d = [z - r for z, r in zip(zufall, regel, strict=True)]
    v = sum(d) / len(d)
    ci = bootstrap_interval(d, seed, ziehungen, 1.0 - 0.05 / vergleiche)
    if ci is None:
        return dict(v=v, lo=None, hi=None, klasse=None, ausgang="unentschieden", m=len(d))
    k = ST.klasse(v, ci[0], ci[1])
    return dict(v=v, lo=ci[0], hi=ci[1], klasse=k, ausgang=ausgang(v, k), m=len(d))


def ausgang(v: float, klasse: str | None) -> str:
    """'vorteil' (klar, Regel besser), 'nachteil' (klar, Regel schlechter) oder 'unentschieden'."""
    if klasse == "klar":
        return "vorteil" if v > 0 else "nachteil"
    return "unentschieden"


def zaehle(ausgaenge) -> tuple[int, int, int]:
    """(Vorteile, Nachteile, unentschieden)."""
    a = list(ausgaenge)
    return a.count("vorteil"), a.count("nachteil"), a.count("unentschieden")


# ---------------------------------------------------------------- Zerlegung der Streuung
def _zentriert(gap: np.ndarray) -> np.ndarray:
    """Abstand je Instanz um das Mittel der Instanz über alle Zellen zentriert (gap: Instanzen x Auswahl x Akzeptanz)."""
    return gap - gap.mean(axis=(1, 2), keepdims=True)


def _quadratsummen(y: np.ndarray) -> tuple[float, float, float, float]:
    """SS_Auswahl, SS_Akzeptanz, SS_Wechselwirkung, SS_gesamt der zentrierten Werte y (Instanzen x S x R)."""
    i, s, r = y.shape
    m = y.mean()
    ms = y.mean(axis=(0, 2))
    mr = y.mean(axis=(0, 1))
    msr = y.mean(axis=0)
    ss_a = i * r * float(((ms - m) ** 2).sum())
    ss_r = i * s * float(((mr - m) ** 2).sum())
    ss_w = i * float(((msr - ms[:, None] - mr[None, :] + m) ** 2).sum())
    return ss_a, ss_r, ss_w, float((y ** 2).sum())


def zerlege(gap) -> dict:
    """Anteile der Streuung in Prozent: Auswahl, Akzeptanz, Wechselwirkung, Rest. gap: Instanzen x Auswahlzeilen x Akzeptanzspalten."""
    y = _zentriert(np.asarray(gap, dtype=np.float64))
    ss_a, ss_r, ss_w, ss = _quadratsummen(y)
    if ss <= 0.0:
        return dict(auswahl=0.0, akzeptanz=0.0, ww=0.0, rest=0.0, ss=ss)
    return dict(auswahl=100 * ss_a / ss, akzeptanz=100 * ss_r / ss, ww=100 * ss_w / ss, rest=100 * (ss - ss_a - ss_r - ss_w) / ss, ss=ss)


def rauschanteil(gap, var, seeds: int) -> float:
    """Anteil des Rauschens der Zufalls-Seeds an der Gesamtstreuung in Prozent: Summe der Varianzen der Zellmittel (Varianz / Seeds) durch SS_gesamt."""
    y = _zentriert(np.asarray(gap, dtype=np.float64))
    ss = float((y ** 2).sum())
    return 100.0 * float(np.asarray(var, dtype=np.float64).sum()) / seeds / ss if ss > 0 else 0.0


def permutationstest(gap, vertauschungen: int = C.PERMUTATIONEN, seed: int = C.ZWECK_PERM) -> dict:
    """Permutationstest der Wechselwirkung: Reste (nach Abzug von Auswahl- und Akzeptanzeffekt) werden je Instanz unter den Zellen vertauscht.

    p = (c + 1) / (P + 1), c = Zahl der Vertauschungen mit mindestens so großer Wechselwirkungs-Quadratsumme; kleinster Wert 1 / (P + 1)."""
    y = _zentriert(np.asarray(gap, dtype=np.float64))
    i, s, r = y.shape
    m = y.mean()
    ms = y.mean(axis=(0, 2))
    mr = y.mean(axis=(0, 1))
    e = y - (m + (ms - m)[None, :, None] + (mr - m)[None, None, :])
    beobachtet = _quadratsummen(y)[2]
    e2 = e.reshape(i, s * r)
    c = 0
    block = 100
    zaehler = 0
    for _ in range(0, vertauschungen, block):
        k = min(block, vertauschungen - zaehler)
        u = uniform_block(seed, zaehler * i * s * r, k * i * s * r).reshape(k, i, s * r)
        order = np.argsort(u, axis=2)
        perm = np.take_along_axis(np.broadcast_to(e2, (k, i, s * r)), order, axis=2).reshape(k, i, s, r)
        mp = perm.mean(axis=1)                                   # k x s x r
        ww = i * ((mp - mp.mean(axis=2, keepdims=True) - mp.mean(axis=1, keepdims=True) + mp.mean(axis=(1, 2), keepdims=True)) ** 2).sum(axis=(1, 2))
        c += int((ww >= beobachtet - 1e-12).sum())
        zaehler += k
    return dict(p=(c + 1) / (vertauschungen + 1), c=c, vertauschungen=vertauschungen, beobachtet=beobachtet,
                kleinster=1.0 / (vertauschungen + 1))


# ---------------------------------------------------------------- Ränge und Rangkorrelation
def ranks(werte) -> list[float]:
    """Ränge (1 = kleinster Wert), Gleichstände bekommen den mittleren Rang."""
    w = list(werte)
    order = sorted(range(len(w)), key=lambda i: w[i])
    out = [0.0] * len(w)
    i = 0
    while i < len(w):
        j = i
        while j + 1 < len(w) and w[order[j + 1]] == w[order[i]]:
            j += 1
        mittel = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            out[order[k]] = mittel
        i = j + 1
    return out


def spearman(a, b) -> float:
    """Rangkorrelation: Pearson-Korrelation der Ränge."""
    ra, rb = np.asarray(ranks(a)), np.asarray(ranks(b))
    ra -= ra.mean()
    rb -= rb.mean()
    n = float(np.sqrt((ra ** 2).sum() * (rb ** 2).sum()))
    return float((ra * rb).sum() / n) if n > 0 else 0.0


def spearman_matrix(mittel) -> list[list[float]]:
    """mittel: Auswahlzeilen x Akzeptanzspalten (mittlerer Abstand); Ergebnis: Spalte x Spalte."""
    m = np.asarray(mittel, dtype=np.float64)
    r = m.shape[1]
    return [[spearman(m[:, a], m[:, b]) for b in range(r)] for a in range(r)]


def umkehr(matrix, spalte: int, andere) -> int:
    """Zahl der anderen Akzeptanzregeln, gegen die die Rangfolge der `spalte` mit Rangkorrelation unter -0,5 umgekehrt ist."""
    return sum(1 for j in andere if matrix[spalte][j] < C.SPEARMAN_GRENZE)


# ---------------------------------------------------------------- Kennzahlen eines Einzellaufs
def ablauf_kennzahlen(start: float, best: float, final: float, apps: int, accd: int, succ: int) -> dict:
    """Kennzahlen von Experiment 0 aus den Zählern der Suche; Nenner 0 gibt None."""
    return dict(gain=100.0 * (start - best) / start, acc_pct=100.0 * accd / apps if apps else None,
                nonimp_pct=100.0 * (accd - succ) / accd if accd else None, end_gap=100.0 * (final - best) / best)


def anteil_b5(apps, evals) -> tuple[float | None, float | None]:
    """Anteil von 2opt_b5 an den Anwendungen und den Auswertungen in Prozent (None bei Nenner 0)."""
    sa, se = sum(apps), sum(evals)
    return (100.0 * apps[C.H_2OPT_B5] / sa if sa else None, 100.0 * evals[C.H_2OPT_B5] / se if se else None)


def anteile_je_zugart(werte) -> list[float]:
    s = sum(werte)
    return [100.0 * w / s if s else 0.0 for w in werte]


# ---------------------------------------------------------------- Live-Kosten (Zählung der Auswertungen vor dem Start)
def live_cost_ablauf(n: int, faktor: int) -> int:
    return faktor * n


def live_cost_e1(n: int, faktor: int = C.E1_BUDGET, auswahl: str = "cf") -> int:
    """Auswertungen von Experiment 1: zwei Auswahlzeilen (die gewählte und Zufall) x sechs Akzeptanzregeln x Läufe x Budget; 0 bei Auswahl Zufall."""
    if auswahl == "rand":
        return 0
    laeufe = 3 * C.E1_INSTANZEN[n] * C.E1_LAEUFE
    return 2 * len(C.AKZ6) * laeufe * faktor * n


def live_cost_e5(n: int, faktor: int, regel: str = "cf") -> int:
    """Auswertungen von Experiment 5: drei Akzeptanzregeln x Läufe x Budget; 0 bei Zufall und festen Zugarten."""
    if regel not in C.LERN_REGELN_APP:
        return 0
    laeufe = 3 * C.E5_INSTANZEN[n] * C.E5_LAEUFE
    return len(C.E5_AKZ) * laeufe * faktor * n


# ---------------------------------------------------------------- Verdikte
def verdict_ablauf(best: float, gain: float, evals: int, apps: int, acc_pct, nonimp_pct, end_gap: float) -> tuple[str, str]:
    """Experiment 0: reine Faktenzeile eines Einzellaufs, keine Vergleichsaussage."""
    kopf = f"Beste Tour {de(best, 0)} ({de(gain, 1)} % unter der Startlösung nach {tsd(evals)} Auswertungen, {tsd(apps)} Anwendungen). "
    if acc_pct is None or nonimp_pct is None:
        mitte = "Keine Annahme. "
    else:
        mitte = f"{de(acc_pct, 1)} % der Anwendungen angenommen, davon {de(nonimp_pct, 1)} % ohne strenge Verbesserung. "
    return "info", kopf + mitte + f"Die letzte Tour liegt {de(end_gap, 2)} % über der besten. Einzellauf, kein Mittel."


def verdict_gegen_zufall(auswahl: str, zeilen, n_inst: int, n_laeufe: int, budget_text: str = "50·n") -> tuple[str, str]:
    """Experiment 1: dieselbe Auswahl gegen Zufall unter jeder Akzeptanzregel. zeilen: Liste von dicts mit akz (Anzeigename) und ausgang."""
    if n_inst < 2:
        return "info", "Zu wenige Instanzen für ein Intervall: Auswahl und Stichprobe vergrößern."
    v, nach, u = zaehle(z["ausgang"] for z in zeilen)
    k = len(zeilen)
    kopf = (f"{auswahl} gegen Zufall, Budget {budget_text}, {n_inst} Instanzen × {n_laeufe} Zufalls-Seeds (Intervalle nach Bonferroni für {k} Vergleiche): "
            f"Vorteil unter {v} von {k} Akzeptanzregeln, Nachteil unter {nach}, unentschieden unter {u}.")
    if nach:
        namen = ", ".join(z["akz"] for z in zeilen if z["ausgang"] == "nachteil")
        kopf += f" Nachteil unter: {namen}."
    if v:
        namen = ", ".join(z["akz"] for z in zeilen if z["ausgang"] == "vorteil")
        kopf += f" Vorteil unter: {namen}."
    art = "info"
    if nach and v:
        art = "warning"
    elif nach:
        art = "warning"
    elif v:
        art = "success"
    return art, kopf


def verdict_tafel(stufe: int, alle: dict, ohne: dict, umkehr_la: int, umkehr_la10: int, k_vorteil: int, k_nachteil: int, k_unentschieden: int) -> tuple[str, str]:
    """Experiment 2: wie viel der Streuung der Zellmittel erklärt die Akzeptanz, wie viel die Auswahl? alle / ohne: dicts mit auswahl, akzeptanz, ww, rest."""
    x, z, w, r = alle["akzeptanz"], alle["auswahl"], alle["ww"], alle["rest"]
    y = ohne["akzeptanz"]
    rang = (f"Die Rangfolge der Auswahlzeilen unter Late Acceptance kehrt sich gegenüber {umkehr_la} von 4 anderen Akzeptanzregeln um "
            f"(Late Acceptance mit L = 10: {umkehr_la10} von 4; Rangkorrelation unter −0,5)."
            if umkehr_la >= C.SPEARMAN_MINDEST else
            f"Keine Rangumkehr unter Late Acceptance ({umkehr_la} von 4; mit L = 10: {umkehr_la10} von 4).")
    zaehl = f" Gegen Zufall: {k_vorteil} Vorteile, {k_nachteil} Nachteile, {k_unentschieden} unentschieden von 30 Vergleichen."
    if x >= C.FAKTOR_AKZEPTANZ * z and y < C.ANTEIL_OHNE_LA and x - y >= C.DIFF_ANTEILE:
        return "warning", (f"Stufe {stufe}·n: Die Akzeptanzregel erklärt {de(x, 1)} % der Streuung der Zellmittel, die Auswahl {de(z, 1)} %. "
                           f"**Der große Akzeptanzanteil entsteht durch Late Acceptance:** ohne Late Acceptance (L = 50 und L = 10) sind es {de(y, 1)} %. {rang}" + zaehl)
    if x >= C.FAKTOR_AKZEPTANZ * z:
        return "info", (f"Stufe {stufe}·n: Die Akzeptanzregel erklärt {de(x, 1)} % der Streuung der Zellmittel, die Auswahl {de(z, 1)} %, auch ohne "
                        f"Late Acceptance {de(y, 1)} %. {rang}" + zaehl)
    return "info", (f"Stufe {stufe}·n: Akzeptanz {de(x, 1)} %, Auswahl {de(z, 1)} %, Wechselwirkung {de(w, 1)} %: **kein Faktor 2**. Der Rest ({de(r, 1)} %) "
                    f"ist Rauschen der Zufalls-Seeds und Streuung zwischen Instanz und Zelle. {rang}" + zaehl)


def kipp_laengen(ausgaenge_je_l) -> tuple[int | None, int | None]:
    """(L_v, L_n): größtes L <= 50 mit Vorteil, zusammenhängend ab dem kleinsten L; kleinstes L mit Nachteil. ausgaenge_je_l: Liste (L, ausgang) nach L sortiert."""
    l_v = None
    for L, a in ausgaenge_je_l:
        if L > C.LA_LEN:
            break
        if a == "vorteil":
            l_v = L
        else:
            break
    l_n = next((L for L, a in ausgaenge_je_l if a == "nachteil"), None)
    return l_v, l_n


def laengen_text(laengen, wort: str = "") -> str:
    """Listenlängen als Text hinter `wort`: eine zusammenhängende Reihe bis zum größten gemessenen L als „ab L = x“, sonst aufgezählt, leer als „bei keinem L“."""
    laengen = list(laengen)
    pre = (wort + " ") if wort else ""
    if not laengen:
        return pre + "bei keinem L"
    alle = list(C.L_WERTE)
    if laengen == alle[alle.index(laengen[0]):] and len(laengen) > 1:
        return f"{pre}ab L = {laengen[0]}"
    return f"{pre}bei L = " + ", ".join(str(x) for x in laengen)


def verdict_listenlaenge(auswahl: str, stufe: int, ausgaenge_je_l) -> tuple[str, str]:
    """Experiment 3: bei welchen Listenlängen von Late Acceptance liegt die Auswahl gegen Zufall vorn, bei welchen hinten?"""
    vor = [L for L, a in ausgaenge_je_l if a == "vorteil"]
    nach = [L for L, a in ausgaenge_je_l if a == "nachteil"]
    kopf = f"Auswahl {auswahl}, {stufe}·n: "
    ketten = "Je länger die Liste, desto weiter darf die aktuelle Tour vom Rekord abweichen; ob das die Ursache ist, ist hier nicht isoliert."
    if vor and nach:
        l_v, l_n = kipp_laengen(ausgaenge_je_l)
        if l_v is not None and l_n is not None and vor == [L for L in C.L_WERTE if L <= l_v] and l_n > l_v:
            return "warning", kopf + f"Vorteil gegen Zufall bis L = {l_v}, **Nachteil ab L = {l_n}**, dazwischen unentschieden. " + ketten
        return "warning", kopf + f"{laengen_text(vor, 'Vorteil gegen Zufall')}, **{laengen_text(nach, 'Nachteil')}**, sonst unentschieden. " + ketten
    if nach:
        return "warning", kopf + f"{laengen_text(nach, 'Nachteil gegen Zufall')}, Vorteil bei keinem L. " + ketten
    if vor:
        return "success", kopf + f"{laengen_text(vor, 'Vorteil gegen Zufall')}, Nachteil bei keinem L."
    return "info", kopf + "weder Vorteil noch Nachteil gegen Zufall bei einer der gemessenen Listenlängen."


def verdict_budget(akz: str, k_vorteil_je_stufe, k_nachteil_je_stufe) -> tuple[str, str]:
    """Experiment 4: ab welchem Budget kein Vorteil gegen Zufall mehr vorkommt. Argumente: Listen (Stufe, Zahl der Auswahlzeilen von 5)."""
    stufen = [s for s, _ in k_vorteil_je_stufe]
    k0 = k_vorteil_je_stufe[0][1]
    if all(k == 0 for _, k in k_vorteil_je_stufe):
        return "info", f"Unter {akz} bei keiner Stufe ein Vorteil gegen Zufall; Nachteil bei {k_nachteil_je_stufe[-1][1]} von 5 bei {stufen[-1]}·n."
    if all(k > 0 for _, k in k_vorteil_je_stufe):
        return "success", f"Unter {akz} ein Vorteil gegen Zufall bei jeder Stufe."
    b_stern = next((s for i, (s, k) in enumerate(k_vorteil_je_stufe) if k == 0 and all(kk == 0 for _, kk in k_vorteil_je_stufe[i:])), None)
    nach = k_nachteil_je_stufe[-1][1]
    if b_stern is not None and k0 > 0:
        return "info", (f"Unter {akz}: Vorteil gegen Zufall bei {k0} von 5 Auswahlzeilen bei {stufen[0]}·n, **ab {b_stern}·n bei keiner mehr**; "
                        f"Nachteil bei {nach} von 5 bei {stufen[-1]}·n.")
    zeile = ", ".join(f"{s}·n: {k}" for s, k in k_vorteil_je_stufe)
    return "info", f"Unter {akz}: Zahl der Auswahlzeilen mit Vorteil gegen Zufall je Stufe ({zeile}); Nachteil bei {nach} von 5 bei {stufen[-1]}·n."


def verdict_zugart(regel: str, anteil_ob, anteil_la, aus_ob, aus_la) -> tuple[str, str]:
    """Experiment 5: Anteil der Anwendungen (und Auswertungen) auf 2opt_b5 unter Late Acceptance gegen „nur besser“. Anteile in Prozent, None bei Nenner 0."""
    if None in (anteil_ob, anteil_la, aus_ob, aus_la):
        return "info", "Mindestens eine Akzeptanzregel hatte keine Anwendung: kein Anteil zu berechnen."
    gleich = C.GLEICHVERTEILUNG_B5_APPS
    if anteil_la - anteil_ob >= C.ZUGART_DIFF:
        return "warning", (f"{regel} legt unter Late Acceptance {de(anteil_la, 1)} % der Anwendungen ({de(aus_la, 1)} % der Auswertungen) auf `2opt_b5`, unter „nur besser“ "
                           f"{de(anteil_ob, 1)} % ({de(aus_ob, 1)} %); bei Gleichverteilung wären es {de(gleich, 1)} %. Ob das eine Folge der Belohnung (Kreditzuweisung) ist, "
                           "prüft Stück 3 der Reihe, hier ist es nicht isoliert.")
    return "info", (f"{regel} legt {de(anteil_ob, 1)} % der Anwendungen auf `2opt_b5` unter „nur besser“ und {de(anteil_la, 1)} % unter Late Acceptance "
                    f"(Auswertungen: {de(aus_ob, 1)} % und {de(aus_la, 1)} %); bei Gleichverteilung wären es {de(gleich, 1)} %. Die Differenz liegt unter {de(C.ZUGART_DIFF, 0)} Prozentpunkten.")
