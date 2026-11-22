"""Schreibt die Sätze mit Messzahlen in die README (zwischen den Marken MESSUNG:START und MESSUNG:ENDE), aus derselben Quelle wie die App.

Aufruf (aus dem Demo-Ordner):  python tools/aka_readme.py            schreibt den Block neu
                               python tools/aka_readme.py --check    prüft nur (Rückgabe 1 bei Abweichung)
Nach jeder neuen Messung (tools/aka_make_frozen.py) aufrufen; tests/test_claims.py prüft dasselbe."""

import sys
from pathlib import Path

ORDNER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ORDNER))

import aka_saetze as SZ  # noqa: E402
import aka_texts as T  # noqa: E402

START, ENDE = "<!-- MESSUNG:START -->", "<!-- MESSUNG:ENDE -->"
A_START, A_ENDE = "<!-- ANNAHMEN:START -->", "<!-- ANNAHMEN:ENDE -->"
K_START, K_ENDE = "<!-- KORREKTUREN:START -->", "<!-- KORREKTUREN:ENDE -->"


def block() -> str:
    teile = [
        ("Kernfrage 1: Schlägt dieselbe Auswahlregel Zufall, wenn die Akzeptanzregel wechselt?", SZ.satz_hook()),
        ("Kernfrage 0: Annahme und Wanderung", SZ.satz_wanderung()),
        ("Kernfrage 2: Wie viel der Streuung erklärt die Akzeptanz?", SZ.satz_zerlegung()),
        ("Kernfrage 2: Spannweiten", SZ.satz_spannweite(50) + " " + SZ.satz_spannweite(200)),
        ("Kernfrage 3: Bei welcher Listenlänge kippt die Auswahl?", SZ.satz_l()),
        ("Kernfrage 5: Was lernt die Auswahl unter welcher Akzeptanz?", SZ.satz_zugart()),
    ]
    return "\n\n".join(f"**{frage}** {text}" for frage, text in teile)


def _ersetze(readme: str, start: str, ende: str, inhalt: str) -> str:
    a, b = readme.index(start) + len(start), readme.index(ende)
    return readme[:a] + "\n" + inhalt.strip("\n") + "\n" + readme[b:]


def einsetzen(readme: str) -> str:
    """Messblock, Tabelle der Korrekturen und Annahmen (derselbe Text wie im Abschnitt der App) einsetzen."""
    r = _ersetze(readme, START, ENDE, block())
    r = _ersetze(r, K_START, K_ENDE, SZ.tabelle_korrekturen())
    return _ersetze(r, A_START, A_ENDE, T.ASSUMPTIONS_MARKDOWN)


def main() -> int:
    pfad = ORDNER / "README.md"
    alt = pfad.read_text(encoding="utf-8")
    neu = einsetzen(alt)
    if "--check" in sys.argv:
        print("README-Block stimmt" if alt == neu else "README-Block weicht ab: python tools/aka_readme.py")
        return 0 if alt == neu else 1
    pfad.write_text(neu, encoding="utf-8", newline="\n")
    print("README-Block geschrieben")
    return 0


if __name__ == "__main__":
    sys.exit(main())
