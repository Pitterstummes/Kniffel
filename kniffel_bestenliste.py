"""Leaderboard for heuristic weights: which weights reach which average score?

The heuristic (as in kniffel_forimport_numba.py) rates a roll per free field with
    potential = points^2 / max_points[field] * weight[field]
and uses it both for keeping dice (one roll ahead) and for choosing the field.
Weights can be one row of 15 values (same for the whole game) or a matrix with
one row per game phase, e.g. 3 rows for rounds 1-5, 6-10, 11-15.

All entries are evaluated with the SAME dice (common random numbers, fixed seed),
so differences between entries are real and not noise.

    python kniffel_bestenliste.py                      # show leaderboard
    python kniffel_bestenliste.py --neu "Paul 2024" --gewichte 1,1,1,1,1.05,1.1,0.4,0.8,0.9,1,0.5,0.4,1,1,0.45
    python kniffel_bestenliste.py --neu "alle 1" --gewichte 1
    python kniffel_bestenliste.py --optimieren 3 --start "Paul 2024" --minuten 10
    python kniffel_bestenliste.py --optimieren 1 --minuten 10   # one row, start from best entry

Reference: optimal strategy (kniffel_engine.solve) = 288.90 points, upper limit for any heuristic.
"""

import argparse
import csv
import datetime
import os
import time

import numpy as np
from numba import njit, prange

import kniffel_engine as E

HERE = os.path.dirname(os.path.abspath(__file__))
LISTE = os.path.join(HERE, "kniffel_bestenliste.csv")
N_GAMES = 200_000
SEED = 2026
OPTIMUM = 288.90


