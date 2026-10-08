"""Kniffel with switchable house rules: exact optimal strategy, simulation, advisor.

Generalises kniffel_engine.py (same tables and scoring) by jokers:
  NJ jokers per game (Paul's rule: 2). After the third roll a joker can be used to
    - "Neustart":    ignore the whole roll and play the turn again (3 new rolls), or
    - "Einzelwurf":  roll one single die once more.
  Several jokers may be used in the same turn. Both kinds can be switched on/off.

State = (filled fields as bit mask, upper sum 0..63, Kniffel-50 flag, jokers left).
Without jokers the result is identical to kniffel_engine.py (288.90 with bonus 37).

    from kniffel_regeln import Regeln, loese
    R = Regeln(bonus=37, joker=2, neustart=True, einzelwurf=True)
    S = loese(R)                       # value table, cached as .npy
    S.erwartung()                      # expected score of a whole game
    S.simuliere(100_000)               # scores (+ joker usage)
"""

import math
import os
import time
from dataclasses import dataclass

import numpy as np
from numba import njit, prange

import kniffel_engine as E

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = E.FIELDS


@dataclass(frozen=True)
class Regeln:
    bonus: int = 37            # upper bonus at >= 63 (Paul: 37, standard: 35)
    joker: int = 0             # jokers per game (Paul with friend: 2)
    neustart: bool = True      # joker kind: ignore roll, play turn again
    einzelwurf: bool = True    # joker kind: roll one die once more
    kniffel_extra: int = 50    # extra Kniffel after a 50 in the Kniffel field

    def name(self):
        if self.joker == 0:
            return f"bonus{self.bonus}"
        kinds = ("N" if self.neustart else "") + ("E" if self.einzelwurf else "")
        return f"bonus{self.bonus}_joker{self.joker}{kinds}_x{self.kniffel_extra}"


# ----------------------------------------------------------------------------- tables

def tables():
    T = E.build_tables()
    # keep index of "roll r without one die of value v" (for the single-die joker)
    rm = -np.ones((252, 6), dtype=np.int64)
    for r, c in enumerate(T["roll_counts"]):
        for v in range(6):
            if c[v] > 0:
                cc = list(c)
                cc[v] -= 1
                rm[r, v] = T["keep_index"][tuple(cc)]
    T["rm_keep"] = rm
    return T


@njit(cache=True)
def sidx(mask, u, k, j, nj):
    return (((mask * 64 + u) * 2 + k) * (nj + 1)) + j


@njit(cache=True)
def field_best(mask, u, k, j, nj, V, scores, bonus, extra_pts, out_val, out_field):
    extra_on = k == 1 and (mask >> 13) & 1 == 1
    for r in range(252):
        best = -1e18
        bf = -1
        extra = extra_pts if (extra_on and scores[r, 13] == 50) else 0.0
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
            val = sc + b + extra + V[sidx(mask | (1 << f), nu, nk, j, nj)]
            if val > best:
                best = val
                bf = f
        out_val[r] = best
        out_field[r] = bf


@njit(cache=True)
def keep_values(after, t_start, t_roll, t_prob, out):
    for ki in range(462):
        s = 0.0
        for t in range(t_start[ki], t_start[ki + 1]):
            s += t_prob[t] * after[t_roll[t]]
        out[ki] = s


@njit(cache=True)
def best_keeps(Kv, roll_keeps, roll_nkeeps, out, out_keep):
    for r in range(252):
        best = -1e18
        bk = -1
        for jj in range(roll_nkeeps[r]):
            ki = roll_keeps[r, jj]
            if Kv[ki] > best:
                best = Kv[ki]
                bk = ki
        out[r] = best
        out_keep[r] = bk


