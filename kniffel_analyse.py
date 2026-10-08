"""Kniffel analyses with the exact optimal strategy (kniffel_engine.py).

    python kniffel_analyse.py            # all analyses, text output (ANALYSE_ergebnisse.txt)

The value table V (about 67 MB) is computed once (some minutes) and cached.
"""

import os
import sys
import time

import numpy as np
from numba import njit, prange

import kniffel_engine as E

CACHE = os.environ.get("KNIFFEL_CACHE", os.path.join(os.path.dirname(os.path.abspath(__file__)), "kniffel_V_bonus37.npy"))


# ----------------------------------------------------------------------------- per-field statistics

@njit(cache=True)
def play_optimal_stats(V, scores, bonus, t_start, t_roll, t_prob, roll_keeps, roll_nkeeps, out):
    """Like E.play_optimal, but writes per-field points, the turn a field was filled,
    bonus and extra Kniffel points into `out` (17 + 15 entries)."""
    mask = 0
    u = 0
    k = 0
    a3 = np.empty(252)
    f3 = np.empty(252, dtype=np.int64)
    K = np.empty(462)
    a2 = np.empty(252)
    kk2 = np.empty(252, dtype=np.int64)
    a1 = np.empty(252)
    kk1 = np.empty(252, dtype=np.int64)
    for turn in range(15):
        E.field_values(mask, u, k, V, scores, bonus, a3, f3)
        E.keep_values(a3, t_start, t_roll, t_prob, K)
        E.best_over_keeps(K, roll_keeps, roll_nkeeps, a2, kk2)
        E.keep_values(a2, t_start, t_roll, t_prob, K)
        E.best_over_keeps(K, roll_keeps, roll_nkeeps, a1, kk1)
        r = E.sample_roll(0, t_start, t_roll, t_prob)
        r = E.sample_roll(kk1[r], t_start, t_roll, t_prob)
        r = E.sample_roll(kk2[r], t_start, t_roll, t_prob)
        f = f3[r]
        sc = scores[r, f]
        if k == 1 and (mask >> 13) & 1 == 1 and scores[r, 13] == 50:
            out[16] += 50
        out[f] = sc
        out[17 + f] = turn + 1
        if f < 6:
            if u < 63 and u + sc >= 63:
                out[15] = bonus
            u = min(63, u + sc)
        if f == 13:
            k = 1 if sc == 50 else 0
        mask |= 1 << f


@njit(parallel=True, cache=True)
def simulate_stats(n, seed, V, scores, bonus, t_start, t_roll, t_prob, roll_keeps, roll_nkeeps):
    out = np.zeros((n, 32))
    for i in prange(n):
        np.random.seed(seed + i)
        play_optimal_stats(V, scores, bonus, t_start, t_roll, t_prob, roll_keeps, roll_nkeeps, out[i])
    return out


# ----------------------------------------------------------------------------- heuristic vs optimal

