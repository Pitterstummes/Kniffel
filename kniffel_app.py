"""Kniffel nach den Regeln der Toolbox-App: Joker wie in der App und Devil Deal, exakt optimal.

Gleiche Tabellen und Punkte wie kniffel_engine.py (Bonus 37, Extra-Kniffel 50). Zusaetzlich:
  Joker (NJ pro Spiel, Paul: 2), hoechstens einer pro Runde:
    - Neustart: nach jedem Wurf (ab dem 1.) den Zug verwerfen und mit 3 neuen Wuerfen nochmal spielen.
      Danach ist wieder ein Joker erlaubt (neue Runde).
    - Ein Wuerfel nochmal: nach dem 3. Wurf einen einzelnen Wuerfel ein weiteres Mal werfen.
  Devil Deal (einmal pro Spiel), nach dem 3. Wurf (auch nach "ein Wuerfel nochmal"):
    man sagt ein Zielfeld an (nicht Chance), ein gewaehlter Wuerfel wird neu geworfen, es bleiben 5 Wuerfel.
    Win  = das Zielfeld bringt danach MEHR Punkte als vorher -> Eintrag im Zielfeld.
           Ein Kniffel ist immer ein Win mit freier Wahl (mit Extra-Kniffel, wenn schon 50 drin sind),
           ausser das Kniffel-Feld ist gestrichen. Kniffel als Ziel geht auch, wenn schon 50 drin sind.
    Fail = der Teufel traegt dort ein, wo man am meisten verliert (unter den punktenden Feldern;
           gestrichen wird nur, wenn nichts punktet).

Zustand = (belegte Felder, Summe oben 0..63, Kniffel-50, Joker uebrig 0..NJ, Devil offen 0/1).
Ergebnisse wie in der App: ohne alles 288,90 · nur Devil 292,74 · 2 Joker 308,81 · beides 312,67.

    from kniffel_app import AppRegeln, loese
    S = loese(AppRegeln(joker=2, devil=True))   # ca. 1-3 min, danach aus dem Cache
    S.erwartung()
    S.rat([4, 4, 4, 4, 1], noch=0, joker=2, devil=True)
    S.simuliere(20_000).mean()
"""

import os
import time
from dataclasses import dataclass

import numpy as np
from numba import njit, prange

import kniffel_engine as E

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = E.FIELDS
NEG = -1e30
POS = 1e30


@dataclass(frozen=True)
class AppRegeln:
    joker: int = 2        # Joker pro Spiel (0..2)
    devil: bool = True    # Devil Deal einmal pro Spiel
    bonus: int = 37
    kniffel_extra: int = 50

    def name(self):
        # "devilt2" = Devil mit Zielfeld ohne Chance (alte Caches mit der frueheren Regel werden nicht mehr gelesen)
        return f"app_bonus{self.bonus}_joker{self.joker}_devil{'t2' if self.devil else 0}_x{self.kniffel_extra}"


def tables():
    T = E.build_tables()
    # Wurf r, ein Wuerfel der Augenzahl v+1 wird durch y+1 ersetzt -> neuer Wurf (-1, wenn v fehlt)
    rep = -np.ones((252, 6, 6), dtype=np.int64)
    for r, c in enumerate(T["roll_counts"]):
        for v in range(6):
            if c[v] == 0:
                continue
            for y in range(6):
                cc = list(c)
                cc[v] -= 1
                cc[y] += 1
                rep[r, v, y] = T["roll_index"][tuple(cc)]
    T["rep"] = rep
    return T


@njit(cache=True)
def sidx(mask, u, k, j, d, jn, dn):
    return ((((mask * 64 + u) * 2 + k) * jn + j) * dn) + d