@njit(cache=True)
def turn_all(mask, u, k, nj, V, scores, bonus, extra_pts, restart_on, single_on,
             t_start, t_roll, t_prob, roll_keeps, roll_nkeeps, rm_keep,
             A3, F3, OPT3, KK1, KK2, TV):
    """Full turn tables for all joker counts j = 0..nj of state (mask, u, k).
    A3[j, r]: value after the third roll (incl. joker options), F3: best field,
    OPT3: 0 = write, 1 = restart, 2..7 = reroll a die of value 1..6,
    KK1/KK2: best keeps after roll 1/2, TV[j]: value at turn start."""
    fv = np.empty(252)
    ff = np.empty(252, dtype=np.int64)
    K = np.empty(462)
    a2 = np.empty(252)
    a1 = np.empty(252)
    for j in range(nj + 1):
        field_best(mask, u, k, j, nj, V, scores, bonus, extra_pts, fv, ff)
        for r in range(252):
            A3[j, r] = fv[r]
            F3[j, r] = ff[r]
            OPT3[j, r] = 0
        if j > 0:
            for r in range(252):
                if restart_on and TV[j - 1] > A3[j, r]:
                    A3[j, r] = TV[j - 1]
                    OPT3[j, r] = 1
                if single_on:
                    for v in range(6):
                        ki = rm_keep[r, v]
                        if ki < 0:
                            continue
                        s = 0.0
                        for t in range(t_start[ki], t_start[ki + 1]):
                            s += t_prob[t] * A3[j - 1, t_roll[t]]
                        if s > A3[j, r]:
                            A3[j, r] = s
                            OPT3[j, r] = 2 + v
        keep_values(A3[j], t_start, t_roll, t_prob, K)
        best_keeps(K, roll_keeps, roll_nkeeps, a2, KK2[j])
        keep_values(a2, t_start, t_roll, t_prob, K)
        best_keeps(K, roll_keeps, roll_nkeeps, a1, KK1[j])
        s = 0.0
        for t in range(t_start[0], t_start[1]):
            s += t_prob[t] * a1[t_roll[t]]
        TV[j] = s


@njit(parallel=True, cache=True)
def solve_level(masks, nj, V, scores, bonus, extra_pts, restart_on, single_on,
                t_start, t_roll, t_prob, roll_keeps, roll_nkeeps, rm_keep):
    for i in prange(len(masks)):
        mask = masks[i]
        A3 = np.empty((nj + 1, 252))
        F3 = np.empty((nj + 1, 252), dtype=np.int64)
        OPT3 = np.empty((nj + 1, 252), dtype=np.int64)
        KK1 = np.empty((nj + 1, 252), dtype=np.int64)
        KK2 = np.empty((nj + 1, 252), dtype=np.int64)
        TV = np.empty(nj + 1)
        for u in range(64):
            for k in range(2):
                if k == 1 and (mask >> 13) & 1 == 0:
                    continue
                turn_all(mask, u, k, nj, V, scores, bonus, extra_pts, restart_on, single_on,
                         t_start, t_roll, t_prob, roll_keeps, roll_nkeeps, rm_keep,
                         A3, F3, OPT3, KK1, KK2, TV)
                for j in range(nj + 1):
                    V[sidx(mask, u, k, j, nj)] = TV[j]


# ----------------------------------------------------------------------------- simulation

@njit(cache=True)
def sample(ki, t_start, t_roll, t_prob):
    x = np.random.random()
    acc = 0.0
    for t in range(t_start[ki], t_start[ki + 1]):
        acc += t_prob[t]
        if x < acc:
            return t_roll[t]
    return t_roll[t_start[ki + 1] - 1]


