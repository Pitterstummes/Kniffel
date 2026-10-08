"""Kniffel engine: fast tables, exact optimal strategy, heuristic from kniffel_forimport_numba.

Rules as in Paul's code (kniffel_forimport_numba.py):
  0-5  Ones..Sixes (sum of that number)      upper bonus BONUS (37) at >= 63
  6    One pair      (highest pair x 2)
  7    Two pairs     (two different pairs, sum x 2)
  8    Three of a kind (value x 3)
  9    Four of a kind  (value x 4)
  10   Full house    30 (exactly 3 + 2, five equal does not count)
  11   Small straight 25 (four in a row)
  12   Big straight   40
  13   Kniffel        50
  14   Chance         sum
  Extra Kniffel after a scored 50: +50 and the roll is written to another free field.

Everything is built on precomputed tables:
  252 sorted rolls, 462 "keeps" (kept dice as a multiset), sparse transition
  probabilities keep -> roll, the score table roll x field, and for each roll
  the list of keeps that are possible from it.

The optimal strategy is computed by dynamic programming over all states
(filled fields as bit mask, upper sum 0..63, Kniffel-50 flag): 2^15 * 64 * 2
states, each solved exactly for the three rolls of a turn.
"""

import math
import os
import time
from itertools import combinations_with_replacement

import numpy as np
from numba import njit, prange

FIELDS = ["Einser", "Zweier", "Dreier", "Vierer", "Fünfer", "Sechser", "Ein Paar", "Zwei Paare",
          "Dreierpasch", "Viererpasch", "Full House", "Kleine Straße", "Große Straße", "Kniffel", "Chance"]
NF = 15
BONUS = 37
BONUS_LIMIT = 63
KNIFFEL_EXTRA = 50
MAXPOINTS = np.array([5, 10, 15, 20, 25, 30, 12, 22, 18, 24, 30, 25, 40, 50, 30], dtype=np.float64)
PAUL_WEIGHTS = np.array([1, 1, 1, 1, 1.05, 1.1, 0.4, 0.8, 0.9, 1, 0.5, 0.4, 1, 1, 0.45])  # simulate_numba.py


# ----------------------------------------------------------------------------- tables

def score_counts(c):
    """Score of a roll (given as counts of 1..6) in every field."""
    s = np.zeros(NF, dtype=np.int64)
    total = sum((i + 1) * c[i] for i in range(6))
    for i in range(6):
        s[i] = (i + 1) * c[i]
    pairs = [i + 1 for i in range(6) if c[i] >= 2]
    s[6] = 2 * max(pairs) if pairs else 0
    s[7] = 2 * sum(pairs) if len(pairs) >= 2 else 0
    s[8] = next((3 * (i + 1) for i in range(6) if c[i] >= 3), 0)
    s[9] = next((4 * (i + 1) for i in range(6) if c[i] >= 4), 0)
    s[10] = 30 if (3 in c and 2 in c) else 0
    present = [c[i] > 0 for i in range(6)]
    s[11] = 25 if any(all(present[j:j + 4]) for j in range(3)) else 0
    s[12] = 40 if (all(present[0:5]) or all(present[1:6])) else 0
    s[13] = 50 if 5 in c else 0
    s[14] = total
    return s


