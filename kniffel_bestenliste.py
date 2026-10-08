"""Leaderboard for heuristic weights: which weights reach which average score?

The heuristic (as in kniffel_forimport_numba.py) rates a roll per free field with
    potential = points^2 / max_points[field] * weight[field]
and uses it both for keeping dice (one roll ahead) and for choosing the field.
Weights can be one row of 15 values (same for the whole game) or a matrix with
one row per game phase, e.g. 3 rows for rounds 1-5, 6-10, 11-15.

Jokers (house rule, see kniffel_regeln.py): after the third roll the heuristic
  - rerolls one die if that raises the expected best potential by more than
    the factor (1 + einzel), and otherwise
  - restarts the turn if the best potential is below "schwelle".
Both parameters are optimised together with the weights.

All entries are evaluated with the SAME dice (common random numbers, fixed seed),
so differences between entries are real and not noise.

    python kniffel_bestenliste.py                      # show leaderboard
    python kniffel_bestenliste.py --neu "Paul 2024" --gewichte 1,1,1,1,1.05,1.1,0.4,0.8,0.9,1,0.5,0.4,1,1,0.45
    python kniffel_bestenliste.py --optimieren 1 --minuten 10            # one row, start from best entry
    python kniffel_bestenliste.py --optimieren 1 --joker 2 --minuten 10  # with 2 jokers

Reference (exact optimum, kniffel_regeln): 288.90 without jokers, 308.94 with 2 jokers (both kinds).
"""

import argparse
import csv
import datetime
import os
import time

import numpy as np
from numba import njit, prange

import kniffel_engine as E
import kniffel_regeln as KR

HERE = os.path.dirname(os.path.abspath(__file__))
LISTE = os.path.join(HERE, "kniffel_bestenliste.csv")
N_GAMES = 200_000
SEED = 2026
OPTIMUM = {0: 288.90, 1: 299.50, 2: 308.94}
COLUMNS = ["name", "mittel", "median", "streuung", "phasen", "joker", "schwelle", "einzel", "gewichte",
           "spiele", "datum", "notiz"]


@njit(cache=True)
def best_pot(scores, maxpoints, w, free, r):
    best = -1e18
    bf = -1
    for f in range(15):
        if free[f]:
            sc = scores[r, f]
            p = sc * sc / maxpoints[f] * w[f]
            if p > best:
                best = p
                bf = f
    return best, bf