@njit(cache=True)
def play(nj, V, scores, bonus, extra_pts, restart_on, single_on,
         t_start, t_roll, t_prob, roll_keeps, roll_nkeeps, rm_keep, out):
    """One optimal game. out: [0] total, [1] restarts used, [2] single rerolls used,
    [3+f] points of field f, [18] bonus, [19] extra Kniffel points."""
    A3 = np.empty((nj + 1, 252))
    F3 = np.empty((nj + 1, 252), dtype=np.int64)
    OPT3 = np.empty((nj + 1, 252), dtype=np.int64)
    KK1 = np.empty((nj + 1, 252), dtype=np.int64)
    KK2 = np.empty((nj + 1, 252), dtype=np.int64)
    TV = np.empty(nj + 1)
    mask = 0
    u = 0
    k = 0
    j = nj
    for turn in range(15):
        turn_all(mask, u, k, nj, V, scores, bonus, extra_pts, restart_on, single_on,
                 t_start, t_roll, t_prob, roll_keeps, roll_nkeeps, rm_keep, A3, F3, OPT3, KK1, KK2, TV)
        while True:  # loop for restarts
            r = sample(0, t_start, t_roll, t_prob)
            r = sample(KK1[j, r], t_start, t_roll, t_prob)
            r = sample(KK2[j, r], t_start, t_roll, t_prob)
            while j > 0 and OPT3[j, r] >= 2:  # single-die rerolls
                ki = rm_keep[r, OPT3[j, r] - 2]
                j -= 1
                out[2] += 1
                r = sample(ki, t_start, t_roll, t_prob)
            if j > 0 and OPT3[j, r] == 1:
                j -= 1
                out[1] += 1
                continue
            break
        f = F3[j, r]
        sc = scores[r, f]
        if k == 1 and (mask >> 13) & 1 == 1 and scores[r, 13] == 50:
            out[0] += extra_pts
            out[19] += extra_pts
        out[0] += sc
        out[3 + f] = sc
        if f < 6:
            if u < 63 and u + sc >= 63:
                out[0] += bonus
                out[18] = bonus
            u = min(63, u + sc)
        if f == 13:
            k = 1 if sc == 50 else 0
        mask |= 1 << f


@njit(parallel=True, cache=True)
def simulate(n, seed, nj, V, scores, bonus, extra_pts, restart_on, single_on,
             t_start, t_roll, t_prob, roll_keeps, roll_nkeeps, rm_keep):
    out = np.zeros((n, 20))
    for i in prange(n):
        np.random.seed(seed + i)
        play(nj, V, scores, bonus, extra_pts, restart_on, single_on,
             t_start, t_roll, t_prob, roll_keeps, roll_nkeeps, rm_keep, out[i])
    return out


# ----------------------------------------------------------------------------- user API