def build_tables():
    rolls = [tuple(r) for r in combinations_with_replacement(range(1, 7), 5)]
    roll_counts = np.array([[r.count(v) for v in range(1, 7)] for r in rolls], dtype=np.int64)
    roll_index = {tuple(c): i for i, c in enumerate(roll_counts)}
    keeps = []
    for m in range(6):
        for k in combinations_with_replacement(range(1, 7), m):
            keeps.append(tuple(k.count(v) for v in range(1, 7)))
    keep_index = {k: i for i, k in enumerate(keeps)}
    keep_counts = np.array(keeps, dtype=np.int64)

    # sparse keep -> roll transitions
    t_start = np.zeros(len(keeps) + 1, dtype=np.int64)
    t_roll, t_prob = [], []
    for ki, k in enumerate(keeps):
        n = 5 - sum(k)
        for add in combinations_with_replacement(range(1, 7), n):
            ac = [add.count(v) for v in range(1, 7)]
            perms = math.factorial(n)
            for a in ac:
                perms //= math.factorial(a)
            r = tuple(k[i] + ac[i] for i in range(6))
            t_roll.append(roll_index[r])
            t_prob.append(perms / 6 ** n)
        t_start[ki + 1] = len(t_roll)

    # keeps possible from each roll (unique sub-multisets)
    roll_keeps = -np.ones((len(rolls), 32), dtype=np.int64)
    roll_nkeeps = np.zeros(len(rolls), dtype=np.int64)
    for ri, c in enumerate(roll_counts):
        subs = set()
        for a in range(c[0] + 1):
            for b in range(c[1] + 1):
                for d in range(c[2] + 1):
                    for e in range(c[3] + 1):
                        for f in range(c[4] + 1):
                            for g in range(c[5] + 1):
                                subs.add(keep_index[(a, b, d, e, f, g)])
        subs = sorted(subs)
        roll_keeps[ri, :len(subs)] = subs
        roll_nkeeps[ri] = len(subs)

    scores = np.array([score_counts(list(c)) for c in roll_counts], dtype=np.int64)
    first = np.zeros(len(rolls))  # probability of each roll from scratch
    for j in range(t_start[0], t_start[1]):
        first[t_roll[j]] += t_prob[j]
    return dict(rolls=rolls, roll_counts=roll_counts, roll_index=roll_index, keep_counts=keep_counts,
                keep_index=keep_index, t_start=t_start, t_roll=np.array(t_roll, dtype=np.int64),
                t_prob=np.array(t_prob), roll_keeps=roll_keeps, roll_nkeeps=roll_nkeeps,
                scores=scores, first=first)


# ----------------------------------------------------------------------------- optimal strategy

@njit(cache=True)
def sidx(mask, u, k):
    return (mask * 64 + u) * 2 + k


@njit(cache=True)
def field_values(mask, u, k, V, scores, bonus, out_best, out_field):
    """For every final roll: best value (points now + expected rest) and the field."""
    extra_on = k == 1 and (mask >> 13) & 1 == 1
    for r in range(252):
        best = -1e18
        bf = -1
        extra = 0.0
        if extra_on and scores[r, 13] == 50:
            extra = 50.0
        for f in range(15):
            if (mask >> f) & 1:
                continue
            sc = scores[r, f]
            nu = u
            b = 0.0
            if f < 6:
                nu = min(63, u + sc)
                if u < 63 and u + sc >= 63:
                    b = bonus
            nk = k
            if f == 13:
                nk = 1 if sc == 50 else 0
            val = sc + b + extra + V[sidx(mask | (1 << f), nu, nk)]
            if val > best:
                best = val
                bf = f
        out_best[r] = best
        out_field[r] = bf


@njit(cache=True)
def keep_values(after, t_start, t_roll, t_prob, out):
    for ki in range(462):
        s = 0.0
        for j in range(t_start[ki], t_start[ki + 1]):
            s += t_prob[j] * after[t_roll[j]]
        out[ki] = s


@njit(cache=True)
def best_over_keeps(Kv, roll_keeps, roll_nkeeps, out, out_keep):
    for r in range(252):
        best = -1e18
        bk = -1
        for j in range(roll_nkeeps[r]):
            ki = roll_keeps[r, j]
            if Kv[ki] > best:
                best = Kv[ki]
                bk = ki
        out[r] = best
        out_keep[r] = bk


@njit(cache=True)
def turn_value(mask, u, k, V, scores, bonus, t_start, t_roll, t_prob, roll_keeps, roll_nkeeps):
    a3 = np.empty(252)
    f3 = np.empty(252, dtype=np.int64)
    field_values(mask, u, k, V, scores, bonus, a3, f3)
    K = np.empty(462)
    keep_values(a3, t_start, t_roll, t_prob, K)
    a2 = np.empty(252)
    kk = np.empty(252, dtype=np.int64)
    best_over_keeps(K, roll_keeps, roll_nkeeps, a2, kk)
    keep_values(a2, t_start, t_roll, t_prob, K)
    a1 = np.empty(252)
    best_over_keeps(K, roll_keeps, roll_nkeeps, a1, kk)
    s = 0.0
    for j in range(t_start[0], t_start[1]):
        s += t_prob[j] * a1[t_roll[j]]
    return s