@njit(cache=True)
def play(scores, bonus, maxpoints, W, nj, schwelle, einzel,
         t_start, t_roll, t_prob, roll_keeps, roll_nkeeps, rm_keep, used):
    """Heuristic game with weight matrix W (phases x 15); phase = turn * phases // 15."""
    free = np.ones(15, dtype=np.bool_)
    kniffel_fifty = False
    u = 0
    total = 0.0
    pot = np.empty(252)
    bp = np.empty(252)
    nph = W.shape[0]
    j = nj
    for turn in range(15):
        w = W[turn * nph // 15]
        for r in range(252):
            s = 0.0
            for f in range(15):
                if free[f]:
                    sc = scores[r, f]
                    s += sc * sc / maxpoints[f] * w[f]
            pot[r] = s
            bp[r] = best_pot(scores, maxpoints, w, free, r)[0]
        while True:  # restart loop
            r = E.sample_roll(0, t_start, t_roll, t_prob)
            for rr in range(2):
                best = -1e18
                bk = 0
                for jj in range(roll_nkeeps[r]):
                    ki = roll_keeps[r, jj]
                    s = 0.0
                    for t in range(t_start[ki], t_start[ki + 1]):
                        s += t_prob[t] * pot[t_roll[t]]
                    if s > best:
                        best = s
                        bk = ki
                r = E.sample_roll(bk, t_start, t_roll, t_prob)
            # jokers after the third roll
            restart = False
            while j > 0:
                cur = bp[r]
                bestk = -1
                beste = cur * (1.0 + einzel)
                for v in range(6):
                    ki = rm_keep[r, v]
                    if ki < 0:
                        continue
                    e = 0.0
                    for t in range(t_start[ki], t_start[ki + 1]):
                        e += t_prob[t] * bp[t_roll[t]]
                    if e > beste:
                        beste = e
                        bestk = ki
                if bestk >= 0:
                    j -= 1
                    used[1] += 1
                    r = E.sample_roll(bestk, t_start, t_roll, t_prob)
                    continue
                if cur < schwelle:
                    j -= 1
                    used[0] += 1
                    restart = True
                break
            if not restart:
                break
        bf = best_pot(scores, maxpoints, w, free, r)[1]
        sc = scores[r, bf]
        if bf == 13 and sc == 50 and kniffel_fifty:
            total += 50
            free[13] = False
            bf2 = best_pot(scores, maxpoints, w, free, r)[1]
            free[13] = True
            if bf2 == -1:
                continue
            bf = bf2
            sc = scores[r, bf]
        total += sc
        if bf < 6:
            if u < 63 and u + sc >= 63:
                total += bonus
            u = min(63, u + sc)
        if bf == 13 and sc == 50:
            kniffel_fifty = True
        else:
            free[bf] = False
    return total


@njit(parallel=True, cache=True)
def evaluate(n, seed, scores, bonus, maxpoints, W, nj, schwelle, einzel,
             t_start, t_roll, t_prob, roll_keeps, roll_nkeeps, rm_keep):
    out = np.empty(n)
    used = np.zeros((n, 2))
    for i in prange(n):
        np.random.seed(seed + i)
        out[i] = play(scores, bonus, maxpoints, W, nj, schwelle, einzel,
                      t_start, t_roll, t_prob, roll_keeps, roll_nkeeps, rm_keep, used[i])
    return out, used


_T = None


def tables():
    global _T
    if _T is None:
        _T = KR.tables()
    return _T


def score(T, W, n=N_GAMES, joker=0, schwelle=5.0, einzel=0.2, return_used=False):
    """Evaluate weights. T is accepted for backwards compatibility; the joker tables are used."""
    T = tables()
    W = np.atleast_2d(np.asarray(W, dtype=np.float64))
    if W.shape[1] == 1:
        W = np.repeat(W, 15, axis=1)
    s, used = evaluate(n, SEED, T["scores"], float(E.BONUS), E.MAXPOINTS, W, int(joker), float(schwelle),
                       float(einzel), T["t_start"], T["t_roll"], T["t_prob"], T["roll_keeps"],
                       T["roll_nkeeps"], T["rm_keep"])
    return (s, W, used) if return_used else (s, W)


def load():
    if not os.path.exists(LISTE):
        return []
    with open(LISTE, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter=";"))
    for r in rows:
        r.setdefault("joker", "0")
        r["joker"] = r.get("joker") or "0"
        r["schwelle"] = r.get("schwelle") or ""
        r["einzel"] = r.get("einzel") or ""
    return rows


