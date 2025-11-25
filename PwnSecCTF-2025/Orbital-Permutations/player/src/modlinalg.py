#!/usr/bin/env python3
from __future__ import annotations
import math
import random
from typing import List, Optional
from perms import modinv

def lcm_many(vals: List[int]) -> int:
    L = 1
    for v in vals:
        L = (L * v) // math.gcd(L, v)
    return L

def mat_eye(n: int) -> List[List[int]]:
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]

def mat_inv_mod(A: List[List[int]], mod: int) -> List[List[int]]:
    n = len(A)
    M = [row[:] + eye for row, eye in zip(A, mat_eye(n))]
    r = 0
    for c in range(n):
        piv = r
        while piv < n and math.gcd(M[piv][c] % mod, mod) != 1:
            piv += 1
        if piv == n:
            raise ValueError("Matrix not invertible mod {}".format(mod))
        if piv != r:
            M[r], M[piv] = M[piv], M[r]
        a = M[r][c] % mod
        inva = modinv(a, mod)
        for j in range(2 * n):
            M[r][j] = (M[r][j] * inva) % mod
        for i in range(n):
            if i == r:
                continue
            f = M[i][c] % mod
            if f == 0:
                continue
            for j in range(2 * n):
                M[i][j] = (M[i][j] - f * M[r][j]) % mod
        r += 1
        if r == n:
            break
    return [row[n:] for row in M]

def random_invertible_matrix_mod(n: int, mod: int, seed: Optional[int]) -> List[List[int]]:
    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    while True:
        A = [[rng.randrange(mod) for _ in range(n)] for __ in range(n)]
        for i in range(n):
            if math.gcd(A[i][i], mod) != 1:
                A[i][i] = (A[i][i] | 1)
        try:
            _ = mat_inv_mod([row[:] for row in A], mod)
            return A
        except Exception:
            continue

def mat_vec_mul_mod(A: List[List[int]], x: List[int], mod: int) -> List[int]:
    n, m = len(A), len(A[0])
    assert m == len(x)
    out = [0] * n
    for i in range(n):
        s = 0
        Ai = A[i]
        for j in range(m):
            s = (s + (Ai[j] % mod) * (x[j] % mod)) % mod
        out[i] = s
    return out
