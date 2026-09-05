#!/usr/bin/env python3
"""Exact supplementary checks for the SODN Version 12 internal research notes.

The script uses only the Python standard library.  It does not attempt to
reproduce the global exhaustive searches named in the manuscript.  It checks:

  * the explicit 5 x 4 and 10 x 3 instances;
  * the all-m three-column chain for m=3,...,50;
  * the seven exceptional p=3 transfer words in Appendix A;
  * the ordinary RW3+ closure and the full transfer graph for the canonical
    cyclic K_6 incidence construction.

All logic is exact and combinatorial; no floating-point tolerance is used.
"""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Set, Tuple

Cell = Tuple[int, int]
CellPair = FrozenSet[Cell]
EdgePair = Tuple[int, int]
INF = "inf"


@dataclass(frozen=True)
class Edge:
    name: str
    support: Tuple[Cell, ...]


class DSU:
    def __init__(self, elements: Iterable[Cell]) -> None:
        self.parent = {x: x for x in elements}
        self.rank = {x: 0 for x in elements}

    def find(self, x: Cell) -> Cell:
        p = self.parent[x]
        if p != x:
            self.parent[x] = self.find(p)
        return self.parent[x]

    def union(self, a: Cell, b: Cell) -> bool:
        a = self.find(a)
        b = self.find(b)
        if a == b:
            return False
        if self.rank[a] < self.rank[b]:
            a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1
        return True


def _rectangles(m: int, n: int):
    for i, k in combinations(range(1, m + 1), 2):
        for j, ell in combinations(range(1, n + 1), 2):
            yield (((i, j), (k, ell)), ((i, ell), (k, j)))


def closure_check(
    m: int,
    n: int,
    e1_cells: Sequence[Cell],
    e2_supports: Sequence[Tuple[Cell, Cell]],
    *,
    complementary_rule: bool = True,
) -> Dict[str, object]:
    """Compute the least fixed point of the Version 11 RW3/RW3+ rules."""
    e1 = [Edge(f"a{k + 1}", (c,)) for k, c in enumerate(e1_cells)]
    e2 = [Edge(f"e{k + 1}", tuple(s)) for k, s in enumerate(e2_supports)]
    edges = e1 + e2

    occupied: Set[Cell] = set()
    for edge in edges:
        for cell in edge.support:
            if cell in occupied:
                raise AssertionError(f"simplicity violation at {cell}")
            occupied.add(cell)

    selected_two: Set[CellPair] = {frozenset(edge.support) for edge in e2}
    dsu = DSU(occupied)
    orthogonal: Set[FrozenSet[Cell]] = set()
    contradiction = False

    def root_pair(a: Cell, b: Cell) -> FrozenSet[Cell]:
        return frozenset((dsu.find(a), dsu.find(b)))

    def normalize_orthogonal() -> bool:
        nonlocal orthogonal, contradiction
        normalized: Set[FrozenSet[Cell]] = set()
        for pair in orthogonal:
            a, b = tuple(pair)
            pair2 = root_pair(a, b)
            if len(pair2) == 1:
                contradiction = True
            else:
                normalized.add(pair2)
        changed = normalized != orthogonal
        orthogonal = normalized
        return changed

    def add_orthogonal(a: Cell, b: Cell) -> bool:
        nonlocal contradiction
        pair = root_pair(a, b)
        if len(pair) == 1:
            contradiction = True
            return False
        if pair in orthogonal:
            return False
        orthogonal.add(pair)
        return True

    def is_orthogonal(a: Cell, b: Cell) -> bool:
        pair = root_pair(a, b)
        return len(pair) == 2 and pair in orthogonal

    def delta(a: Cell, b: Cell) -> int:
        return int(frozenset((a, b)) in selected_two)

    rectangles = list(_rectangles(m, n))
    rounds = 0
    while True:
        rounds += 1
        changed = normalize_orthogonal()

        # Line rule.
        for a, b in combinations(sorted(occupied), 2):
            if a[0] == b[0] or a[1] == b[1]:
                changed |= dsu.union(a, b) if delta(a, b) else add_orthogonal(a, b)

        # Complementary-pair rule.
        if complementary_rule:
            for diagonal1, diagonal2 in rectangles:
                if (
                    frozenset(diagonal1) in selected_two
                    and frozenset(diagonal2) in selected_two
                ):
                    changed |= dsu.union(*diagonal1)
                    changed |= dsu.union(*diagonal2)

        changed |= normalize_orthogonal()

        # Rectangle transfer, in both directions.
        for diagonal1, diagonal2 in rectangles:
            for target, companion in ((diagonal1, diagonal2), (diagonal2, diagonal1)):
                c, d = companion
                if delta(c, d) == 0:
                    companion_known = (
                        c not in occupied or d not in occupied or is_orthogonal(c, d)
                    )
                else:
                    companion_known = (
                        c in occupied and d in occupied and dsu.find(c) == dsu.find(d)
                    )
                if not companion_known:
                    continue

                a, b = target
                if delta(a, b) == 1:
                    if a not in occupied or b not in occupied:
                        raise AssertionError("selected diagonal has an unoccupied half")
                    changed |= dsu.union(a, b)
                elif a in occupied and b in occupied:
                    changed |= add_orthogonal(a, b)

        changed |= normalize_orthogonal()
        if contradiction or not changed:
            break
        if rounds > 10000:
            raise RuntimeError("fixed-point closure did not terminate")

    edge_roots: Dict[str, Optional[Cell]] = {}
    resolved = True
    for edge in edges:
        roots = {dsu.find(c) for c in edge.support}
        if len(roots) != 1:
            resolved = False
            edge_roots[edge.name] = None
        else:
            edge_roots[edge.name] = next(iter(roots))

    injective = resolved and len(set(edge_roots.values())) == len(edges)
    missing: List[Tuple[str, str]] = []
    for edge, other in combinations(edges, 2):
        if not any(
            is_orthogonal(a, b) for a in edge.support for b in other.support
        ):
            missing.append((edge.name, other.name))

    return {
        "m": m,
        "n": n,
        "e1": len(e1),
        "e2": len(e2),
        "selected_edges": len(edges),
        "rounds": rounds,
        "resolved": resolved,
        "injective": injective,
        "missing_count": len(missing),
        "contradiction": contradiction,
        "accepted": resolved and injective and not missing and not contradiction,
        "orthogonal_class_pairs": len(orthogonal),
        "missing_examples": missing[:10],
    }