@njit(cache=True)
def prepare(mask, u, k, jn, dn, V, scores, bonus, extra_pts, rep, entry, fail, devil, s3n, pts, entf, dtg):
    """Fuer (mask, u, k): bester Eintrag entry[j, d, r], Devil-Fail fail[j, r], Devil-Werte devil[j, r, v]
    (bestes Ziel dtg[j, r, v]), Eintrag in ein Feld entf[j, f, r] (ohne Devil danach),
    Wert nach dem 3. Wurf ohne weiteren Joker s3n[j, d, r], beste Punkte pts[r]."""
    extra_on = k == 1 and (mask >> 13) & 1 == 1
    for r in range(252):
        best_pts = 0
        for f in range(15):
            if (mask >> f) & 1 == 0 and scores[r, f] > best_pts:
                best_pts = scores[r, f]
        ex = extra_pts if (extra_on and scores[r, 13] == 50) else 0.0
        pts[r] = best_pts + ex
        for j in range(jn):
            fs = POS
            fa = POS
            for d in range(dn):
                best = NEG
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
                    nm = mask | (1 << f)
                    nv = 0.0 if nm == 32767 else V[sidx(nm, nu, nk, j, d, jn, dn)]
                    val = sc + b + nv
                    if val > best:
                        best = val
                    if d == 0:
                        entf[j, f, r] = val
                        if sc > 0 and val < fs:
                            fs = val
                        if val < fa:
                            fa = val
                entry[j, d, r] = best + ex
            fail[j, r] = (fs if fs < POS else fa) + ex
    for j in range(jn):
        for d in range(dn):
            for r in range(252):
                s3n[j, d, r] = entry[j, d, r]
        if dn == 2:
            free_ok = (mask >> 13) & 1 == 0 or k == 1
            for r in range(252):
                for v in range(6):
                    if rep[r, v, 0] < 0:
                        devil[j, r, v] = NEG
                        dtg[j, r, v] = -1
                        continue
                    base = 0.0
                    for y in range(6):
                        r2 = rep[r, v, y]
                        base += entry[j, 0, r2] if (free_ok and scores[r2, 13] == 50) else fail[j, r2]
                    best = base
                    bt = 13
                    for t in range(13):  # Kniffel nur ueber freie Wahl, Chance ist kein Ziel
                        if (mask >> t) & 1:
                            continue
                        s = base
                        for y in range(6):
                            r2 = rep[r, v, y]
                            if scores[r2, t] > scores[r, t] and not (free_ok and scores[r2, 13] == 50):
                                s += entf[j, t, r2] - fail[j, r2]
                        if s > best:
                            best = s
                            bt = t
                    devil[j, r, v] = best / 6.0
                    dtg[j, r, v] = bt
                    if devil[j, r, v] > s3n[j, 1, r]:
                        s3n[j, 1, r] = devil[j, r, v]


@njit(cache=True)
def keep_values(after, t_start, t_roll, t_prob, out):
    for ki in range(462):
        s = 0.0
        for t in range(t_start[ki], t_start[ki + 1]):
            s += t_prob[t] * after[t_roll[t]]
        out[ki] = s


@njit(cache=True)
def best_keeps(Kv, roll_keeps, roll_nkeeps, floor, out, out_keep):
    for r in range(252):
        best = floor
        bk = -1
        for jj in range(roll_nkeeps[r]):
            ki = roll_keeps[r, jj]
            if Kv[ki] > best:
                best = Kv[ki]
                bk = ki
        out[r] = best
        out_keep[r] = bk


@njit(cache=True)
def stages(j, d, has_restart, restart, s3n, rep, t_start, t_roll, t_prob, roll_keeps, roll_nkeeps,
           a3, opt3, k2, a2, kk2, k1, a1, kk1):
    """Ein Zug mit j Jokern und Devil d. opt3: 0 = normal (eintragen/Devil), 1 = Neustart, 2+v = Wuerfel v+1 nochmal.
    kk2/kk1 = bestes Behalten (-1 = Neustart)."""
    floor = restart if has_restart else NEG
    for r in range(252):
        best = s3n[j, d, r]
        o = 0
        if has_restart:
            if restart > best:
                best = restart
                o = 1
            for v in range(6):
                if rep[r, v, 0] < 0:
                    continue
                s = 0.0
                for y in range(6):
                    s += s3n[j - 1, d, rep[r, v, y]]
                s /= 6.0
                if s > best:
                    best = s
                    o = 2 + v
        a3[r] = best
        opt3[r] = o
    keep_values(a3, t_start, t_roll, t_prob, k2)
    best_keeps(k2, roll_keeps, roll_nkeeps, floor, a2, kk2)
    keep_values(a2, t_start, t_roll, t_prob, k1)
    best_keeps(k1, roll_keeps, roll_nkeeps, floor, a1, kk1)
    s = 0.0
    for t in range(t_start[0], t_start[1]):
        s += t_prob[t] * a1[t_roll[t]]
    return s


@njit(cache=True)
def reachable_table():
    out = np.zeros((64, 64), dtype=np.bool_)
    for um in range(64):
        cur = np.zeros(64, dtype=np.bool_)
        cur[0] = True
        for f in range(6):
            if (um >> f) & 1:
                nxt = np.zeros(64, dtype=np.bool_)
                for s in range(64):
                    if cur[s]:
                        for c in range(6):
                            nxt[min(63, s + c * (f + 1))] = True
                cur = nxt
        out[um] = cur
    return out


