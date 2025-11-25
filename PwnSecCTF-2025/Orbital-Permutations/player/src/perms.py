#!/usr/bin/python3
from __future__ import annotations
import math
from typing import List, Tuple, Sequence
from rbktypes import Perm

def compose(p: Perm, q: Perm) -> Perm:
    if len(p) != len(q):
        raise ValueError("Permutation size mismatch")
    return tuple(p[i] for i in q)

def inverse(p: Perm) -> Perm:
    inv = [0] * len(p)
    for i, j in enumerate(p):
        inv[j] = i
    return tuple(inv)

def identity(n: int) -> Perm:
    return tuple(range(n))

def cycle_to_perm(n: int, cycle: Sequence[int]) -> Perm:
    out = list(range(n))
    L = len(cycle)
    for i in range(L):
        out[cycle[i]] = cycle[(i + 1) % L]
    return tuple(out)

def perm_to_cycles(p: Perm) -> List[List[int]]:
    n = len(p)
    seen = [False] * n
    cycles: List[List[int]] = []
    for i in range(n):
        if seen[i] or p[i] == i:
            continue
        cur = i
        cyc: List[int] = []
        while not seen[cur]:
            seen[cur] = True
            cyc.append(cur)
            cur = p[cur]
        if cyc:
            cycles.append(cyc)
    return cycles

def pow_perm(p: Perm, e: int) -> Perm:
    if e < 0:
        p = inverse(p)
        e = -e
    out = identity(len(p))
    base = p
    while e:
        if e & 1:
            out = compose(base, out)
        base = compose(base, base)
        e >>= 1
    return out

def perm_order(p: Perm) -> int:
    cyc = perm_to_cycles(p)
    if not cyc:
        return 1
    L = 1
    for c in cyc:
        L = (L * len(c)) // math.gcd(L, len(c))
    return L

def modinv(a: int, m: int) -> int:
    a %= m
    if m == 1:
        return 0
    t, nt = 0, 1
    r, nr = m, a
    while nr:
        q = r // nr
        t, nt = nt, t - q * nt
        r, nr = nr, r - q * nr
    if r != 1:
        raise ValueError("no inverse")
    return t % m