def chain_instance(m: int):
    if m < 3:
        raise ValueError("m must be at least 3")
    e1 = [(1, 1), (1, 2), (2, 1), (2, 3), (3, 2), (3, 3)]
    e1.extend((i, 2) for i in range(4, m + 1))
    e2 = [((i, 1), (i + 1, 3)) for i in range(3, m)]
    return e1, e2


def explicit_instances() -> Dict[str, Dict[str, object]]:
    e1_54 = [
        (1, 2), (1, 3), (1, 4), (2, 1), (2, 2),
        (3, 4), (4, 1), (4, 4), (5, 1), (5, 3),
    ]
    e2_54 = [((3, 1), (4, 2)), ((5, 2), (3, 3)), ((4, 3), (2, 4))]

    e1_103 = [
        (1, 1), (1, 2), (2, 1), (2, 3), (3, 2), (3, 3),
        (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 2), (10, 2),
    ]
    e2_103 = [
        ((10, 3), (9, 1)), ((4, 2), (4, 3)), ((5, 3), (2, 2)),
        ((1, 3), (6, 2)), ((3, 1), (9, 3)), ((7, 2), (6, 3)),
        ((5, 2), (8, 3)),
    ]

    return {
        "explicit_5x4": closure_check(5, 4, e1_54, e2_54, complementary_rule=False),
        "explicit_10x3": closure_check(10, 3, e1_103, e2_103, complementary_rule=False),
    }


