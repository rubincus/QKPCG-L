"""Recompute the reference values r of QKPCG-L from the DCKP solution certificates of Wei et al. (2023).

A QKPCG-L instance and its Set I source have the same items, weights, capacity and conflict graph, so the
selection that certifies the best-known DCKP value of the source is feasible for the QKPCG-L instance.
Its QKPCG objective is the reference value r.

The certificates are distributed by the authors of RSO in DCKP-6340_sol_certificates.zip
(https://github.com/Zequn-Wei/DCKP-sol); Set I is in the folder 0-set_I_100ins, one 0/1 vector per
file named <instance>.txt_obj=<value>.

Usage: python qkpcgl_reference.py <instances_folder> <certificate_folder> [output.csv]
Requires Python 3.9+ and NumPy.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qkpcgl_verify import evaluate  # noqa: E402


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) not in (2, 3):
        raise SystemExit(__doc__)
    inst_dir, cert_dir = Path(argv[0]), Path(argv[1])
    manifest = Path(__file__).resolve().parents[1] / "MANIFEST.csv"
    rows = []
    for m in csv.DictReader(open(manifest)):
        cert = next(f for f in cert_dir.rglob(f"{m['source']}.txt_obj=*"))
        items = [i + 1 for i, v in enumerate(cert.read_text().split()) if v == "1"]
        obj, weight, cap, conflicts, ok = evaluate(inst_dir / m["instance"], items)
        if not ok:
            raise SystemExit(f"{cert.name} is not feasible for {m['instance']}")
        rows.append({"instance": m["instance"], "source": m["source"], "dckp_value": cert.name.split("=")[1],
                     "r": obj, "items": len(items), "weight": weight, "capacity": cap})
        print(f"{m['instance']}  r = {obj}", flush=True)
    if len(argv) == 3:
        with open(argv[2], "w", newline="") as fh:
            wr = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
            wr.writeheader()
            wr.writerows(rows)


if __name__ == "__main__":
    main()