@njit(parallel=True, cache=True)
def solve_level(masks, V, scores, bonus, t_start, t_roll, t_prob, roll_keeps, roll_nkeeps):
    for i in prange(len(masks)):
        mask = masks[i]
        for u in range(64):
            for k in range(2):
                if k == 1 and (mask >> 13) & 1 == 0:
                    continue
                V[sidx(mask, u, k)] = turn_value(mask, u, k, V, scores, bonus, t_start, t_roll,
                                                 t_prob, roll_keeps, roll_nkeeps)


def solve(T, bonus=BONUS, cache_file=None):
    """Value table V[state] = expected points still to come under optimal play."""
    if cache_file and os.path.exists(cache_file):
        return np.load(cache_file)
    V = np.zeros(2 ** NF * 64 * 2)
    pop = np.array([bin(m).count("1") for m in range(2 ** NF)])
    t0 = time.time()
    for level in range(NF - 1, -1, -1):
        masks = np.nonzero(pop == level)[0].astype(np.int64)
        solve_level(masks, V, T["scores"], float(bonus), T["t_start"], T["t_roll"], T["t_prob"],
                    T["roll_keeps"], T["roll_nkeeps"])
        print(f"  Ebene {level:2d} ({len(masks):5d} Feldkombinationen) fertig, {time.time() - t0:.0f} s")
    if cache_file:
        np.save(cache_file, V)
    return V


# ----------------------------------------------------------------------------- playing

@njit(cache=True)
def sample_roll(keep_ki, t_start, t_roll, t_prob):
    x = np.random.random()
    acc = 0.0
    last = t_start[keep_ki + 1] - 1
    for j in range(t_start[keep_ki], t_start[keep_ki + 1]):
        acc += t_prob[j]
        if x < acc:
            return t_roll[j]
    return t_roll[last]


@njit(cache=True)
def play_optimal(V, scores, bonus, t_start, t_roll, t_prob, roll_keeps, roll_nkeeps):
    mask = 0
    u = 0
    k = 0
    total = 0.0
    a3 = np.empty(252)
    f3 = np.empty(252, dtype=np.int64)
    K = np.empty(462)
    a2 = np.empty(252)
    kk2 = np.empty(252, dtype=np.int64)
    a1 = np.empty(252)
    kk1 = np.empty(252, dtype=np.int64)
    for turn in range(15):
        field_values(mask, u, k, V, scores, bonus, a3, f3)
        keep_values(a3, t_start, t_roll, t_prob, K)
        best_over_keeps(K, roll_keeps, roll_nkeeps, a2, kk2)
        keep_values(a2, t_start, t_roll, t_prob, K)
        best_over_keeps(K, roll_keeps, roll_nkeeps, a1, kk1)
        r = sample_roll(0, t_start, t_roll, t_prob)
        r = sample_roll(kk1[r], t_start, t_roll, t_prob)
        r = sample_roll(kk2[r], t_start, t_roll, t_prob)
        f = f3[r]
        sc = scores[r, f]
        if k == 1 and (mask >> 13) & 1 == 1 and scores[r, 13] == 50:
            total += 50
        total += sc
        if f < 6:
            if u < 63 and u + sc >= 63:
                total += bonus
            u = min(63, u + sc)
        if f == 13:
            k = 1 if sc == 50 else 0
        mask |= 1 << f
        if mask == (1 << 15) - 1:
            break
    return total


@njit(parallel=True, cache=True)
def simulate_optimal(n, seed, V, scores, bonus, t_start, t_roll, t_prob, roll_keeps, roll_nkeeps):
    out = np.empty(n)
    for i in prange(n):
        np.random.seed(seed + i)
        out[i] = play_optimal(V, scores, bonus, t_start, t_roll, t_prob, roll_keeps, roll_nkeeps)
    return out


# Paul's heuristic (same decisions as kniffel_forimport_numba.py, but with tables)

@njit(cache=True)
def potential(sc, f, maxpoints, weights):
    return sc * sc / maxpoints[f] * weights[f]


