"""Typical field-choice mistakes of the heuristic: collect situations where the
heuristic's field differs from the optimal one, grouped by (heuristic field, optimal field).

    python kniffel_beispiele.py
"""
import collections
import os

import numpy as np

import kniffel_engine as E

CACHE = os.environ.get("KNIFFEL_CACHE", os.path.join(os.path.dirname(os.path.abspath(__file__)), "kniffel_V_bonus37.npy"))


def main(games=3000, seed=5):
    T = E.build_tables()
    V = E.solve(T, cache_file=CACHE)
    sc = T["scores"]
    rng = np.random.default_rng(seed)
    pairs = collections.defaultdict(lambda: [0, 0.0, None])
    for g in range(games):
        mask, u, k = 0, 0, 0
        for turn in range(15):
            # heuristic reroll decisions (with potentials over free fields)
            free = [f for f in range(15) if not (mask >> f) & 1]
            pot = np.array([sum(E.potential(sc[r, f], f, E.MAXPOINTS, E.PAUL_WEIGHTS) for f in free) for r in range(252)])
            r = rng.choice(252, p=T["first"])
            for _ in range(2):
                best, bk = -1, 0
                for j in range(T["roll_nkeeps"][r]):
                    ki = T["roll_keeps"][r, j]
                    a, b = T["t_start"][ki], T["t_start"][ki + 1]
                    s = float(T["t_prob"][a:b] @ pot[T["t_roll"][a:b]])
                    if s > best:
                        best, bk = s, ki
                a, b = T["t_start"][bk], T["t_start"][bk + 1]
                r = T["t_roll"][a:b][rng.choice(b - a, p=T["t_prob"][a:b] / T["t_prob"][a:b].sum())]
            dice = [v + 1 for v in range(6) for _ in range(T["roll_counts"][r][v])]
            opts = E.option_values(T, V, mask, u, k, dice)
            hf = max(free, key=lambda f: E.potential(sc[r, f], f, E.MAXPOINTS, E.PAUL_WEIGHTS))
            of = max(opts, key=lambda n: opts[n][1])
            loss = opts[of][1] - opts[E.FIELDS[hf]][1]
            if E.FIELDS[hf] != of and loss > 0.5:
                key = (E.FIELDS[hf], of)
                pairs[key][0] += 1
                pairs[key][1] += loss
                if pairs[key][2] is None or loss > pairs[key][2][0]:
                    filled = [E.FIELDS[f] for f in range(15) if (mask >> f) & 1]
                    pairs[key][2] = (loss, "".join(map(str, dice)), turn + 1, u, filled)
            # apply heuristic choice
            s = sc[r, hf]
            if hf < 6:
                u = min(63, u + s)
            if hf == 13:
                k = 1 if s == 50 else 0
            mask |= 1 << hf
    print(f"{games} Spiele mit der Heuristik. Häufigste teure Fehlentscheidungen bei der Feldwahl:")
    print(" Heuristik wählt → optimal wäre | Anzahl/Spiel | Ø Verlust | Beispiel (Wurf, Runde, oben, belegt)")
    for (h, o), (n, l, ex) in sorted(pairs.items(), key=lambda kv: -kv[1][1])[:12]:
        print(f" {h:13s} → {o:13s} | {n / games:5.2f} | {l / n:5.2f} | {ex[1]}, Runde {ex[2]}, oben {ex[3]}, belegt: {', '.join(ex[4]) or '-'}")


if __name__ == "__main__":
    main()
