"""Additional exact checks: Appendix A.4 and independent rational kernel ranks."""
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import json
import random
import sys

from .gram import base_representatives, kernel_dimension, matchings


def rank_by_elimination(edges):
    columns = list(combinations(range(len(edges)), 2))
    equations = defaultdict(Counter)
    for index, (a, b) in enumerate(columns):
        for i, j in edges[a]:
            for k, l in edges[b]:
                equations[(min(i, k), max(i, k), min(j, l), max(j, l))][index] += 1
    pivots = {}
    for equation in equations.values():
        row = {key: Fraction(value) for key, value in equation.items()}
        while row:
            pivot = min(row)
            if pivot not in pivots:
                divisor = row[pivot]
                pivots[pivot] = {key: value / divisor for key, value in row.items()}
                break
            scale = row[pivot]
            for key, value in pivots[pivot].items():
                row[key] = row.get(key, 0) - scale * value
                if not row[key]:
                    del row[key]
    return len(columns) - len(pivots)


def appendix_checks(p, alpha, beta):
    inf = p

    def rho(a, t):
        return a if t == inf else inf if t == a else (2 * a - t) % p

    def move(state, code):
        i, j, t, u = state
        ep, et = map(int, code)
        assert (t != inf if ep == 0 else t != alpha[i]), (state, code)
        assert (u != inf if et == 0 else u != beta[j]), (state, code)
        col_f = (2 * i + ep) % (2 * p)
        col_g = (2 * j + 1 + et) % (2 * p)
        assert col_f != col_g, (state, code)
        # Derive the companion variable from its actual cell representatives.
        row_f = t if ep == 0 else rho(alpha[i], t)
        row_g = u if et == 0 else rho(beta[j], u)
        new_i, new_j = (j + et) % p, (i - 1 + ep) % p
        new_t = rho(alpha[new_i], row_f) if et == 0 else row_f
        new_u = rho(beta[new_j], row_g) if ep == 0 else row_g
        return new_i, new_j, new_t, new_u

    def word(state, codes):
        for code in codes.split():
            state = move(state, code)
        return state

    def ground(state):
        i, j, t, u = state
        return ((j == i and t != alpha[i] and u != inf) or
                (j == (i - 1) % p and t != inf and u != beta[j]))

    checked = 0
    for i in range(p):
        prev, nxt = (i - 1) % p, (i + 1) % p
        for t in range(p + 1):
            for u in range(p + 1):
                initial = i, i, t, u
                if ground(initial):
                    continue
                if t == alpha[i] and u != inf and u != beta[i]:
                    codes = '01 11 10'
                    target = nxt, i, (4 * alpha[nxt] - 3 * alpha[i]) % p, rho(beta[i], u)
                elif t == alpha[i] and u == beta[i]:
                    codes = '00 10 00 01'
                    target = prev, prev, (3 * alpha[i] - 2 * alpha[prev]) % p, beta[i]
                elif u == inf and t != inf and t != alpha[i]:
                    codes = '01 00 10'
                    target = i, prev, rho(alpha[i], t), (3 * beta[i] - 2 * beta[prev]) % p
                elif t == inf and u == inf:
                    codes = '11 10 11 01'
                    target = nxt, nxt, rho(alpha[nxt], alpha[i]), (4 * beta[nxt] - 3 * beta[i]) % p
                else:
                    assert t == alpha[i] and u == inf
                    codes = '01 00 00 01'
                    target = prev, prev, (3 * alpha[i] - 2 * alpha[prev]) % p, (4 * beta[prev] - 3 * beta[i]) % p
                terminal = word(initial, codes)
                assert terminal == target and ground(terminal), (p, initial, terminal, target)
                checked += 1
        for j in range(p):
            if i == j:
                continue
            for t in range(p + 1):
                for u in range(p + 1):
                    initial = i, j, t, u
                    if u != inf and t != inf and t != alpha[j]:
                        codes = '00 01'
                    elif u != inf:
                        codes = '10 00'
                    elif t != alpha[i]:
                        codes = '11 01'
                    elif j != (i - 1) % p:
                        codes = '01 00 10 01'
                    else:
                        assert ground(initial)
                        continue
                    terminal = word(initial, codes)
                    assert (terminal[1] - terminal[0]) % p == (j - i - 1) % p
                    checked += 1
    return checked


def main():
    rng = random.Random(20260905)
    rank_checks = 0
    for rows in base_representatives():
        e1 = [(i, j) for i, mask in enumerate(rows) for j in range(4) if mask >> j & 1]
        free = tuple((i, j) for i in range(5) for j in range(4) if (i, j) not in e1)
        for k in (3, 4, 5):
            candidates = list(matchings(free, k))
            for e2 in rng.sample(candidates, 20):
                edges = [(p,) for p in e1] + list(e2)
                assert kernel_dimension(edges) == rank_by_elimination(edges)
                rank_checks += 1
    counts = {}
    for p in (5, 7, 11, 13, 17, 19):
        count = 0
        for _ in range(10):
            alpha, beta = list(range(p)), list(range(p))
            rng.shuffle(alpha)
            rng.shuffle(beta)
            count += appendix_checks(p, alpha, beta)
        counts[p] = count
    # Independent products also verify that the canonical p=3 displayed kernel is zero.
    from . import reference as original
    e1, e2, _ = original.p3_incidence_instance()
    p3_dim = kernel_dimension([(p,) for p in e1] + list(e2))
    assert p3_dim == 0
    result = {'rational_elimination_cross_checks': rank_checks,
              'appendix_words_checked_by_prime': counts,
              'permutation_pairs_per_prime': 10, 'random_seed': 20260905,
              'canonical_p3_displayed_kernel_dimension': p3_dim}
    print(json.dumps(result, indent=2))
    return result