def p1f_k6() -> List[List[Tuple[int, int]]]:
    """A cyclic perfect one-factorization of K_6 on vertices 0,...,5."""
    factors: List[List[Tuple[int, int]]] = []
    for anchor in range(5):
        factor = [(5, anchor)]
        used = {anchor}
        for x in range(5):
            if x in used:
                continue
            y = (2 * anchor - x) % 5
            if y == x or y in used:
                continue
            factor.append(tuple(sorted((x, y))))
            used.add(x)
            used.add(y)
        if len(factor) != 3:
            raise AssertionError("invalid factor")
        factors.append(factor)

    all_edges = [tuple(sorted(e)) for factor in factors for e in factor]
    if set(all_edges) != set(combinations(range(6), 2)):
        raise AssertionError("factors do not partition K_6")

    for factor, other in combinations(factors, 2):
        adjacency = {v: [] for v in range(6)}
        for a, b in factor + other:
            adjacency[a].append(b)
            adjacency[b].append(a)
        seen: Set[int] = set()
        stack = [0]
        while stack:
            v = stack.pop()
            if v in seen:
                continue
            seen.add(v)
            stack.extend(adjacency[v])
        if len(seen) != 6 or any(len(adjacency[v]) != 2 for v in adjacency):
            raise AssertionError("factor pair is not a Hamilton cycle")
    return factors


def p3_incidence_instance():
    vertices = list(range(6))
    row_edges = list(combinations(vertices, 2))
    row_index = {edge: i + 1 for i, edge in enumerate(row_edges)}

    e1: List[Cell] = []
    edge_objects: List[Edge] = []
    for edge in row_edges:
        row = row_index[edge]
        for column in edge:
            cell = (row, column + 1)
            e1.append(cell)
            edge_objects.append(Edge(f"I{edge}_{column}", (cell,)))

    e2: List[Tuple[Cell, Cell]] = []
    for factor_index, factor in enumerate(p1f_k6()):
        # For p=3, the two non-anchor rows are paired regardless of labels.
        for anchor_index, anchor_edge in enumerate(factor):
            other_edges = [edge for i, edge in enumerate(factor) if i != anchor_index]
            row_a = row_index[tuple(sorted(other_edges[0]))]
            row_b = row_index[tuple(sorted(other_edges[1]))]
            u, v = anchor_edge
            diagonal0 = ((row_a, u + 1), (row_b, v + 1))
            diagonal1 = ((row_a, v + 1), (row_b, u + 1))
            e2.extend((diagonal0, diagonal1))
            edge_objects.append(Edge(f"F{factor_index}a{anchor_index}d0", diagonal0))
            edge_objects.append(Edge(f"F{factor_index}a{anchor_index}d1", diagonal1))

    if len(e1) != 30 or len(e2) != 30:
        raise AssertionError("wrong p=3 incidence counts")
    return e1, e2, edge_objects


def p3_transfer_graph() -> Dict[str, object]:
    e1, e2, edges = p3_incidence_instance()
    closure = closure_check(15, 6, e1, e2, complementary_rule=True)

    owner: Dict[Cell, int] = {}
    for edge_index, edge in enumerate(edges):
        for cell in edge.support:
            if cell in owner:
                raise AssertionError(f"non-simple p=3 support at {cell}")
            owner[cell] = edge_index

    def gram_variable(a: Cell, b: Cell) -> Optional[EdgePair]:
        if a not in owner or b not in owner:
            return None
        e, f = owner[a], owner[b]
        if e == f:
            return None
        return (e, f) if e < f else (f, e)

    variables = set(combinations(range(len(edges)), 2))
    grounded: Set[EdgePair] = set()
    adjacency: Dict[EdgePair, Set[EdgePair]] = {var: set() for var in variables}

    occupied_cells = list(owner)
    for a, b in combinations(occupied_cells, 2):
        if a[0] == b[0] or a[1] == b[1]:
            var = gram_variable(a, b)
            if var is not None:
                grounded.add(var)

    for diagonal1, diagonal2 in _rectangles(15, 6):
        var1 = gram_variable(*diagonal1)
        var2 = gram_variable(*diagonal2)
        surviving = [var for var in (var1, var2) if var is not None]
        if len(surviving) == 1:
            grounded.add(surviving[0])
        elif len(surviving) == 2:
            if surviving[0] == surviving[1]:
                grounded.add(surviving[0])
            else:
                adjacency[surviving[0]].add(surviving[1])
                adjacency[surviving[1]].add(surviving[0])

    seen: Set[EdgePair] = set()
    components = []
    for start in sorted(variables):
        if start in seen:
            continue
        color = {start: 0}
        stack = [start]
        seen.add(start)
        nodes: List[EdgePair] = []
        is_bipartite = True
        has_ground = False
        while stack:
            var = stack.pop()
            nodes.append(var)
            has_ground |= var in grounded
            for neighbor in adjacency[var]:
                if neighbor not in color:
                    color[neighbor] = 1 - color[var]
                    seen.add(neighbor)
                    stack.append(neighbor)
                elif color[neighbor] == color[var]:
                    is_bipartite = False
        components.append(
            {"size": len(nodes), "grounded": has_ground, "bipartite": is_bipartite}
        )

    categories = Counter((c["grounded"], c["bipartite"]) for c in components)
    category_nodes = Counter()
    for component in components:
        category_nodes[(component["grounded"], component["bipartite"])] += component["size"]

    odd_ungrounded = [
        c for c in components if not c["grounded"] and not c["bipartite"]
    ]
    free_bipartite = [
        c for c in components if not c["grounded"] and c["bipartite"]
    ]

    if closure["missing_count"] != sum(c["size"] for c in odd_ungrounded):
        raise AssertionError("RW3+ missing count does not match odd components")
    if free_bipartite:
        raise AssertionError("unexpected free p=3 transfer component")

    def label(key: Tuple[bool, bool]) -> str:
        return f"grounded={str(key[0]).lower()},bipartite={str(key[1]).lower()}"

    return {
        "closure": closure,
        "selected_edge_vectors": len(edges),
        "off_diagonal_variables": len(variables),
        "ground_equations": len(grounded),
        "component_count": len(components),
        "component_counts": {label(k): v for k, v in sorted(categories.items())},
        "component_variable_counts": {
            label(k): v for k, v in sorted(category_nodes.items())
        },
        "ungrounded_odd_components": len(odd_ungrounded),
        "ungrounded_odd_size_distribution": dict(
            sorted(Counter(c["size"] for c in odd_ungrounded).items())
        ),
        "ungrounded_bipartite_components": len(free_bipartite),
        "rw3plus_unresolved_equals_odd_variables": True,
    }