@njit(cache=True)
def heuristic_regret(V, scores, bonus, maxpoints, weights, t_start, t_roll, t_prob, roll_keeps,
                     roll_nkeeps, field_loss, field_count, keep_loss):
    """Play Paul's heuristic; at each decision measure how much expected score it loses
    compared with the optimal decision in the same situation (rest of game optimal).
    field_loss[f]/field_count[f]: loss when the heuristic chose field f.
    Returns the final score."""
    mask = 0
    u = 0
    k = 0
    total = 0.0
    pot = np.empty(252)
    a3 = np.empty(252)
    f3 = np.empty(252, dtype=np.int64)
    K2 = np.empty(462)
    a2 = np.empty(252)
    kk2 = np.empty(252, dtype=np.int64)
    K1 = np.empty(462)
    for turn in range(15):
        # optimal values for this turn
        E.field_values(mask, u, k, V, scores, bonus, a3, f3)
        E.keep_values(a3, t_start, t_roll, t_prob, K2)
        E.best_over_keeps(K2, roll_keeps, roll_nkeeps, a2, kk2)
        E.keep_values(a2, t_start, t_roll, t_prob, K1)
        for r in range(252):
            s = 0.0
            for f in range(15):
                if not (mask >> f) & 1 or (f == 13 and k == 1):
                    s += E.potential(scores[r, f], f, maxpoints, weights)
            pot[r] = s
        r = E.sample_roll(0, t_start, t_roll, t_prob)
        for rr in range(2):
            Kopt = K1 if rr == 0 else K2
            best = -1.0
            bk = 0
            bestopt = -1e18
            for j in range(roll_nkeeps[r]):
                ki = roll_keeps[r, j]
                s = 0.0
                for t in range(t_start[ki], t_start[ki + 1]):
                    s += t_prob[t] * pot[t_roll[t]]
                if s > best:
                    best = s
                    bk = ki
                if Kopt[ki] > bestopt:
                    bestopt = Kopt[ki]
            keep_loss[0] += bestopt - Kopt[bk]
            keep_loss[1] += 1
            r = E.sample_roll(bk, t_start, t_roll, t_prob)
        # field choice of the heuristic (Kniffel field selectable while k == 1)
        best = -1.0
        bf = -1
        for f in range(15):
            if not (mask >> f) & 1 or (f == 13 and k == 1):
                p = E.potential(scores[r, f], f, maxpoints, weights)
                if p > best:
                    best = p
                    bf = f
        extra = 0.0
        if bf == 13 and k == 1:
            if scores[r, 13] == 50:
                extra = 50.0
            # heuristic: +50, then write elsewhere; with 0 the Kniffel field is crossed out (already 50)
            best = -1.0
            bf2 = -1
            for f in range(15):
                if not (mask >> f) & 1 and f != 13:
                    p = E.potential(scores[r, f], f, maxpoints, weights)
                    if p > best:
                        best = p
                        bf2 = f
            if extra == 0.0:
                # the original writes 0 into the already filled Kniffel field: a lost turn.
                # From here on the game has more fields than turns, V no longer applies -> stop measuring.
                keep_loss[2] += 1
                break
            bf = bf2
            if bf == -1:
                total += extra
                continue
        sc = scores[r, bf]
        nu = u
        b = 0.0
        if bf < 6:
            nu = min(63, u + sc)
            if u < 63 and u + sc >= 63:
                b = bonus
        nk = k
        if bf == 13:
            nk = 1 if sc == 50 else 0
        chosen = sc + b + extra + V[E.sidx(mask | (1 << bf), nu, nk)]
        field_loss[bf] += a3[r] - chosen
        field_count[bf] += 1
        total += sc + b + extra
        mask |= 1 << bf
        u = nu
        k = nk
    return total


@njit(parallel=False, cache=True)
def simulate_regret(n, seed, V, scores, bonus, maxpoints, weights, t_start, t_roll, t_prob,
                    roll_keeps, roll_nkeeps):
    field_loss = np.zeros(15)
    field_count = np.zeros(15)
    keep_loss = np.zeros(3)
    totals = np.empty(n)
    for i in range(n):
        np.random.seed(seed + i)
        totals[i] = heuristic_regret(V, scores, bonus, maxpoints, weights, t_start, t_roll, t_prob,
                                     roll_keeps, roll_nkeeps, field_loss, field_count, keep_loss)
    return totals, field_loss, field_count, keep_loss


# ----------------------------------------------------------------------------- helpers

def roll_idx(T, dice):
    return T["roll_index"][tuple(sorted(dice).count(v) for v in range(1, 7))]


def prob_in_one_turn(T, field):
    """Probability to get a scoring roll for `field` within one turn when playing only for it."""
    a3 = (T["scores"][:, field] > 0).astype(float)
    K = np.empty(462)
    E.keep_values(a3, T["t_start"], T["t_roll"], T["t_prob"], K)
    a2 = np.empty(252)
    kk = np.empty(252, dtype=np.int64)
    E.best_over_keeps(K, T["roll_keeps"], T["roll_nkeeps"], a2, kk)
    E.keep_values(a2, T["t_start"], T["t_roll"], T["t_prob"], K)
    a1 = np.empty(252)
    E.best_over_keeps(K, T["roll_keeps"], T["roll_nkeeps"], a1, kk)
    return float(T["first"] @ a1)


