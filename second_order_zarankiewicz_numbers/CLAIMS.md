# Claim-to-evidence index

All commands run from the package root; generated output goes to runs/latest.
The released counterparts are in results/, witnesses/, and certificates/.

| Claim | Reproduction | Released evidence |
|---|---|---|
| Classical z values and all extremal base types | python reproduce.py all | results/base_extremality.json |
| zRL(4,4)=10 | enumerate 4 4 9 10; enumerate 4 4 9 11; enumerate 4 4 9 12 | exhaustive_RW3plus_4x4_total*.json |
| zRL(5,4)=13 | enumerate 5 4 10 13; enumerate 5 4 10 14; enumerate 5 4 10 15 | exhaustive_RW3plus_5x4_total*.json |
| zRL(6,4)=16 | enumerate 6 4 12 16; enumerate 6 4 12 17; enumerate 6 4 12 18 | exhaustive_RW3plus_6x4_total*.json |
| zRL(5,5)=17 | enumerate 5 5 12 17; enumerate 5 5 12 18 | exhaustive_RW3plus_5x5_total*.json |
| zRL(7,4)=19 | enumerate 7 4 13 19; enumerate 7 4 13 20 | exhaustive_RW3plus_7x4_total*.json |
| Weak values 10,12,14,16,17 on these five grids | python reproduce.py all | exhaustive_weak_* reports and matching witness files |
| Explicit 5 x 4 and three-column examples | python reproduce.py verify | paper_*.json and chain_*.json in witnesses/ |
| z_wL(7,7)=28 | python reproduce.py benchmark77 | weak77_upper_python.json; fano_symmetry.json; weak_7x7_total28.json |
| Seven accepted extensions among 91 | python reproduce.py verify | benchmark77_extensions.json and seven total29 witness files |
| zRL(7,7)>=31 (earlier witness) | discover 7 7 21 31 --criterion benchmark | RW3_7x7_total31.json |
| zRL(7,7)>=32 | python reproduce.py benchmark77 | witnesses/RW3_7x7_total32.json; results/RW3_7x7_total32_verification.json |
| 1,139 / 1,052 / 119 Gram survivors at totals 13 / 14 / 15 | python reproduce.py survivors | gram_survivors.json, including every canonical class |
| Appendix finite checks and 180 rational checks | python reproduce.py all | appendix_verification.json |
| Signed scan from the internal research directions | python reproduce.py research | signed_scan.json |
| Independent C++ weak upper bound | python scripts/verify_cpp.py | weak77_upper.json; cpp_independent_verification.json |

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

The exact value of z2(5,4) and the global equality conjecture z2=zRL remain
open. Survivor files are lists of unresolved cases; no numerical SDP or
uncertified rank assertion is used as evidence.