@njit(parallel=True, cache=True)
def solve_level(masks, jn, dn, V, scores, bonus, extra_pts, rep, reach, t_start, t_roll, t_prob, roll_keeps, roll_nkeeps):
    for i in prange(len(masks)):
        mask = masks[i]
        entry = np.empty((jn, dn, 252))
        fail = np.empty((jn, 252))
        devil = np.empty((jn, 252, 6))
        s3n = np.empty((jn, dn, 252))
        pts = np.empty(252)
        entf = np.empty((jn, 15, 252)); dtg = np.empty((jn, 252, 6), dtype=np.int64)
        a3 = np.empty(252); a2 = np.empty(252); a1 = np.empty(252)
        k2 = np.empty(462); k1 = np.empty(462)
        opt3 = np.empty(252, dtype=np.int64); kk2 = np.empty(252, dtype=np.int64); kk1 = np.empty(252, dtype=np.int64)
        for u in range(64):
            if not reach[mask & 63, u]:
                continue
            for k in range(2):
                if k == 1 and (mask >> 13) & 1 == 0:
                    continue
                prepare(mask, u, k, jn, dn, V, scores, bonus, extra_pts, rep, entry, fail, devil, s3n, pts, entf, dtg)
                for d in range(dn):
                    for j in range(jn):
                        has_r = j > 0
                        rs = V[sidx(mask, u, k, j - 1, d, jn, dn)] if has_r else 0.0
                        V[sidx(mask, u, k, j, d, jn, dn)] = stages(
                            j, d, has_r, rs, s3n, rep, t_start, t_roll, t_prob, roll_keeps, roll_nkeeps,
                            a3, opt3, k2, a2, kk2, k1, a1, kk1)


# ----------------------------------------------------------------------------- Simulation

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
def best_entry_field(mask, u, k, j, d, jn, dn, V, scores, bonus, r, worst_scoring):
    """Feld fuer Wurf r: bestes (oder fuer Devil-Fail das schlimmste punktende)."""
    bf = -1
    bv = POS if worst_scoring else NEG
    any_scoring = False
    if worst_scoring:
        for f in range(15):
            if (mask >> f) & 1 == 0 and scores[r, f] > 0:
                any_scoring = True
    for f in range(15):
        if (mask >> f) & 1:
            continue
        sc = scores[r, f]
        if worst_scoring and any_scoring and sc == 0:
            continue
        nu = u
        b = 0.0
        if f < 6:
            nu = min(63, u + sc)
            if u < 63 and u + sc >= 63:
                b = bonus
        nk = k
        if f == 13:
            nk = 1 if sc == 50 else 0
        nm = mask | (1 << f)
        val = sc + b + (0.0 if nm == 32767 else V[sidx(nm, nu, nk, j, d, jn, dn)])
        if (worst_scoring and val < bv) or (not worst_scoring and val > bv):
            bv = val
            bf = f
    return bf


@njit(cache=True)
def play(jn, dn, V, scores, bonus, extra_pts, rep, t_start, t_roll, t_prob, roll_keeps, roll_nkeeps, out):
    """Ein optimales Spiel. out: [0] Punkte, [1] Neustarts, [2] Einzelwuerfe, [3] Devil benutzt, [4] Devil Win."""
    entry = np.empty((jn, dn, 252)); fail = np.empty((jn, 252)); devil = np.empty((jn, 252, 6))
    s3n = np.empty((jn, dn, 252)); pts = np.empty(252)
    entf = np.empty((jn, 15, 252)); dtg = np.empty((jn, 252, 6), dtype=np.int64)
    a3 = np.empty(252); a2 = np.empty(252); a1 = np.empty(252); k2 = np.empty(462); k1 = np.empty(462)
    opt3 = np.empty(252, dtype=np.int64); kk2 = np.empty(252, dtype=np.int64); kk1 = np.empty(252, dtype=np.int64)
    mask = 0; u = 0; k = 0; j = jn - 1; d = dn - 1
    for turn in range(15):
        prepare(mask, u, k, jn, dn, V, scores, bonus, extra_pts, rep, entry, fail, devil, s3n, pts, entf, dtg)
        while True:  # Neustarts
            has_r = j > 0
            rs = V[sidx(mask, u, k, j - 1, d, jn, dn)] if has_r else 0.0
            stages(j, d, has_r, rs, s3n, rep, t_start, t_roll, t_prob, roll_keeps, roll_nkeeps, a3, opt3, k2, a2, kk2, k1, a1, kk1)
            r = sample(0, t_start, t_roll, t_prob)
            if kk1[r] < 0:
                j -= 1; out[1] += 1; continue
            r = sample(kk1[r], t_start, t_roll, t_prob)
            if kk2[r] < 0:
                j -= 1; out[1] += 1; continue
            r = sample(kk2[r], t_start, t_roll, t_prob)
            if opt3[r] == 1:
                j -= 1; out[1] += 1; continue
            break
        if opt3[r] >= 2:
            v = opt3[r] - 2
            r = rep[r, v, np.random.randint(6)]
            j -= 1
            out[2] += 1
        # Devil, wenn er mehr bringt als eintragen
        forced = False
        target = -1
        if d == 1:
            bv = -1
            bval = entry[j, 1, r]
            for v in range(6):
                if devil[j, r, v] > bval:
                    bval = devil[j, r, v]
                    bv = v
            if bv >= 0:
                r0 = r
                t = dtg[j, r, bv]
                r = rep[r, bv, np.random.randint(6)]
                d = 0
                out[3] += 1
                free = scores[r, 13] == 50 and ((mask >> 13) & 1 == 0 or k == 1)
                if free:
                    out[4] += 1
                elif t != 13 and scores[r, t] > scores[r0, t]:
                    out[4] += 1
                    target = t
                else:
                    forced = True
        f = target if target >= 0 else best_entry_field(mask, u, k, j, d, jn, dn, V, scores, bonus, r, forced)
        sc = scores[r, f]
        if k == 1 and (mask >> 13) & 1 == 1 and scores[r, 13] == 50:
            out[0] += extra_pts
        out[0] += sc
        if f < 6:
            if u < 63 and u + sc >= 63:
                out[0] += bonus
            u = min(63, u + sc)
        if f == 13:
            k = 1 if sc == 50 else 0
        mask |= 1 << f