@njit(cache=True)
def play(scores, bonus, maxpoints, W, t_start, t_roll, t_prob, roll_keeps, roll_nkeeps):
    """Heuristic game with weight matrix W (phases x 15); phase = turn * phases // 15."""
    free = np.ones(15, dtype=np.bool_)
    kniffel_fifty = False
    u = 0
    total = 0.0
    pot = np.empty(252)
    nph = W.shape[0]
    for turn in range(15):
        w = W[turn * nph // 15]
        for r in range(252):
            s = 0.0
            for f in range(15):
                if free[f]:
                    sc = scores[r, f]
                    s += sc * sc / maxpoints[f] * w[f]
            pot[r] = s
        r = E.sample_roll(0, t_start, t_roll, t_prob)
        for rr in range(2):
            best = -1e18
            bk = 0
            for j in range(roll_nkeeps[r]):
                ki = roll_keeps[r, j]
                s = 0.0
                for t in range(t_start[ki], t_start[ki + 1]):
                    s += t_prob[t] * pot[t_roll[t]]
                if s > best:
                    best = s
                    bk = ki
            r = E.sample_roll(bk, t_start, t_roll, t_prob)
        best = -1e18
        bf = -1
        for f in range(15):
            if free[f]:
                sc = scores[r, f]
                p = sc * sc / maxpoints[f] * w[f]
                if p > best:
                    best = p
                    bf = f
        sc = scores[r, bf]
        if bf == 13 and sc == 50 and kniffel_fifty:
            total += 50
            best = -1e18
            bf = -1
            for f in range(15):
                if free[f] and f != 13:
                    s2 = scores[r, f]
                    p = s2 * s2 / maxpoints[f] * w[f]
                    if p > best:
                        best = p
                        bf = f
            if bf == -1:
                continue
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
def evaluate(n, seed, scores, bonus, maxpoints, W, t_start, t_roll, t_prob, roll_keeps, roll_nkeeps):
    out = np.empty(n)
    for i in prange(n):
        np.random.seed(seed + i)
        out[i] = play(scores, bonus, maxpoints, W, t_start, t_roll, t_prob, roll_keeps, roll_nkeeps)
    return out


def score(T, W, n=N_GAMES):
    W = np.atleast_2d(np.asarray(W, dtype=np.float64))
    if W.shape[1] == 1:
        W = np.repeat(W, 15, axis=1)
    s = evaluate(n, SEED, T["scores"], float(E.BONUS), E.MAXPOINTS, W, T["t_start"], T["t_roll"],
                 T["t_prob"], T["roll_keeps"], T["roll_nkeeps"])
    return s, W


def load():
    if not os.path.exists(LISTE):
        return []
    with open(LISTE, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


def save_entry(name, W, s, note=""):
    rows = load()
    rows.append(dict(name=name, mittel=f"{s.mean():.2f}", median=f"{np.median(s):.0f}", streuung=f"{s.std():.1f}",
                     phasen=str(W.shape[0]), gewichte="|".join(",".join(f"{x:.3g}" for x in row) for row in W),
                     spiele=str(len(s)), datum=datetime.date.today().isoformat(), notiz=note))
    with open(LISTE, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, list(rows[-1].keys()), delimiter=";")
        w.writeheader()
        w.writerows(rows)


def show():
    rows = sorted(load(), key=lambda r: -float(r["mittel"]))
    print(f"Bestenliste ({N_GAMES:,} Spiele, gleiche Würfel für alle, optimal wären {OPTIMUM}):")
    print(f" #  {'Name':28s} Mittel  Median  Phasen  Abstand zu optimal")
    for i, r in enumerate(rows, 1):
        print(f"{i:2d}  {r['name'][:28]:28s} {float(r['mittel']):6.2f}  {r['median']:>6s}  {r['phasen']:>6s}  {float(r['mittel']) - OPTIMUM:+7.2f}")


def weights_of(name):
    for r in load():
        if r["name"] == name:
            return np.array([[float(x) for x in row.split(",")] for row in r["gewichte"].split("|")])
    raise SystemExit(f"Kein Eintrag {name!r}")


def optimise(T, phases, start, minutes, rng=np.random.default_rng(1)):
    """Simple (1+1) evolution: change a few weights, keep the change if the mean improves."""
    W = np.repeat(np.atleast_2d(start), phases, axis=0) if np.atleast_2d(start).shape[0] != phases else np.array(start)
    s, W = score(T, W, n=50_000)
    best = s.mean()
    step = 0.3
    t0 = time.time()
    tries = 0
    while time.time() - t0 < minutes * 60:
        tries += 1
        cand = W.copy()
        k = rng.integers(1, 4)
        for _ in range(k):
            i, j = rng.integers(phases), rng.integers(15)
            cand[i, j] = max(0.01, cand[i, j] * np.exp(rng.normal(0, step)))
        sc, _ = score(T, cand, n=50_000)
        if sc.mean() > best:
            W, best = cand, sc.mean()
            print(f"  {time.time() - t0:5.0f} s  Versuch {tries:4d}: {best:.2f}", flush=True)
        if tries % 200 == 0:
            step = max(0.05, step * 0.8)
    return W


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--neu", help="Name des neuen Eintrags")
    ap.add_argument("--gewichte", help="15 Werte (oder 1 Wert für alle), Phasen mit | trennen")
    ap.add_argument("--optimieren", type=int, metavar="PHASEN", help="Gewichte suchen (1 = eine Zeile, 3 = je Spieldrittel)")
    ap.add_argument("--start", help="Startgewichte: Name eines Eintrags (Standard: bester Eintrag)")
    ap.add_argument("--minuten", type=float, default=5)
    a = ap.parse_args()
    T = E.build_tables()

    if a.neu and a.gewichte:
        W = [[float(x) for x in row.split(",")] for row in a.gewichte.split("|")]
        s, W = score(T, W)
        save_entry(a.neu, W, s)
        print(f"{a.neu}: Mittel {s.mean():.2f}, Median {np.median(s):.0f}")
    if a.optimieren:
        rows = load()
        start_name = a.start or (max(rows, key=lambda r: float(r["mittel"]))["name"] if rows else None)
        start = weights_of(start_name) if start_name else E.PAUL_WEIGHTS
        print(f"Optimiere {a.optimieren} Phase(n), Start: {start_name or 'Paul 2024'}, {a.minuten} min …")
        W = optimise(T, a.optimieren, start, a.minuten)
        s, W = score(T, W)
        name = a.neu or f"optimiert {a.optimieren} Phase(n) {datetime.datetime.now():%m-%d %H:%M}"
        save_entry(name, W, s, note=f"Start: {start_name}, {a.minuten} min")
        print(f"{name}: Mittel {s.mean():.2f}")
        print("Gewichte:\n" + "\n".join("  " + " ".join(f"{x:5.2f}" for x in row) for row in W))
    show()


if __name__ == "__main__":
    main()
