# Coverage and exactness

The finite searches are exact and use integer combinatorics. The following
coverage arguments explain how the generated records support upper bounds.

1. Small bases: enumerate sorted row masks of total degree z, enforce
   column-pair disjointness, and quotient by all column permutations.
   Sorting rows loses no unlabeled base. Repeat at z+1 and obtain no bases.
2. Matchings: branch on the first remaining cell, either unused or paired
   with each later cell. This uniquely covers every matching. A remaining
   f cells and k pairs have f!/((f-2k)! 2^k k!) completions.
3. Safe pruning: weak, RW3, and RW3+ acceptance are hereditary under deletion
   of whole selected two-edges with E1 fixed. The deletion argument below handles
   the deletion of one member of a complementary pair explicitly. A rejected
   prefix has no accepted extension. Accepted and weighted rejected counts
   must equal the full matching count.
4. Independent closure: the reference implementation directly tracks cells
   and orthogonality. The second tracks knowledge components for rectangle
   diagonals, grounded by lines, holes, and (in RW3+) complementary pairs.
   Resolving a selected pair merges all its representative-pair components.
   It performs no ungrounded odd-cycle inference.
5. Independent coverage checks: reference enumeration compares entire
   rejection/acceptance records; unpruned runs check small cases independently
   of the pruning argument.
6. Fano completeness: the pair bound forces seven degree-three rows at the
   21-edge extremum. Exact covers enumerate 30 fixed-column row sets, in one
   isomorphism class. The 168 automorphisms are transitive on 168 individually
   weak-admissible pairs, allowing one pair to be fixed without losing any
   possible size. Increasing pair lists cover all normalized augmentations.
   No size-eight augmentation is accepted.
7. Gram filter: direct polynomial products give exact homogeneous equations.
   A nonzero symmetric kernel H has zero diagonal by simplicity and trace
   zero. I-H/lambda_max(H) is positive semidefinite and singular, so the
   polynomial has a shorter SOS. This implication does not need universal
   resolution. The converse does.
8. Scope: chain tests cover m=3,...,50. Appendix tests check the seven
   exceptional p=3 words and 2,767,800 words for six larger primes with
   recorded seeded label permutations. The infinite claims use the proofs;
   the finite computations do not replace them.

Candidate counts over base representatives are not augmentation isomorphism
counts. Full survivor quotienting is a separate operation and exports every
canonical representative. The 7 x 7 prefix counts are conditioned on the
specified first pair; they are not counts over all labeled grids.

## Why rejection pruning is exhaustive

Fix E1 and delete whole selected two-edges from a simple accepted family.
For weak admissibility, deletion cannot fill an empty opposite cell or
create a forbidden opposite-cell pattern. It removes dependency arcs.
If one member of a complementary pair is deleted, the remaining member
has holes on its opposite diagonal and therefore has no outgoing dependency
arcs. The contracted dependency graph acquires no cycle.

For RW3 and RW3+, restrict a resolution certificate to the remaining occupied
cells. Identifications only join the two halves of one selected edge.
Consequently no identification or saturation between surviving edges
requires a deleted cell. Line certificates persist. In a rectangle transfer,
if the companion diagonal loses a cell, its prescribed value is now zero
and the hole rule supplies the certificate. Otherwise the old certificate
persists by induction. Removing one member of a complementary pair leaves
the other resolved by the hole rule. All required surviving identifications
and orthogonalities persist.

Acceptance is therefore hereditary under deletion of whole two-edges.
A rejected prefix has no accepted extension. The first-free-cell branching
rule partitions all remaining matchings, and the factorial completion count
weights each rejected subtree exactly. Every result records those prefixes
and verifies accepted plus rejected counts against the unpruned total.

## The displayed-basis Gram filter

If a nonzero symmetric H satisfies f^T H f = 0 for the displayed bilinear
forms f, simplicity forces the diagonal of H to vanish. Thus H has trace
zero and a positive largest eigenvalue. The matrix I-H/lambda_max(H) is
positive semidefinite and singular and represents the same polynomial,
which certifies a shorter sum of squares.

A zero kernel does not prove irreducibility unless universal resolution
has separately been established. This is why the exported total-14 and
total-15 survivors are unresolved research cases.