@njit(cache=True)
def play_heuristic(scores, bonus, maxpoints, weights, t_start, t_roll, t_prob, roll_keeps, roll_nkeeps):
    """Reroll: keep that maximises the expected sum of 'potential' over all free fields
    after ONE more roll (as in collect_decision_parameters). Field: highest potential."""
    free = np.ones(15, dtype=np.bool_)
    kniffel_fifty = False
    u = 0
    total = 0.0
    pot = np.empty(252)
    for turn in range(15):
        for r in range(252):
            s = 0.0
            for f in range(15):
                if free[f]:
                    s += potential(scores[r, f], f, maxpoints, weights)
            pot[r] = s
        r = sample_roll(0, t_start, t_roll, t_prob)
        for rr in range(2):
            best = -1.0
            bk = 0
            for j in range(roll_nkeeps[r]):
                ki = roll_keeps[r, j]
                s = 0.0
                for t in range(t_start[ki], t_start[ki + 1]):
                    s += t_prob[t] * pot[t_roll[t]]
                if s > best:
                    best = s
                    bk = ki
            r = sample_roll(bk, t_start, t_roll, t_prob)
        # choose field (the Kniffel field stays selectable after a 50, like the original)
        best = -1.0
        bf = -1
        for f in range(15):
            if free[f]:
                p = potential(scores[r, f], f, maxpoints, weights)
                if p > best:
                    best = p
                    bf = f
        sc = scores[r, bf]
        if bf == 13 and sc == 50 and kniffel_fifty:
            total += 50  # extra Kniffel: +50 and write the roll to another field
            best = -1.0
            bf = -1
            for f in range(15):
                if free[f] and f != 13:
                    p = potential(scores[r, f], f, maxpoints, weights)
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
            kniffel_fifty = True  # field stays free for further Kniffel bonuses
        else:
            free[bf] = False
    return total


@njit(parallel=True, cache=True)
def simulate_heuristic(n, seed, scores, bonus, maxpoints, weights, t_start, t_roll, t_prob,
                       roll_keeps, roll_nkeeps):
    out = np.empty(n)
    for i in prange(n):
        np.random.seed(seed + i)
        out[i] = play_heuristic(scores, bonus, maxpoints, weights, t_start, t_roll, t_prob,
                                roll_keeps, roll_nkeeps)
    return out


# ----------------------------------------------------------------------------- analysis helpers

def turn_tables(T, V, mask, u, k, bonus=BONUS):
    """All intermediate values of one turn (for 'what should I do here' questions)."""
    a3 = np.empty(252)
    f3 = np.empty(252, dtype=np.int64)
    field_values(mask, u, k, V, T["scores"], float(bonus), a3, f3)
    K2 = np.empty(462)
    keep_values(a3, T["t_start"], T["t_roll"], T["t_prob"], K2)
    a2 = np.empty(252)
    kk2 = np.empty(252, dtype=np.int64)
    best_over_keeps(K2, T["roll_keeps"], T["roll_nkeeps"], a2, kk2)
    K1 = np.empty(462)
    keep_values(a2, T["t_start"], T["t_roll"], T["t_prob"], K1)
    return dict(a3=a3, f3=f3, K2=K2, K1=K1)


def option_values(T, V, mask, u, k, roll, bonus=BONUS):
    """Value of writing `roll` (tuple of 5 dice) into each free field: points + expected rest."""
    r = T["roll_index"][tuple(sorted(roll).count(v) for v in range(1, 7))]
    sc = T["scores"][r]
    res = {}
    for f in range(NF):
        if (mask >> f) & 1:
            continue
        nu, b, nk = u, 0, k
        if f < 6:
            nu = min(63, u + sc[f])
            b = bonus if (u < 63 and u + sc[f] >= 63) else 0
        if f == 13:
            nk = 1 if sc[f] == 50 else 0
        res[FIELDS[f]] = (int(sc[f]), sc[f] + b + V[sidx(mask | (1 << f), nu, nk)])
    return res


def keep_name(T, ki):
    c = T["keep_counts"][ki]
    return "".join(str(v + 1) * c[v] for v in range(6)) or "(alles neu)"


def mask_of(*names):
    m = 0
    for n in names:
        m |= 1 << FIELDS.index(n)
    return m