@njit(parallel=True, cache=True)
def simulate(n, seed, jn, dn, V, scores, bonus, extra_pts, rep, t_start, t_roll, t_prob, roll_keeps, roll_nkeeps):
    out = np.zeros((n, 5))
    for i in prange(n):
        np.random.seed(seed + i)
        play(jn, dn, V, scores, bonus, extra_pts, rep, t_start, t_roll, t_prob, roll_keeps, roll_nkeeps, out[i])
    return out


# ----------------------------------------------------------------------------- Bedienung

class Loesung:
    def __init__(self, R, T, V):
        self.R, self.T, self.V = R, T, V
        self.jn = R.joker + 1
        self.dn = 2 if R.devil else 1

    def _idx(self, mask, u, k, j, d):
        return sidx(mask, u, k, j, d, self.jn, self.dn)

    def wert(self, belegt=(), oben=0, kniffel50=False, joker=None, devil=None):
        """Erwartete restliche Punkte zu Beginn eines Zugs."""
        j = self.R.joker if joker is None else min(joker, self.R.joker)
        d = int(self.R.devil if devil is None else (devil and self.R.devil))
        mask = E.mask_of(*belegt) | ((1 << 13) if kniffel50 else 0)
        return float(self.V[self._idx(mask, min(63, oben), int(kniffel50), j, d)])

    def erwartung(self):
        return self.wert()

    def simuliere(self, n=20_000, seed=1):
        """Gesamtpunkte von n optimalen Spielen (Spalte 0), dazu Neustarts, Einzelwuerfe, Devil, Devil-Win."""
        T, R = self.T, self.R
        return simulate(n, seed, self.jn, self.dn, self.V, T["scores"], float(R.bonus), float(R.kniffel_extra), T["rep"],
                        T["t_start"], T["t_roll"], T["t_prob"], T["roll_keeps"], T["roll_nkeeps"])

    def rat(self, wurf, noch=0, belegt=(), oben=0, kniffel50=False, joker=None, devil=None, joker_diese_runde=False, top=8):
        """Rat fuer einen Wurf: noch = verbleibende normale Wuerfe (2, 1) oder 0 nach dem 3. Wurf.
        Liste (Moeglichkeit, erwartete Punkte bis Spielende), beste zuerst."""
        T, R = self.T, self.R
        jn, dn = self.jn, self.dn
        j = R.joker if joker is None else min(joker, R.joker)
        d = int(R.devil if devil is None else (devil and R.devil))
        u = min(63, oben)
        k = int(kniffel50)
        mask = E.mask_of(*belegt) | ((1 << 13) if kniffel50 else 0)
        r = T["roll_index"][tuple(sorted(wurf).count(v) for v in range(1, 7))]
        entry = np.empty((jn, dn, 252)); fail = np.empty((jn, 252)); dv = np.empty((jn, 252, 6))
        s3n = np.empty((jn, dn, 252)); pts = np.empty(252)
        entf = np.empty((jn, 15, 252)); dtg = np.empty((jn, 252, 6), dtype=np.int64)
        prepare(mask, u, k, jn, dn, self.V, T["scores"], float(R.bonus), float(R.kniffel_extra), T["rep"], entry, fail, dv, s3n, pts,
                entf, dtg)
        a = j > 0 and not joker_diese_runde
        restart = self.V[self._idx(mask, u, k, j - 1, d)] if a else 0.0
        res = []
        if noch == 0:
            sc = T["scores"][r]
            extra = R.kniffel_extra if (k == 1 and sc[13] == 50 and (mask >> 13) & 1) else 0
            for f in range(15):
                if (mask >> f) & 1:
                    continue
                nu, b, nk = u, 0, k
                if f < 6:
                    nu = min(63, u + sc[f])
                    b = R.bonus if (u < 63 and u + sc[f] >= 63) else 0
                if f == 13:
                    nk = 1 if sc[f] == 50 else 0
                nm = mask | (1 << f)
                nv = 0.0 if nm == 32767 else self.V[self._idx(nm, nu, nk, j, d)]
                res.append((f"{FIELDS[f]} ({sc[f]})", sc[f] + b + extra + nv))
            if a:
                for v in range(6):
                    if T["rep"][r, v, 0] >= 0:
                        val = float(np.mean([s3n[j - 1, d, T["rep"][r, v, y]] for y in range(6)]))
                        res.append((f"Joker: eine {v + 1} nochmal werfen", val))
            if d == 1:
                for v in range(6):
                    if T["rep"][r, v, 0] >= 0:
                        res.append((f"Devil Deal auf eine {v + 1}, Ziel {FIELDS[dtg[j, r, v]]}", float(dv[j, r, v])))
        else:
            a3 = np.empty(252); a2 = np.empty(252); a1 = np.empty(252); k2 = np.empty(462); k1 = np.empty(462)
            o3 = np.empty(252, dtype=np.int64); kk2 = np.empty(252, dtype=np.int64); kk1 = np.empty(252, dtype=np.int64)
            stages(j, d, a, restart, s3n, T["rep"], T["t_start"], T["t_roll"], T["t_prob"], T["roll_keeps"], T["roll_nkeeps"],
                   a3, o3, k2, a2, kk2, k1, a1, kk1)
            K = k1 if noch >= 2 else k2
            for jj in range(T["roll_nkeeps"][r]):
                ki = T["roll_keeps"][r, jj]
                res.append((f"behalten {E.keep_name(T, ki)}", K[ki]))
        if a:
            res.append(("Joker: Neustart", restart))
        res.sort(key=lambda x: -x[1])
        return [(n, float(v)) for n, v in res[:top]]


