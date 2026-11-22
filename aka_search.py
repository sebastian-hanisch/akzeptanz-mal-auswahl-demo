"""Die Suche: in jeder Anwendung eine Zugart wählen, einen Vorschlag bewerten, über die Annahme entscheiden, Auswertungen zählen.

Eigene Fassung (keine Kopie der Suche aus hyperheuristik-demo), weil diese Demo die Akzeptanzregel zum Thema hat: gegenüber der Kopie
(`tests/quelle_search.py`, dort bitgleich geprüft) kennt sie zusätzlich
  * jede Listenlänge von Late Acceptance (`"la<L>"`, z. B. `"la1"`, `"la200"`; `"la"` = 50 und `"la10"` = 10 wie in der Kopie),
  * die Gegenprobe „alle Züge annehmen“ (`"am"`),
  * die Spur mit der Nummer der Anwendung (7. Eintrag) und Zählstände je Kontrollpunkt (`stats=True`): Anwendungen, Auswertungen, Annahmen,
    strenge Verbesserungen je Zugart und die Summe des Abstands der aktuellen zur besten Tour über alle Anwendungen.
`arms` ist die Menge der erlaubten Zugarten: alle acht für die Zufallsmischung, `(h,)` für eine feste Zugart."""

import aka_accept as AC
import aka_constants as C
from aka_moves import PROPOSE, apply_move, cost_of, propose_2opt_b5
from aka_scenario import tour_cost

_OB, _RR, _LA, _GD, _SA, _AM = 0, 1, 2, 3, 4, 5
_KIND = {"ob": _OB, "rr": _RR, "la": _LA, "gd": _GD, "sa": _SA, "am": _AM}


def parse_accept(accept: str) -> tuple[str, int]:
    """Name der Akzeptanz -> (Regel, Listenlänge). 'la<L>' mit beliebigem L >= 1; die Namen der Kopie (ob, rr, la, la10, gd, sa) und 'am'."""
    if accept == "am":
        return "am", 0
    if accept in AC.REGELN:
        return AC.REGELN[accept]
    if accept.startswith("la") and accept[2:].isdigit() and int(accept[2:]) >= 1:
        return "la", int(accept[2:])
    raise ValueError(f"unbekannte Akzeptanz {accept!r}")


def check_feasible(t, n: int) -> bool:
    """Unabhängiger Prüfer: t ist eine Permutation der Orte 0 bis n - 1."""
    return len(t) == n and sorted(t) == list(range(n))