def rho_p3(a: int, x):
    if x == INF:
        return a
    if x == a:
        return INF
    return (2 * a - x) % 3


def p3_word_move(state, code: str):
    i, j, t, u = state
    eps, eta = int(code[0]), int(code[1])

    f_available = (eps == 0 and t != INF) or (eps == 1 and t != i)
    g_available = (eta == 0 and u != INF) or (eta == 1 and u != j)
    if not f_available or not g_available:
        raise AssertionError(f"unavailable endpoint: state={state}, move={code}")
    if code == "10" and j == i:
        raise AssertionError("move 10 uses the same outer column")
    if code == "01" and j == (i - 1) % 3:
        raise AssertionError("move 01 uses the same outer column")

    if code == "00":
        new_t = rho_p3(j, t)
        new_u = rho_p3((i - 1) % 3, u)
    elif code == "01":
        new_t = t
        new_u = rho_p3((i - 1) % 3, rho_p3(j, u))
    elif code == "10":
        new_t = rho_p3(j, rho_p3(i, t))
        new_u = u
    elif code == "11":
        new_t = rho_p3(i, t)
        new_u = rho_p3(j, u)
    else:
        raise ValueError(code)

    return ((j + eta) % 3, (i - 1 + eps) % 3, new_t, new_u)


def check_p3_words() -> Dict[str, object]:
    words = {
        "(0,0)": (0, 0, "00 10 00 01 00 10 00 10 11"),
        "(0,1)": (0, 1, "00 10 00 00 01"),
        "(0,2)": (0, 2, "01 00 01 00 10 00 01"),
        "(0,inf)": (0, INF, "01 00 00 00 01"),
        "(1,inf)": (1, INF, "01 00 00 10 00"),
        "(2,inf)": (2, INF, "01 00 10 00 01 00 01"),
        "(inf,inf)": (INF, INF, "11 10 00 10 00 01 00 10 00"),
    }
    results = {}
    for name, (t, u, word) in words.items():
        initial = (0, 0, t, u)
        state = initial
        moves = word.split()
        for code in moves:
            state = p3_word_move(state, code)
        closed = state == initial
        odd = len(moves) % 2 == 1
        if not closed or not odd:
            raise AssertionError(f"invalid p=3 word {name}")
        results[name] = {"length": len(moves), "closed": closed, "odd": odd}
    return {"all_endpoint_valid": True, "all_closed": True, "all_odd": True, "words": results}