class Loesung:
    """Solved rule set: value table plus helpers for questions."""

    def __init__(self, R, T, V):
        self.R, self.T, self.V = R, T, V
        self.nj = R.joker

    def _args(self):
        T, R = self.T, self.R
        return (float(R.bonus), float(R.kniffel_extra), R.neustart, R.einzelwurf,
                T["t_start"], T["t_roll"], T["t_prob"], T["roll_keeps"], T["roll_nkeeps"], T["rm_keep"])

    def wert(self, belegt=(), oben=0, kniffel50=False, joker=None):
        """Expected points still to come from the start of a turn in this situation."""
        j = self.nj if joker is None else joker
        mask = E.mask_of(*belegt) | ((1 << 13) if kniffel50 else 0)
        return float(self.V[sidx(mask, min(63, oben), int(kniffel50), j, self.nj)])

    def erwartung(self):
        return self.wert()

    def simuliere(self, n=100_000, seed=1):
        a = self._args()
        out = simulate(n, seed, self.nj, self.V, self.T["scores"], *a)
        return out

    def turn(self, belegt=(), oben=0, kniffel50=False, joker=None):
        nj = self.nj
        mask = E.mask_of(*belegt) | ((1 << 13) if kniffel50 else 0)
        A3 = np.empty((nj + 1, 252))
        F3 = np.empty((nj + 1, 252), dtype=np.int64)
        OPT3 = np.empty((nj + 1, 252), dtype=np.int64)
        KK1 = np.empty((nj + 1, 252), dtype=np.int64)
        KK2 = np.empty((nj + 1, 252), dtype=np.int64)
        TV = np.empty(nj + 1)
        turn_all(mask, min(63, oben), int(kniffel50), nj, self.V, self.T["scores"], *self._args(),
                 A3, F3, OPT3, KK1, KK2, TV)
        return dict(mask=mask, A3=A3, F3=F3, OPT3=OPT3, KK1=KK1, KK2=KK2, TV=TV)

    def rat(self, wurf, noch=0, belegt=(), oben=0, kniffel50=False, joker=None, top=6):
        """Advice for a roll: noch = rerolls left (2, 1) or 0 = after the third roll.
        Returns a list of (option, expected points until game end)."""
        T = self.T
        j = self.nj if joker is None else joker
        tt = self.turn(belegt, oben, kniffel50)
        r = T["roll_index"][tuple(sorted(wurf).count(v) for v in range(1, 7))]
        mask, u, k = tt["mask"], min(63, oben), int(kniffel50)
        res = []
        if noch == 0:
            sc = T["scores"][r]
            extra = self.R.kniffel_extra if (k == 1 and sc[13] == 50 and (mask >> 13) & 1) else 0
            for f in range(15):
                if (mask >> f) & 1:
                    continue
                nu, b, nk = u, 0, k
                if f < 6:
                    nu = min(63, u + sc[f])
                    b = self.R.bonus if (u < 63 and u + sc[f] >= 63) else 0
                if f == 13:
                    nk = 1 if sc[f] == 50 else 0
                res.append((f"{FIELDS[f]} ({sc[f]})",
                            sc[f] + b + extra + self.V[sidx(mask | (1 << f), nu, nk, j, self.nj)]))
            if j > 0 and self.R.neustart:
                res.append(("Joker: Neustart", tt["TV"][j - 1]))
            if j > 0 and self.R.einzelwurf:
                for v in range(6):
                    ki = T["rm_keep"][r, v]
                    if ki >= 0:
                        a, b2 = T["t_start"][ki], T["t_start"][ki + 1]
                        val = float(T["t_prob"][a:b2] @ tt["A3"][j - 1][T["t_roll"][a:b2]])
                        res.append((f"Joker: eine {v + 1} neu würfeln", val))
        else:
            K = np.empty(462)
            if noch == 1:
                keep_values(tt["A3"][j], T["t_start"], T["t_roll"], T["t_prob"], K)
            else:
                a2 = np.empty(252)
                kk = np.empty(252, dtype=np.int64)
                keep_values(tt["A3"][j], T["t_start"], T["t_roll"], T["t_prob"], K)
                best_keeps(K, T["roll_keeps"], T["roll_nkeeps"], a2, kk)
                keep_values(a2, T["t_start"], T["t_roll"], T["t_prob"], K)
            for jj in range(T["roll_nkeeps"][r]):
                ki = T["roll_keeps"][r, jj]
                res.append((f"behalten {E.keep_name(T, ki)}", K[ki]))
        res.sort(key=lambda x: -x[1])
        return [(n, float(v)) for n, v in res[:top]]


_TABLES = None


def loese(R=Regeln(), cache_dir=HERE, quiet=False):
    """Solve a rule set (or load it from cache). About 10 s without, 30-60 s with jokers."""
    global _TABLES
    if _TABLES is None:
        _TABLES = tables()
    T = _TABLES
    path = os.path.join(cache_dir, f"kniffel_V_{R.name()}.npy")
    if os.path.exists(path):
        return Loesung(R, T, np.load(path))
    nj = R.joker
    V = np.zeros(2 ** 15 * 64 * 2 * (nj + 1))
    pop = np.array([bin(m).count("1") for m in range(2 ** 15)])
    t0 = time.time()
    for level in range(14, -1, -1):
        masks = np.nonzero(pop == level)[0].astype(np.int64)
        solve_level(masks, nj, V, T["scores"], float(R.bonus), float(R.kniffel_extra), R.neustart, R.einzelwurf,
                    T["t_start"], T["t_roll"], T["t_prob"], T["roll_keeps"], T["roll_nkeeps"], T["rm_keep"])
    if not quiet:
        print(f"{R.name()}: gelöst in {time.time() - t0:.0f} s, Erwartungswert {V[sidx(0, 0, 0, nj, nj)]:.2f}")
    np.save(path, V)
    return Loesung(R, T, V)
