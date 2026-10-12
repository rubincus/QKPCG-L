"""Regenerate the QKPCG-L instances from Set I of the DCKP.

Each QKPCG-L instance keeps n, the capacity C, the profits p, the weights w and the conflict graph of
its Set I source and adds a quadratic profit q_ij, an integer drawn uniformly from {1, ..., 50}, for
every pair i < j. The draws come from NumPy's default generator (PCG64) seeded with the value listed
in MANIFEST.csv, so the output does not depend on which copy of Set I is used (the GitHub copy ends
lines with CRLF, the Mendeley Data copy with LF; their contents are identical). The seeds were derived
once as the first eight bytes (little endian) of SHA-256("<sha256 of source file>:1.0:1:50"), with the
source file taken from the CRLF copy.

Output format (as in the classic QKPCG set of Shi et al., 2017): "n |E| C", a blank line, the profits
and the weights in lines of ten values (each block followed by a blank line), the upper triangle of q
row by row (row i holds q_i,i+1 ... q_i,n-1), and the edges "a b" with 1-based items, a < b, sorted.

Usage: python qkpcgl_generate.py <set_I_folder> <output_folder> [--manifest MANIFEST.csv] [--check]
Requires Python 3.9+ and NumPy.
"""
import argparse
import csv
import hashlib
from pathlib import Path

import numpy as np


def read_dckp(path):
    tok = np.array(Path(path).read_bytes().split(), dtype=np.int64)
    n, m, cap = (int(v) for v in tok[:3])
    p, w = tok[3:3 + n], tok[3 + n:3 + 2 * n]
    e = tok[3 + 2 * n:].reshape(-1, 2) - 1
    if e.shape[0] != m:
        raise ValueError(f"{path}: {e.shape[0]} edges read, {m} declared")
    a, b = np.minimum(e[:, 0], e[:, 1]), np.maximum(e[:, 0], e[:, 1])
    key = np.unique(a * n + b)
    return n, cap, p, w, np.stack([key // n, key % n], axis=1)


def write_instance(out, n, cap, p, w, edges, seed, qlo=1, qhi=50):
    rng = np.random.default_rng(seed)
    q = rng.integers(qlo, qhi + 1, size=n * (n - 1) // 2, dtype=np.int64)
    with open(out, "w", newline="\n") as fh:
        fh.write(f"{n} {edges.shape[0]} {cap}\n\n")
        for vec in (p, w):
            for k in range(0, n, 10):
                fh.write(" ".join(map(str, vec[k:k + 10].tolist())) + " \n")
            fh.write("\n")
        pos = 0
        for i in range(n - 1):
            row = q[pos:pos + n - 1 - i]
            pos += n - 1 - i
            fh.write(" ".join(map(str, row.tolist())) + " \n")
        for a, b in (edges + 1).tolist():
            fh.write(f"{a} {b}\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("set_i", type=Path, help="folder with the Set I files (searched recursively)")
    ap.add_argument("output", type=Path)
    ap.add_argument("--manifest", type=Path, default=Path(__file__).resolve().parents[1] / "MANIFEST.csv")
    ap.add_argument("--check", action="store_true", help="compare the SHA-256 of each file with the manifest")
    a = ap.parse_args(argv)
    a.output.mkdir(parents=True, exist_ok=True)
    sources = {f.stem: f for f in a.set_i.rglob("*") if f.is_file()}
    bad = 0
    for row in csv.DictReader(open(a.manifest)):
        src = Path(row["source"]).stem
        n, cap, p, w, edges = read_dckp(sources[src])
        out = a.output / row["instance"]
        write_instance(out, n, cap, p, w, edges, int(row["seed"]), int(row["q_min"]), int(row["q_max"]))
        digest = hashlib.sha256(out.read_bytes()).hexdigest()
        ok = digest == row["sha256"]
        bad += not ok
        print(f"{row['instance']}  {'ok' if ok else 'SHA-256 MISMATCH'}" if a.check else row["instance"], flush=True)
    if a.check:
        print(f"{bad} mismatches")
        raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