def print_options(T, V, mask, u, k, dice, title, top=6, out=print):
    opts = E.option_values(T, V, mask, u, k, dice)
    best = max(v[1] for v in opts.values())
    out(f"\n{title}")
    out(f"  Wurf {''.join(map(str, sorted(dice)))}: Feld (Punkte jetzt) → erwartete Gesamtpunkte ab jetzt, Abstand zum besten")
    for name, (pts, val) in sorted(opts.items(), key=lambda kv: -kv[1][1])[:top]:
        out(f"    {name:14s} ({pts:2d})  {val:7.2f}   {val - best:+6.2f}")


def print_keeps(T, V, mask, u, k, dice, rerolls_left, title, top=6, out=print):
    tt = E.turn_tables(T, V, mask, u, k)
    Kv = tt["K1"] if rerolls_left == 2 else tt["K2"]
    r = roll_idx(T, dice)
    keeps = [T["roll_keeps"][r, j] for j in range(T["roll_nkeeps"][r])]
    best = max(Kv[ki] for ki in keeps)
    out(f"\n{title}")
    out(f"  Wurf {''.join(map(str, sorted(dice)))}, noch {rerolls_left} Würfe: behalten → erwartete Punkte, Abstand")
    for ki in sorted(keeps, key=lambda x: -Kv[x])[:top]:
        out(f"    {E.keep_name(T, ki):12s} {Kv[ki]:7.2f}   {Kv[ki] - best:+6.2f}")


# ----------------------------------------------------------------------------- main

