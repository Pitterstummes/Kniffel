# Kniffel: Strategie-Analyse mit exakter optimaler Strategie

Neu in diesem Ordner:

| Datei | Zweck |
|---|---|
| `kniffel_engine.py` | Engine mit Tabellen, exakter optimaler Strategie (dynamische Programmierung) und deiner Heuristik |
| `kniffel_analyse.py` | alle Auswertungen unten → `ANALYSE_ergebnisse.txt` |
| `kniffel_berater.py` | "Was soll ich hier tun?" für beliebige Spielstände |
| `kniffel_beispiele.py` | typische Fehlentscheidungen der Heuristik → `beispiele_ergebnisse.txt` |

Die Regeln sind wie in deinem Code: Ein Paar, Zwei Paare, Paschs zählen nur die Pasch-Würfel, Full House 30 (genau 3 + 2), kleine Straße 25, große Straße 40, Kniffel 50, Extra-Kniffel +50 mit Eintrag in ein anderes Feld, Bonus 37 ab 63.

## 1. Geschwindigkeit und Parallelisierung

| | Spiele pro Sekunde |
|---|---:|
| `kniffel_forimport_numba.py` (korrigiert), 1 Kern | 9 |
| deine Heuristik in der neuen Engine, alle Kerne | ca. 105.000 |
| optimale Strategie, alle Kerne | ca. 31.000 |

**Warum so viel schneller:**

1. **Tabellen statt Neuberechnung:**
   - Es gibt nur 252 verschiedene Würfe (sortiert) und 462 Möglichkeiten, Würfel zu behalten.
   - Die Punkte für jeden Wurf in jedem Feld (252 × 15) und die Wahrscheinlichkeiten "behalte X → Wurf Y" (4.368 Einträge) werden einmal berechnet.
   - Das Original berechnet bei jeder Würfelentscheidung alle 252 Endzustände mit Punkten für jedes Feld neu und erzeugt dabei viele kleine numpy-Arrays (`np.delete`, `np.argwhere`, `np.concatenate`).
2. **Parallel in numba (`prange`)** statt `multiprocess.Pool`: kein Kopieren zwischen Prozessen, keine Start-Kosten.
3. **Feste Zufalls-Seeds je Spiel:** Zwei Strategien lassen sich mit denselben Würfen vergleichen (gemeinsame Zufallszahlen). Damit sieht man auch kleine Unterschiede. Das war das Problem in `optimizer.py` ("changes in the average seem to be too noisy").

## 2. Optimale Strategie: Wie gut ist die Feldauswahl?

Die optimale Strategie wird exakt berechnet (in 10 Sekunden):

- Für jeden Spielstand (welche Felder belegt, Punkte oben 0–63, Kniffel mit 50 ja/nein, insgesamt 4,2 Millionen) steht der Erwartungswert der restlichen Punkte fest, wenn man ab dort optimal spielt.
- Daraus folgt für jede Entscheidung (welche Würfel behalten, welches Feld) die beste Wahl.

| Strategie | Mittel | Median | 5 % / 95 % |
|---|---:|---:|---|
| **optimal** (exakt 288,90) | 288,8 | 286 | 218 / 380 |
| deine Heuristik (Gewichte aus simulate_numba.py) | 253,9 | 243 | 193 / 339 |

Die Heuristik verliert also **35 Punkte pro Spiel**. Jede Entscheidung der Heuristik wurde gegen die optimale bewertet:

- **14,3 Punkte** verliert sie beim Würfel-Behalten. Sie schaut nur einen Wurf voraus und bewertet mit "Punkte² / Maximum · Gewicht".
- **20,7 Punkte** verliert sie bei der Feldwahl, am meisten bei Sechsern (7,8) und Fünfern (2,9).

**Typische teure Fehler** (aus `beispiele_ergebnisse.txt`):

| Heuristik schreibt | besser wäre | Beispiel | Ø Verlust |
|---|---|---|---:|
| 2 Sechser (12) in **Sechser** | Ein Paar | 23366 in Runde 11, oben 46 | 12,7 |
| kleine Zahl in **Fünfer/Sechser** | Einser (opfern) | 11256 in Runde 10 | 18,4 |
| **Viererpasch** mit 46666 | Sechser (24, sichert den Bonus) | Runde 10, oben 34 | 5,6 |
| kleine Zahl oben (Dreier, Einser) | **Kniffel streichen** | 44456 in Runde 14, oben 61 | 8–11 |
| **Dreierpasch** mit 33666 | Full House | Runde 9 | 3,1 |

**Was dahintersteckt:**

- Die Heuristik kennt den Bonus nicht. 37 Punkte sind viel, und die optimale Strategie holt ihn in 83,5 % der Spiele.
- Wer zwei Sechser in die Sechser schreibt, liegt 6 Punkte unter "Soll" (3 je Zahl) und gefährdet den Bonus.
- Es ist besser, ein schwaches Feld unten (Ein Paar, Kniffel) zu opfern.
- Die Gewichte (Full House 0,5, Chance 0,45, kleine Straße 0,4) machen solche Felder künstlich unattraktiv. Deshalb wird z. B. 33666 als Dreierpasch statt als Full House notiert.

