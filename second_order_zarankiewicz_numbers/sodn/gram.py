"""Independent exact displayed-edge Gram-kernel audit (Python standard library).

Builds coefficient equations by multiplying bilinear polynomials, rather than
using the supplied line/rectangle closure. A nonzero kernel certifies
reducibility without any universal-resolution assumption. A zero kernel
alone does NOT certify irreducibility.
"""
from collections import Counter, defaultdict
from itertools import combinations, combinations_with_replacement, permutations
from math import factorial
from pathlib import Path
import json


def kernel_dimension(edges):
    pairs = list(combinations(range(len(edges)), 2))
    coefficients = defaultdict(Counter)
    for index, (e, f) in enumerate(pairs):
        for (i, j) in edges[e]:
            for (k, l) in edges[f]:
                monomial = (min(i, k), max(i, k), min(j, l), max(j, l))
                coefficients[monomial][index] += 1
    parent = list(range(len(pairs)))
    parity = [0] * len(pairs)
    grounded = [False] * len(pairs)

    def find(x):
        if parent[x] != x:
            old = parent[x]
            parent[x] = find(old)
            parity[x] ^= parity[old]
        return parent[x]

    for equation in coefficients.values():
        terms = list(equation)
        if len(terms) == 1:
            grounded[find(terms[0])] = True
        else:
            assert len(terms) == 2 and set(equation.values()) == {1}
            a, b = terms
            ra, rb = find(a), find(b)
            if ra == rb:
                if parity[a] == parity[b]:
                    grounded[ra] = True
            else:
                parent[ra] = rb
                parity[ra] = parity[a] ^ parity[b] ^ 1
                grounded[rb] |= grounded[ra]
    roots = {find(i) for i in range(len(pairs))}
    return sum(not grounded[r] for r in roots)


def base_representatives():
    cps = list(permutations(range(4)))

    def permute(mask, cp):
        return sum(1 << cp[j] for j in range(4) if mask >> j & 1)

    reps = set()
    labeled = 0
    for rows in combinations_with_replacement(range(16), 5):
        if sum(r.bit_count() for r in rows) != 10:
            continue
        if any((a & b).bit_count() > 1 for a, b in combinations(rows, 2)):
            continue
        weight = factorial(5)
        for multiplicity in Counter(rows).values():
            weight //= factorial(multiplicity)
        labeled += weight
        reps.add(min(tuple(sorted(permute(r, cp) for r in rows)) for cp in cps))
    assert labeled == 2640 and len(reps) == 3
    return sorted(reps)


def matchings(cells, k):
    def perfect(seq):
        if not seq:
            yield ()
        else:
            for i in range(1, len(seq)):
                for rest in perfect(seq[1:i] + seq[i + 1:]):
                    yield ((seq[0], seq[i]),) + rest
    for subset in combinations(cells, 2 * k):
        yield from perfect(subset)


def automorphisms(e1):
    e1 = set(e1)
    maps = []
    for rp in permutations(range(5)):
        for cp in permutations(range(4)):
            if {(rp[i], cp[j]) for i, j in e1} == e1:
                maps.append({(i, j): (rp[i], cp[j]) for i in range(5) for j in range(4)})
    return maps


def canonical_pairing(e2, maps):
    return min(tuple(sorted(tuple(sorted((mapping[a], mapping[b]))) for a, b in e2))
               for mapping in maps)