def save_entry(name, W, s, note="", joker=0, schwelle=None, einzel=None):
    rows = load()
    rows.append(dict(name=name, mittel=f"{s.mean():.2f}", median=f"{np.median(s):.0f}", streuung=f"{s.std():.1f}",
                     phasen=str(W.shape[0]), joker=str(joker),
                     schwelle="" if not joker else f"{schwelle:.3g}", einzel="" if not joker else f"{einzel:.3g}",
                     gewichte="|".join(",".join(f"{x:.3g}" for x in row) for row in W),
                     spiele=str(len(s)), datum=datetime.date.today().isoformat(), notiz=note))
    with open(LISTE, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, COLUMNS, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def show():
    rows = load()
    print(f"Bestenliste ({N_GAMES:,} Spiele, gleiche Würfel für alle)")
    for nj in sorted({int(r["joker"]) for r in rows}):
        sub = sorted((r for r in rows if int(r["joker"]) == nj), key=lambda r: -float(r["mittel"]))
        print(f"\n{'Ohne Joker' if nj == 0 else f'Mit {nj} Joker(n)'} (optimal wären {OPTIMUM.get(nj, float('nan')):.2f}):")
        print(f" #  {'Name':30s} Mittel  Median  Phasen  Abstand zu optimal")
        for i, r in enumerate(sub, 1):
            print(f"{i:2d}  {r['name'][:30]:30s} {float(r['mittel']):6.2f}  {r['median']:>6s}  {r['phasen']:>6s}  "
                  f"{float(r['mittel']) - OPTIMUM.get(nj, np.nan):+7.2f}")


def entry(name):
    for r in load():
        if r["name"] == name:
            W = np.array([[float(x) for x in row.split(",")] for row in r["gewichte"].split("|")])
            return W, float(r["schwelle"] or 5.0), float(r["einzel"] or 0.2)
    raise SystemExit(f"Kein Eintrag {name!r}")


def weights_of(name):
    return entry(name)[0]


def optimise(phases, start, minutes, joker=0, schwelle=5.0, einzel=0.2, rng=np.random.default_rng(1)):
    """Simple (1+1) evolution: change a few parameters, keep the change if the mean improves."""
    W = np.array(start, dtype=float)
    if W.shape[0] != phases:
        W = np.repeat(W[:1], phases, axis=0)
    params = np.array([schwelle, einzel])
    best = score(None, W, n=50_000, joker=joker, schwelle=params[0], einzel=params[1])[0].mean()
    step = 0.3
    t0 = time.time()
    tries = 0
    while time.time() - t0 < minutes * 60:
        tries += 1
        cand, cp = W.copy(), params.copy()
        for _ in range(np.random.default_rng(tries).integers(1, 4)):
            if joker and rng.random() < 0.2:
                i = rng.integers(2)
                cp[i] = max(0.0, cp[i] * np.exp(rng.normal(0, step)) + (0.01 if cp[i] == 0 else 0))
            else:
                i, jj = rng.integers(phases), rng.integers(15)
                cand[i, jj] = max(0.01, cand[i, jj] * np.exp(rng.normal(0, step)))
        m = score(None, cand, n=50_000, joker=joker, schwelle=cp[0], einzel=cp[1])[0].mean()
        if m > best:
            W, params, best = cand, cp, m
            print(f"  {time.time() - t0:5.0f} s  Versuch {tries:4d}: {best:.2f}", flush=True)
        if tries % 200 == 0:
            step = max(0.05, step * 0.8)
    return W, params


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--neu", help="Name des neuen Eintrags")
    ap.add_argument("--gewichte", help="15 Werte (oder 1 Wert für alle), Phasen mit | trennen")
    ap.add_argument("--joker", type=int, default=0)
    ap.add_argument("--schwelle", type=float, default=5.0, help="Neustart, wenn bestes Potenzial darunter")
    ap.add_argument("--einzel", type=float, default=0.2, help="Einzelwurf, wenn Potenzial um diesen Anteil steigt")
    ap.add_argument("--optimieren", type=int, metavar="PHASEN", help="Gewichte suchen (1 = eine Zeile, 3 = je Spieldrittel)")
    ap.add_argument("--start", help="Startgewichte: Name eines Eintrags (Standard: bester Eintrag)")
    ap.add_argument("--minuten", type=float, default=5)
    a = ap.parse_args()

    if a.neu and a.gewichte:
        W = [[float(x) for x in row.split(",")] for row in a.gewichte.split("|")]
        s, W = score(None, W, joker=a.joker, schwelle=a.schwelle, einzel=a.einzel)
        save_entry(a.neu, W, s, joker=a.joker, schwelle=a.schwelle, einzel=a.einzel)
        print(f"{a.neu}: Mittel {s.mean():.2f}, Median {np.median(s):.0f}")
    if a.optimieren:
        rows = load()
        if a.start:
            W0, sw, ez = entry(a.start)
            start_name = a.start
        elif rows:
            start_name = max(rows, key=lambda r: float(r["mittel"]))["name"]
            W0, sw, ez = entry(start_name)
        else:
            start_name, W0, sw, ez = "Paul 2024", np.atleast_2d(E.PAUL_WEIGHTS), a.schwelle, a.einzel
        print(f"Optimiere {a.optimieren} Phase(n), {a.joker} Joker, Start: {start_name}, {a.minuten} min …")
        W, (sw, ez) = optimise(a.optimieren, W0, a.minuten, joker=a.joker, schwelle=sw, einzel=ez)
        s, W, used = score(None, W, joker=a.joker, schwelle=sw, einzel=ez, return_used=True)
        name = a.neu or f"optimiert {a.optimieren} Ph. {a.joker} J. {datetime.datetime.now():%m-%d %H:%M}"
        save_entry(name, W, s, note=f"Start: {start_name}, {a.minuten} min", joker=a.joker, schwelle=sw, einzel=ez)
        print(f"{name}: Mittel {s.mean():.2f}")
        if a.joker:
            print(f"Joker-Parameter: Schwelle {sw:.2f}, Einzel {ez:.2f}; pro Spiel Neustart {used[:, 0].mean():.2f}, "
                  f"Einzelwurf {used[:, 1].mean():.2f}")
        print("Gewichte:\n" + "\n".join("  " + " ".join(f"{x:5.2f}" for x in row) for row in W))
    show()


if __name__ == "__main__":
    main()