## 3. Full House früh eintragen?

Ja, wenn es nach dem letzten Wurf dasteht. Mit noch offenen Würfen lohnt es sich aber oft, weiterzuspielen:

| Lage | beste Wahl | Abstand zur zweitbesten |
|---|---|---|
| Spielbeginn, **letzter** Wurf 22333 | Full House (30) | Dreier (9): −4,5 |
| Spielbeginn, letzter Wurf 55666 | Full House (30) | Zwei Paare/Dreierpasch: −2,5 |
| Spielbeginn, letzter Wurf 11122 | Full House (30) | Einser: −6,6 |
| Spielbeginn, **erster** Wurf 22333 (noch 2 Würfe) | **333 behalten**, nicht das Full House | Full House stehen lassen: −4,3 |
| Spielbeginn, erster Wurf 55666 | **666 behalten** | Full House stehen lassen: −5,4 |
| Spielbeginn, zweiter Wurf 55666 (noch 1 Wurf) | **666 behalten** | Full House stehen lassen: −3,3 |
| Spielmitte, letzter Wurf 22333 | Full House | Dreierpasch: −15,1 |

**Einordnung:**

- Ein fertiges Full House früh einzutragen ist richtig. Ein offenes Full House ist am Spielbeginn im Schnitt nur noch 30,7 Punkte wert, also kaum mehr als die 30, die man jetzt sicher hat. Später wird es oft ohnehin gestrichen oder kostet einen Wurf.
- Mit Würfen übrig lieber den Drilling behalten. Der kann noch zu Viererpasch, Kniffel, hohen Sechsern oder wieder zu einem Full House werden.
- Die Wahrscheinlichkeit, ein Full House in einer Runde zu bekommen, wenn man nur darauf spielt, liegt bei 36,3 %. Bei der optimalen Strategie wird das Full House nur in 4 % der Spiele gestrichen, im Schnitt in Runde 6.

**Weitere Wahrscheinlichkeiten für eine Runde** (nur auf das Feld gespielt):

| Feld | Wahrscheinlichkeit |
|---|---:|
| kleine Straße | 61,5 % |
| große Straße | 26,1 % |
| Viererpasch | 29,1 % |
| Dreierpasch | 74,3 % |
| Kniffel | 4,6 % |

## 4. Optimale Strategie in Zahlen (pro Feld)

| Feld | Ø Punkte | gestrichen | Ø Runde |
|---|---:|---:|---:|
| Einser–Sechser | 2,1 / 5,6 / 9,1 / 12,7 / 16,2 / 20,1 | 9 % bei Einsern, sonst ≤ 1,4 % | 6,6–8,6 |
| Bonus | 30,9 | erreicht 83,5 % | |
| Ein Paar / Zwei Paare | 10,9 / 18,6 | 0,1 % / 1,7 % | 7,9 / 7,0 |
| Dreier-/Viererpasch | 15,5 / 12,2 | 4,5 % / 34,6 % | 8,0 / 10,9 |
| Full House | 28,8 | 4,0 % | 6,2 |
| kleine / große Straße | 24,7 / 34,1 | 1,4 % / 14,8 % | 6,7 / 8,3 |
| Kniffel | 19,4 (+5,5 Extra) | 61,2 % | 10,4 |
| Chance | 22,6 | 0 % | 9,6 |

Die optimale Strategie hebt sich Chance (Runde 9,6), Kniffel und Viererpasch für das Ende auf, als Puffer zum Streichen.

## 5. Bonus 35 statt 37

Mit Standard-Bonus 35 liegt der optimale Erwartungswert bei 287,24 statt 288,90. Der Berater rechnet beides: `--bonus 35`.

## 6. Berater benutzen

```
python kniffel_berater.py --wurf 22333 --noch 2
python kniffel_berater.py --wurf 66655 --noch 0 --belegt "Full House,Einser" --oben 2
```

Ausgabe: alle Möglichkeiten mit den erwarteten Punkten bis Spielende und dem Abstand zur besten. Die Tabelle (67 MB) wird beim ersten Aufruf in 10 s berechnet und als `.npy` gespeichert.

## Ideen für später

- Den Berater als kleines Fenster (tkinter) oder Notebook mit Würfel-Buttons bauen, für echte Spielabende.
- Zwei-Spieler-Variante: Gewinnwahrscheinlichkeit maximieren statt Punkte. Kurz vor Spielende spielt man dann anders.
- Die Gewichte der Heuristik gegen die optimale Strategie fitten, um zu sehen, wie nah eine einfache Regel herankommt (mit gemeinsamen Zufallszahlen jetzt sinnvoll machbar).