_TABLES = None


def loese(R=AppRegeln(), cache_dir=HERE, quiet=False):
    """Regeln loesen (oder aus dem Cache laden, float32 .npy). Etwa 1-3 min mit Jokern und Devil."""
    global _TABLES
    if _TABLES is None:
        _TABLES = tables()
    T = _TABLES
    path = os.path.join(cache_dir, f"kniffel_V_{R.name()}.npy")
    if os.path.exists(path):
        return Loesung(R, T, np.load(path).astype(np.float64))
    jn = R.joker + 1
    dn = 2 if R.devil else 1
    V = np.zeros(2 ** 15 * 64 * 2 * jn * dn)
    pop = np.array([bin(m).count("1") for m in range(2 ** 15)])
    reach = reachable_table()
    t0 = time.time()
    for level in range(14, -1, -1):
        masks = np.nonzero(pop == level)[0].astype(np.int64)
        solve_level(masks, jn, dn, V, T["scores"], float(R.bonus), float(R.kniffel_extra), T["rep"], reach,
                    T["t_start"], T["t_roll"], T["t_prob"], T["roll_keeps"], T["roll_nkeeps"])
    S = Loesung(R, T, V)
    if not quiet:
        print(f"{R.name()}: gelöst in {time.time() - t0:.0f} s, Erwartungswert {S.erwartung():.2f}")
    np.save(path, V.astype(np.float32))
    return S


if __name__ == "__main__":
    import sys
    nj = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    dev = (sys.argv[2] != "0") if len(sys.argv) > 2 else True
    S = loese(AppRegeln(joker=nj, devil=dev))
    sim = S.simuliere(20_000)
    print(f"Simulation 20000 Spiele: Schnitt {sim[:, 0].mean():.2f}, Neustarts {sim[:, 1].mean():.2f}, "
          f"Einzelwürfe {sim[:, 2].mean():.2f}, Devil {sim[:, 3].mean():.2f} (Win {sim[:, 4].mean():.2f})")
    print(S.rat([6, 6, 5, 4, 1], noch=0))
