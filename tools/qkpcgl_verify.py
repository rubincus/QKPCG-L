"""Evaluate a QKPCG solution: objective, weight, conflicting pairs and feasibility.

The instance file follows the classic QKPCG format (Shi et al., 2017): "n |E| C"; n profits; n weights;
the upper triangle of q row by row; |E| edges with 1-based items. The solution file lists the selected
items as 1-based indices separated by blanks or new lines.

objective = sum of p_i over the selected items + sum of q_ij over the selected pairs that are not edges
(a feasible solution contains no edge, so the second term is then the sum over all selected pairs).

Usage: python qkpcgl_verify.py <instance> <solution>
Requires Python 3.9+ and NumPy.
"""
import sys
from pathlib import Path

import numpy as np


def read_instance(path):
    tok = np.array(Path(path).read_bytes().split(), dtype=np.int64)
    n, m, cap = (int(v) for v in tok[:3])
    k = 3
    p = tok[k:k + n]
    k += n
    w = tok[k:k + n]
    k += n
    nq = n * (n - 1) // 2
    q = np.zeros((n, n), dtype=np.int64)
    q[np.triu_indices(n, 1)] = tok[k:k + nq]
    k += nq
    e = tok[k:].reshape(-1, 2) - 1
    if e.shape[0] != m:
        raise ValueError(f"{e.shape[0]} edges read, {m} declared")
    return n, cap, p, w, q + q.T, e


def evaluate(instance, items):
    n, cap, p, w, q, e = read_instance(instance)
    sel = np.zeros(n, dtype=bool)
    idx = np.array(items, dtype=np.int64) - 1
    if idx.size and (idx.min() < 0 or idx.max() >= n):
        raise ValueError("item index out of range 1..n")
    if np.unique(idx).size != idx.size:
        raise ValueError("repeated item")
    sel[idx] = True
    conflicts = int((sel[e[:, 0]] & sel[e[:, 1]]).sum())
    x = sel.astype(np.int64)
    pair = (x @ q @ x) // 2 - int(q[e[:, 0], e[:, 1]][sel[e[:, 0]] & sel[e[:, 1]]].sum())
    obj = int(p @ x) + int(pair)
    weight = int(w @ x)
    return obj, weight, cap, conflicts, weight <= cap and conflicts == 0


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) != 2:
        raise SystemExit(__doc__)
    items = [int(t) for t in Path(argv[1]).read_text().split()]
    obj, weight, cap, conflicts, ok = evaluate(argv[0], items)
    print(f"items {len(items)}  objective {obj}  weight {weight}/{cap}  conflicting pairs {conflicts}  "
          f"{'FEASIBLE' if ok else 'INFEASIBLE'}")


if __name__ == "__main__":
    main()
