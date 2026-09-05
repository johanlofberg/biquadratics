# Reproducible computations for Second Order Zarankiewicz Number

This folder contains the scripts, data, explicit witnesses, and independent
verifiers for the paper by Johan Löfberg and Liqun Qi.
[METHODS.md](METHODS.md) explains coverage and interpretation, and
[CLAIMS.md](CLAIMS.md) maps the numerical claims to reproducible evidence.

| Grid | Exact weak value | Recursive-line value |
|---|---:|---:|
| 4 x 4 | 10 | 10 |
| 5 x 4 | 12 | 13 |
| 6 x 4 | 14 | 16 |
| 5 x 5 | 16 | 17 |
| 7 x 4 | 17 | 19 |
| 7 x 7 | 28 | at least 31 |

The 5 x 5 and 7 x 4 recursive-line entries strengthen version 13 to exact
values. The specified 7 x 7 weak augmentation has exactly seven accepted
extensions among 91 candidates under S, W2, W2prime, and RW3.

## Reproduce

Python 3.10 or later; recorded local runs use Python 3.14.6. All required
computations use the standard library. Do not use Python's -O flag: some
independent checks use assertions.

From this project folder, second_order_zarankiewicz_numbers:

~~~console
python scripts/verify_manifest.py
python reproduce.py verify
python reproduce.py all --reference --research
python -m unittest discover -s tests -v
~~~

On Windows, use py -3 in place of python if necessary. The checksum command verifies the archived files. The verify command
checks the saved witnesses using two independently written exact closure
implementations and rechecks all 91 extensions. The all command regenerates the
base classifications, exhaustive searches, benchmark, complete Gram survivor
lists, and appendix checks. The --reference option repeats the recursive
searches with the direct cell-level implementation and compares its complete
rejection and acceptance records with the fast results. The optional --research
flag repeats the signed-deviation scan.

Generated outputs go to runs/latest, leaving the released baselines intact:

~~~console
python reproduce.py --output runs/my-run all
~~~

A local fast full run including the signed scan took about 60 seconds.
The full reference run including the signed scan took about four minutes;
timings are not mathematical claims.

Individual tasks:

~~~console
python reproduce.py enumerate 6 4 12 17
python reproduce.py enumerate 7 4 13 18 --criterion weak
python reproduce.py discover 5 5 12 17
python reproduce.py discover 7 7 21 31 --criterion benchmark
python reproduce.py benchmark77
python reproduce.py survivors
~~~

Numeric arguments are rows, columns, fixed E1 size, and target total.
Seeded discovery returns a verified witness or an explicit failure at its
restart limit. Discovery failure is never an upper-bound proof.

## Independent C++ check

Optional; all computations also run in Python. With g++ supporting C++17:

~~~console
python scripts/verify_cpp.py
~~~

This checks 6,150 predicate cases and the full weak 7 x 7 enumeration.
Accepted normalized-prefix counts at sizes 1 through 8 are
1, 98, 2305, 12715, 10920, 681, 2, 0.

## Evidence

- CLAIMS.md maps claims to commands and results.
- METHODS.md explains coverage and interpretation.
- witnesses/ stores explicit zero-based [row,column] supports and provenance.
- results/ stores expected counts, every rejected search prefix, and every
  accepted augmentation at the enumerated totals.
- results/gram_survivors.json exports all canonical survivors at totals
  13, 14, and 15; its flattened cell IDs mean row*4+column.
- certificates/fano_symmetry.json supplies the actual 168 automorphisms.
- sodn/reference.py and sodn/core.py independently implement RW3/RW3+.
- tests/ checks these implementations and compares pruning with unpruned runs.
- SOURCE_PROVENANCE.json identifies supplied sources used in the portable code.
- SHA256SUMS.txt records the released file contents.

Zero displayed-basis kernel alone is not an irreducibility certificate.
The 1,052 total-14 and 119 total-15 cases remain unresolved. This package
does not determine z2(5,4); the correct interval is 13 <= z2(5,4) <= 15.
The infinite theorems rely on the mathematical proofs. Finite tests are
explicitly described as supporting checks. Weak three-column values use the
[Qi–Löfberg–Chen theorem, version 3](https://arxiv.org/html/2608.06050v3).

## Generated manuscript tables

~~~console
python scripts/build_tables.py
~~~

This regenerates paper/computational_data.tex and paper/benchmark_data.tex
from the released JSON records. They contain the search-count tables and
explicit benchmark supports used in the manuscript.

The repository-wide GitHub Actions workflow repeats verification on Python
3.10 and 3.14, including the independent C++ enumeration.

## Archive and citation

~~~console
python scripts/package_release.py runs/second_order_zarankiewicz_numbers.zip
~~~

The command builds a standalone archive and refreshes SHA256SUMS.txt.
[CITATION.cff](CITATION.cff) identifies the authors and repository.