def run_search(D, t0, budget, arms, accept, rng, checkpoints=(), trace=False, selector=None, check=False, stats=False):
    """Eine Suche mit `budget` Auswertungen ab der Starttour t0.

    arms: Tupel der erlaubten Zugarten (Indizes aus aka_constants.HNAMEN); ohne `selector` wird je Anwendung gleichverteilt daraus gewählt
        (bei einer einzigen Zugart ohne Zufallszahl).
    accept: 'ob', 'rr', 'la', 'la10', 'la<L>', 'gd', 'sa' oder 'am' (siehe parse_accept).
    rng: Zufallsstrom mit `random()`; Reihenfolge je Anwendung: Auswahl, Vorschlag, bei Annealing die Annahme (nur bei Verlängerung).
    checkpoints: Auswertungszahlen; `ck[i]` ist der Bestwert nach der ersten Anwendung, mit der die verbrauchten Auswertungen
        checkpoints[i] erreichen (2opt_b5 kann den Punkt um bis zu 4 überschreiten).
    trace: Spur der angenommenen Züge als Liste (Auswertungen danach, Zugart, Zug, delta, Länge danach, Bestwert danach, Nummer der Anwendung).
    selector: Haken für gelernte Auswahlregeln: `selector.choose(rng)` gibt den Index in `arms`,
        `selector.update(index, delta, kosten, angenommen)` wird nach jeder Anwendung gerufen.
    check: prüft nach jedem angenommenen Zug Permutation und Länge gegen die volle Neubewertung (nur Tests).
    stats: `ck_stat[i]` = (Anwendungen, apps, evals, accd, succ, wsum) am Kontrollpunkt i; wsum = Summe über alle Anwendungen von
        (aktuelle Länge - Bestwert) / Bestwert.

    Rückgabe: dict mit best, final, used, steps, apps / succ / accd / evals (je Zugart: Anwendungen, strenge Verbesserungen des Vorschlags,
    angenommene Züge, Auswertungen), ck, ck_stat, trace, best_used (Auswertungen beim letzten neuen Bestwert), wsum, tour."""
    n = len(t0)
    t = list(t0)
    cost = tour_cost(D, t)
    cost0 = cost
    best = cost
    best_used = 0
    regel, laenge = parse_accept(accept)
    ak = _KIND[regel]
    hist = AC.new_hist(cost0, laenge) if ak == _LA else None
    kante = cost0 / n
    rnd = rng.random
    na = len(arms)
    eps = C.EPS
    apps = [0] * C.K
    succ = [0] * C.K
    accd = [0] * C.K
    evals = [0] * C.K
    used = 0
    step = 0
    wsum = 0.0
    ck_list = sorted(checkpoints)
    nck = len(ck_list)
    ck_i = 0
    ck_out = []
    ck_stat = []
    spur = [] if trace else None
    pos = 0

    while used < budget:
        # Auswahl der Zugart
        if selector is not None:
            pos = selector.choose(rng)
            h = arms[pos]
        elif na == 1:
            h = arms[0]
        else:
            pos = int(rnd() * na)
            h = arms[pos]
        # Vorschlag und Zählung
        if h == 7:
            c = cost_of(7, budget - used)
            delta, mv = propose_2opt_b5(t, D, n, rng, c)
        else:
            c = 1
            delta, mv = PROPOSE[h](t, D, n, rng)
        used += c
        neu = cost + delta
        # Akzeptanz
        if ak == _OB:
            ok = AC.accept_ob(delta)
        elif ak == _RR:
            ok = AC.accept_rr(delta, neu, best)
        elif ak == _LA:
            ok = AC.accept_la(delta, neu, hist, step)
        elif ak == _GD:
            ok = AC.accept_gd(delta, neu, cost0, used, budget)
        elif ak == _AM:
            ok = True
        else:
            ok = delta <= eps or AC.accept_sa(delta, AC.sa_temperature(used, budget, kante), rnd())
        if ok:
            apply_move(t, h, mv)
            cost = neu
            accd[h] += 1
            if cost < best - 1e-12:
                best = cost
                best_used = used
            if trace:
                spur.append((used, h, mv, delta, cost, best, step + 1))
            if check:
                assert check_feasible(t, n), ("keine Permutation", h, mv)
                assert abs(tour_cost(D, t) - cost) < 1e-6, ("delta falsch", h, mv)
        if ak == _LA:
            AC.update_hist(hist, step, cost)
        step += 1
        # Statistik je Zugart
        apps[h] += 1
        evals[h] += c
        if delta < -eps:
            succ[h] += 1
        wsum += (cost - best) / best
        if selector is not None:
            selector.update(pos, delta, c, ok)
        if nck:
            while ck_i < nck and used >= ck_list[ck_i]:
                ck_out.append(best)
                if stats:
                    ck_stat.append((step, list(apps), list(evals), list(accd), list(succ), wsum))
                ck_i += 1
    while ck_i < nck:
        ck_out.append(best)
        if stats:
            ck_stat.append((step, list(apps), list(evals), list(accd), list(succ), wsum))
        ck_i += 1
    return dict(best=best, final=cost, used=used, steps=step, apps=apps, succ=succ, accd=accd, evals=evals, ck=ck_out, ck_stat=ck_stat,
                trace=spur, best_used=best_used, wsum=wsum, tour=t)