def main():
    lines = []

    def out(s=""):
        print(s)
        lines.append(s)

    T = E.build_tables()
    V = E.solve(T, cache_file=CACHE)
    args = (T["t_start"], T["t_roll"], T["t_prob"], T["roll_keeps"], T["roll_nkeeps"])
    sc, bonus = T["scores"], float(E.BONUS)

    out("KNIFFEL-ANALYSE (Regeln wie in kniffel_forimport_numba.py, Bonus 37)")
    out("=" * 70)
    out(f"\nErwartungswert bei optimaler Strategie (exakt): {V[E.sidx(0, 0, 0)]:.2f} Punkte")

    n = 200_000
    E.simulate_optimal(10, 1, V, sc, bonus, *args)
    t = time.time()
    so = E.simulate_optimal(n, 7, V, sc, bonus, *args)
    dt_o = time.time() - t
    sh = E.simulate_heuristic(n, 7, sc, bonus, E.MAXPOINTS, E.PAUL_WEIGHTS, *args)
    t = time.time()
    sh = E.simulate_heuristic(n, 7, sc, bonus, E.MAXPOINTS, E.PAUL_WEIGHTS, *args)
    dt_h = time.time() - t
    out(f"\nSimulation {n:,} Spiele:")
    out(f"  optimal:            Mittel {so.mean():6.2f}  Median {np.median(so):5.0f}  Streuung {so.std():5.1f}  "
        f"5 %/95 %: {np.percentile(so, 5):.0f}/{np.percentile(so, 95):.0f}  ({n / dt_o:,.0f} Spiele/s)")
    out(f"  Heuristik (Paul):   Mittel {sh.mean():6.2f}  Median {np.median(sh):5.0f}  Streuung {sh.std():5.1f}  "
        f"5 %/95 %: {np.percentile(sh, 5):.0f}/{np.percentile(sh, 95):.0f}  ({n / dt_h:,.0f} Spiele/s)")

    st = simulate_stats(n, 11, V, sc, bonus, *args)
    out("\nOptimale Strategie: Durchschnitt je Feld, wie oft gestrichen (0 Punkte), in welcher Runde gefüllt")
    for f in range(15):
        pts = st[:, f]
        out(f"  {E.FIELDS[f]:14s} {pts.mean():6.2f} P.   gestrichen {np.mean(pts == 0):6.1%}   Runde Ø {st[:, 17 + f].mean():4.1f}")
    out(f"  {'Bonus':14s} {st[:, 15].mean():6.2f} P.   erreicht   {np.mean(st[:, 15] > 0):6.1%}")
    out(f"  {'Extra-Kniffel':14s} {st[:, 16].mean():6.2f} P.")

    out("\nWahrscheinlichkeit in EINER Runde (3 Würfe, nur auf dieses Feld gespielt):")
    for f in [10, 11, 12, 13, 9, 8]:
        out(f"  {E.FIELDS[f]:14s} {prob_in_one_turn(T, f):6.1%}")

    out("\n" + "=" * 70)
    out("FULL HOUSE FRÜH EINTRAGEN?")
    allfree = 0
    print_options(T, V, allfree, 0, 0, [3, 3, 3, 2, 2], "1) Spielbeginn, letzter Wurf 22333", out=out)
    print_options(T, V, allfree, 0, 0, [6, 6, 6, 5, 5], "2) Spielbeginn, letzter Wurf 55666", out=out)
    print_options(T, V, allfree, 0, 0, [1, 1, 1, 2, 2], "3) Spielbeginn, letzter Wurf 11122", out=out)
    print_keeps(T, V, allfree, 0, 0, [3, 3, 3, 2, 2], 2, "4) Spielbeginn, ERSTER Wurf 22333 (noch 2 Würfe)", out=out)
    print_keeps(T, V, allfree, 0, 0, [6, 6, 6, 5, 5], 2, "5) Spielbeginn, ERSTER Wurf 55666 (noch 2 Würfe)", out=out)
    print_keeps(T, V, allfree, 0, 0, [6, 6, 6, 5, 5], 1, "6) Spielbeginn, ZWEITER Wurf 55666 (noch 1 Wurf)", out=out)
    # mid game: upper part mostly done
    mid = E.mask_of("Einser", "Zweier", "Dreier", "Vierer", "Ein Paar", "Zwei Paare", "Chance")
    print_options(T, V, mid, 40, 0, [3, 3, 3, 2, 2],
                  "7) Spielmitte (Einser–Vierer, Paare, Chance belegt; oben 40), letzter Wurf 22333", out=out)
    late = (1 << 15) - 1 - E.mask_of("Full House", "Dreierpasch", "Dreier")
    print_options(T, V, late, 50, 0, [3, 3, 3, 2, 2],
                  "8) Spielende: offen nur Dreier, Dreierpasch, Full House (oben 50), Wurf 22333", out=out)
    out("\nWert eines offenen Full House am Spielbeginn: V(alles frei) − V(nur Full House belegt) = "
        f"{V[E.sidx(0, 0, 0)] - V[E.sidx(E.mask_of('Full House'), 0, 0)]:.2f} Punkte "
        "(so viel bringt das Feld im Schnitt noch, wenn man es offen lässt)")

    out("\n" + "=" * 70)
    out("FELDAUSWAHL DER HEURISTIK (Gewichte aus simulate_numba.py) gegen optimal")
    m = 20_000
    tot, fl, fc, kl = simulate_regret(m, 3, V, sc, bonus, E.MAXPOINTS, E.PAUL_WEIGHTS, *args)
    out(f"  {m:,} Spiele mit der Heuristik, nach jeder Entscheidung bewertet:")
    out(f"  Verlust durch Würfel-Behalten: {kl[0] / m:5.2f} Punkte pro Spiel ({kl[0] / kl[1]:.3f} je Entscheidung)")
    out(f"  Verlust durch Feldwahl:        {fl.sum() / m:5.2f} Punkte pro Spiel")
    out(f"  Verschenkte Runden (0 ins schon volle Kniffel-Feld): {kl[2] / m:.3f} pro Spiel (danach nicht weiter bewertet)")
    out("  Feldwahl je Feld (wie oft gewählt pro Spiel, Ø Verlust wenn gewählt):")
    for f in np.argsort(-fl):
        if fc[f] > 0:
            out(f"    {E.FIELDS[f]:14s} {fc[f] / m:5.2f}×  Ø Verlust {fl[f] / fc[f]:5.2f}  → {fl[f] / m:5.2f} P./Spiel")

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ANALYSE_ergebnisse.txt")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\nGespeichert:", path)


if __name__ == "__main__":
    main()
