from __future__ import annotations
import random
from typing import List
from rbktypes import Perm
from perms import compose, inverse, perm_to_cycles, pow_perm, modinv
from modlinalg import lcm_many

def random_perm(n: int, rng: random.Random) -> Perm:
    arr = list(range(n))
    rng.shuffle(arr)
    return tuple(arr)

def salt_layer_cipher(C: Perm, r: Perm) -> Perm:
    return compose(inverse(r), compose(C, r))

def recover_r_from_Jd(J: Perm, d: int) -> Perm:
    cyc = perm_to_cycles(J)
    L = lcm_many([len(c) for c in cyc]) if cyc else 1
    d_inv = modinv(d % L, L)
    return pow_perm(J, d_inv)