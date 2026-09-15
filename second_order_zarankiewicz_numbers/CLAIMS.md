# Claim-to-evidence index

This index matches the 44-page arXiv:2608.30555v3 manuscript identified in
[MANUSCRIPT.md](MANUSCRIPT.md). All commands run from the package root;
generated output goes to `runs/latest`. Released counterparts are in
`results/`, `witnesses/`, and `certificates/`.

| Claim | Evidence type | Reproduction or proof | Released evidence |
|---|---|---|---|
| Classical z values and all extremal base types | Exact enumeration | `python reproduce.py all` | `results/base_extremality.json` |
| zRL(4,4)=10 | Exact enumeration | `enumerate 4 4 9 10`; totals 11 and 12 likewise | `results/exhaustive_RW3plus_4x4_total*.json` |
| zRL(5,4)=13 | Exact enumeration | `enumerate 5 4 10 13`; totals 14 and 15 likewise | `results/exhaustive_RW3plus_5x4_total*.json`; `witnesses/paper_5x4.json` |
| z2(5,4)=zSL(5,4)=zRL(5,4)=13 | Analytic theorem plus finite lower-bound check | Manuscript Corollary 4.19 and Appendix B: product identities, SOS shortening identities, forbidden-pair orbits, and weighted covers for bases B and C | The proof is printed in Appendix B; the lower-bound witness and zRL enumeration are released here |
| zRL(6,4)=16 | Exact enumeration | `enumerate 6 4 12 16`; totals 17 and 18 likewise | `results/exhaustive_RW3plus_6x4_total*.json`; matching witness |
| z2(6,4)=zSL(6,4)=zRL(6,4)=16 | Analytic theorem plus finite lower-bound check | Manuscript Corollary 4.23: five-row restriction argument; zRL witness gives the lower bound | The proof is in the manuscript; enumeration and witness are released here |
| zRL(5,5)=17 | Exact enumeration | `enumerate 5 5 12 17`; total 18 likewise | `results/exhaustive_RW3plus_5x5_total*.json` |
| zRL(7,4)=19 | Exact enumeration | `enumerate 7 4 13 19`; total 20 likewise | `results/exhaustive_RW3plus_7x4_total*.json` |
| Weak values 10,12,14,16,17 on the five small grids | Exact enumeration | `python reproduce.py all` | `results/exhaustive_weak_*.json` and matching witnesses |
| z_wL(7,7)=28 | Exact normalized enumeration | `python reproduce.py benchmark77` | `results/weak77_upper_python.json`; `certificates/fano_symmetry.json`; `witnesses/weak_7x7_total28.json` |
| Seven accepted 7 x 7 extensions among 91 | Exact verification | `python reproduce.py verify` | `results/benchmark77_extensions.json` and seven total-29 witnesses |
| zRL(7,7)>=32 | Explicit witness | `python reproduce.py benchmark77` | `witnesses/RW3_7x7_total32.json`; `results/RW3_7x7_total32_verification.json` |
| zSL(15,6)=z2(15,6)=60 | Analytic theorem plus two independent exact checkers | `python reproduce.py signed-p3`; manuscript Theorem 7.5 and universal cell bound | `witnesses/incidence_p3.json`; `results/signed_p3_verification.json` |
| Exceptional p=3 transfer words and graph | Exact supporting checks | `python reproduce.py all` | `results/appendix_verification.json` |
| 1,139 / 1,052 / 119 historical Gram survivors at totals 13 / 14 / 15 | Exact historical screening | `python reproduce.py survivors` | `results/gram_survivors.json`, including every canonical class |
| Appendix finite checks and 180 rational checks | Exact supporting checks | `python reproduce.py all` | `results/appendix_verification.json` |
| Signed 5 x 4 scan | Exact research cross-check | `python reproduce.py research` | `results/signed_scan.json` |
| Independent C++ weak upper bound | Independent exact enumeration | `python scripts/verify_cpp.py` | `results/weak77_upper.json`; `results/cpp_independent_verification.json` |

Individual enumerate and discover fragments above are appended to
python reproduce.py. Each exact recursive value is established by a positive
witness and zero acceptance at every larger total up to the cell bound.
Weak upper bounds need only exclusion of the first larger total because
weak admissibility is hereditary under deletion of selected two-edges.

The weak 7 x 7 fixed-pair search is exhaustive after the explicitly verified
automorphism normalization. Its counts do not represent all labeled grids.

The all-m three-column and all-prime incidence claims are analytic theorems,
with supporting finite checks. The weak three-column values cite
https://arxiv.org/html/2608.06050v3. No new local MILP computation is needed
for that imported theorem.

The global equality conjecture z2=zRL remains open outside the families and
finite cases proved in the manuscript and cited concurrent work. The Gram
survivor file is historical: survival only means that the displayed-basis
kernel screen did not shorten that presentation. Appendix B's stronger local
identities prove that every total-14 and total-15 case is reducible. No
numerical SDP or uncertified rank assertion is used as evidence.
