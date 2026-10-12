# QKPCG-L: large instances of the quadratic knapsack problem with conflict graphs

QKPCG-L contains 50 instances of the quadratic knapsack problem with conflict graphs (QKPCG) with
n = 1500 and n = 2000 items. Each instance derives from one instance of classes 11-20 of Set I of the
disjunctively constrained knapsack problem (DCKP) and adds quadratic profits drawn from the
distribution of the classic QKPCG set of Shi et al. (2017). Every instance comes with a reference value
r obtained from published DCKP solution certificates.

<!-- Agregar aqui la cita del articulo y el DOI de Zenodo cuando existan. -->

## Contents

| Path | Content |
|---|---|
| `instances/` | the 50 instances, `<source>_d100.txt` |
| `MANIFEST.csv` | source instance, SHA-256 of both public copies of the source, generation parameters, seed and SHA-256 of each instance |
| `reference_values.csv` | reference value r, number of items, weight and capacity of the reference selection |
| `tools/qkpcgl_verify.py` | evaluates a solution: objective, weight, conflicting pairs, feasibility |
| `tools/qkpcgl_generate.py` | regenerates the instances from Set I and checks them against the manifest |
| `tools/qkpcgl_reference.py` | recomputes r from the DCKP solution certificates |

The tools need Python 3.9 or later and NumPy. The repository stores the instance files byte for byte
(see `.gitattributes`), so their SHA-256 digests match `MANIFEST.csv` on every platform.

## Problem and file format

Given n items with profits p_i, weights w_i and pairwise profits q_ij, a capacity C and a conflict graph
G = (V, E), the QKPCG selects a subset S of items that maximizes
sum_{i in S} p_i + sum_{i < j in S} q_ij, subject to sum_{i in S} w_i <= C and to S containing no edge of G.

The files follow the format of the classic set: `n |E| C`; the n profits; the n weights; the upper
triangle of q row by row (row i holds q_{i,i+1}, ..., q_{i,n}); and the |E| edges as pairs of 1-based
items. As in the classic files, pairs in conflict also carry a value of q, which no feasible solution
collects.

## Generation protocol

1. Inherited data. Each instance copies n, C = 4000, the profits, the weights (in [1, 400]) and the
   conflict graph of its Set I source unchanged. Classes 11-15 have n = 1500 and classes 16-20 have
   n = 2000. Within each size, the conflict-graph density grows from 0.04 to 0.20 in steps of 0.04,
   with five instances per class. In the sources, p_i = w_i + 10.
2. Quadratic profits. Every pair i < j receives an integer q_ij drawn independently and uniformly
   from {1, ..., 50}.
3. Seeds. The draws come from NumPy's PCG64 generator with the seed listed in `MANIFEST.csv`. The seed
   is the first eight bytes (little endian) of SHA-256("<sha256 of the source file>:1.0:1:50"),
   computed on the copy of Set I that ends lines with CRLF.
4. Verification. Each file is read back and compared field by field with its source; `MANIFEST.csv`
   records the SHA-256 of every instance.

Set I is distributed by Wei and Hao on Mendeley Data (doi:10.17632/gb5hhjkygd.1, lines ending in LF)
and in other copies with CRLF line endings. Both copies have the same content, and the generator
reproduces every instance byte for byte from either of them:

```
python tools/qkpcgl_generate.py <set_I_folder> <output_folder> --check
```

## Reference values

A QKPCG-L instance and its DCKP source have the same feasible set, so the selection that certifies the
best-known DCKP value of the source (Wei et al., 2023) is also feasible for the QKPCG-L instance. Its
QKPCG objective is the reference value r in `reference_values.csv`. The reference selections contain
37 to 106 items, and r ranges from 20 279 to 145 866. To recompute r from the certificates published
at https://github.com/Zequn-Wei/DCKP-sol:

```
python tools/qkpcgl_reference.py instances <certificate_folder> reference_values.csv
```

## Verifying a solution

A solution file lists the selected items as 1-based indices separated by blanks or new lines:

```
python tools/qkpcgl_verify.py instances/20I3_d100.txt solution.txt
```

## Sources and citation

When using QKPCG-L, please cite the article that introduces it and the sources of its data:

- Shi, X., Wu, L., Meng, X. (2017). A new optimization model for the sustainable development: Quadratic
  knapsack problem with conflict graphs. Sustainability 9(2), 236. doi:10.3390/su9020236
- Hifi, M., Michrafy, M. (2006). A reactive local search-based algorithm for the disjunctively
  constrained knapsack problem. Journal of the Operational Research Society 57(6), 718-726.
  doi:10.1057/palgrave.jors.2602046
- Quan, Z., Wu, L. (2017). Cooperative parallel adaptive neighbourhood search for the disjunctively
  constrained knapsack problem. Engineering Optimization 49(9), 1541-1557.
- Wei, Z., Hao, J.-K. (2021). Benchmark instances of the disjunctively constrained knapsack problem
  (DCKP). Mendeley Data, V1. doi:10.17632/gb5hhjkygd.1
- Wei, Z., Hao, J.-K., Ren, J., Glover, F. (2023). Responsive strategic oscillation for solving the
  disjunctively constrained knapsack problem. European Journal of Operational Research 309(3),
  993-1009. doi:10.1016/j.ejor.2023.02.009

## License

The instances and the CSV files are derived from Set I of the DCKP (Mendeley Data, CC BY 4.0) with the
changes described above, and are distributed under the Creative Commons Attribution 4.0 International
license (`LICENSE-DATA`). The tools are distributed under the MIT license (`LICENSE`).
