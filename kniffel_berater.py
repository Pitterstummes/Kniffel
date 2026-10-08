"""Kniffel advisor: what is the best move in a given situation (optimal strategy)?

    python kniffel_berater.py --wurf 22333 --noch 2
    python kniffel_berater.py --wurf 22333 --noch 0 --belegt "Einser,Zweier,Chance" --oben 6
    python kniffel_berater.py --wurf 66666 --noch 0 --belegt Kniffel --kniffel50

--wurf      the five dice
--noch      rerolls left in this turn (2 after the first roll, 1 after the second, 0 = write now)
--belegt    already filled fields, comma separated (names as in the score sheet, see --felder)
--oben      points already in the upper part (Einser..Sechser)
--kniffel50 the Kniffel field holds 50 (further Kniffel: +50)
--bonus     upper bonus (default 37 as in Paul's code; 35 = standard Kniffel)
"""

import argparse
import os

import kniffel_engine as E

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--wurf", help="z. B. 22333")
    p.add_argument("--noch", type=int, default=0, choices=[0, 1, 2])
    p.add_argument("--belegt", default="")
    p.add_argument("--oben", type=int, default=0)
    p.add_argument("--kniffel50", action="store_true")
    p.add_argument("--bonus", type=int, default=E.BONUS)
    p.add_argument("--top", type=int, default=6)
    p.add_argument("--felder", action="store_true", help="Feldnamen anzeigen")
    a = p.parse_args()
    if a.felder or not a.wurf:
        print("Felder:", ", ".join(E.FIELDS))
        return

    T = E.build_tables()
    cache = os.environ.get("KNIFFEL_CACHE", os.path.join(HERE, f"kniffel_V_bonus{a.bonus}.npy"))
    if not os.path.exists(cache):
        print("Berechne die optimale Strategie einmalig (ca. 10–60 s) …")
    V = E.solve(T, bonus=a.bonus, cache_file=cache)

    names = [n.strip() for n in a.belegt.split(",") if n.strip()]
    for n in names:
        if n not in E.FIELDS:
            raise SystemExit(f"Unbekanntes Feld {n!r}. Felder: {', '.join(E.FIELDS)}")
    mask = E.mask_of(*names)
    if a.kniffel50 and "Kniffel" not in names:
        mask |= 1 << E.FIELDS.index("Kniffel")
    u = min(63, a.oben)
    k = 1 if a.kniffel50 else 0
    dice = [int(c) for c in a.wurf]
    if len(dice) != 5 or not all(1 <= d <= 6 for d in dice):
        raise SystemExit("--wurf braucht genau 5 Würfel 1–6, z. B. 22333")

    print(f"Erwartete Punkte bis Spielende ab Beginn dieser Runde: {V[E.sidx(mask, u, k)]:.2f}")
    if a.noch == 0:
        opts = E.option_values(T, V, mask, u, k, dice, bonus=a.bonus)
        best = max(v[1] for v in opts.values())
        print(f"Wurf {''.join(map(str, sorted(dice)))} eintragen in … (Punkte jetzt → erwartete Punkte bis Spielende)")
        for name, (pts, val) in sorted(opts.items(), key=lambda kv: -kv[1][1])[:a.top]:
            print(f"  {name:14s} ({pts:2d})  {val:7.2f}  {val - best:+6.2f}")
    else:
        tt = E.turn_tables(T, V, mask, u, k, bonus=a.bonus)
        Kv = tt["K1"] if a.noch == 2 else tt["K2"]
        r = T["roll_index"][tuple(sorted(dice).count(v) for v in range(1, 7))]
        keeps = [T["roll_keeps"][r, j] for j in range(T["roll_nkeeps"][r])]
        best = max(Kv[ki] for ki in keeps)
        print(f"Wurf {''.join(map(str, sorted(dice)))}, noch {a.noch} Würfe – behalten … (erwartete Punkte bis Spielende)")
        for ki in sorted(keeps, key=lambda x: -Kv[x])[:a.top]:
            print(f"  {E.keep_name(T, ki):12s} {Kv[ki]:7.2f}  {Kv[ki] - best:+6.2f}")


if __name__ == "__main__":
    main()
