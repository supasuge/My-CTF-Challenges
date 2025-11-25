#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage:
  python solve.py handout.json
"""
from __future__ import annotations
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import argparse
import base64
import json
import math
from typing import Dict, List, Tuple, Sequence, Optional

Perm = Tuple[int, ...]

def compose(p: Perm, q: Perm) -> Perm:
    if len(p) != len(q):
        raise ValueError("Permutation size mismatch")
    return tuple(p[i] for i in q)

def inverse(p: Perm) -> Perm:
    inv = [0]*len(p)
    for i,j in enumerate(p):
        inv[j] = i
    return tuple(inv)

def identity(n: int) -> Perm:
    return tuple(range(n))

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

def perm_to_cycles(p: Perm) -> List[List[int]]:
    n = len(p)
    seen = [False]*n
    cycles = []
    for i in range(n):
        if seen[i] or p[i] == i:
            continue
        cur = i
        cyc = []
        while not seen[cur]:
            seen[cur] = True
            cyc.append(cur)
            cur = p[cur]
        if cyc:
            cycles.append(cyc)
    return cycles

def modinv(a: int, m: int) -> int:
    a %= m
    if m == 1:
        return 0
    t, nt = 0, 1
    r, nr = m, a
    while nr:
        q = r // nr
        t, nt = nt, t - q*nt
        r, nr = nr, r - q*nr
    if r != 1:
        raise ValueError("no inverse")
    return t % m


def crt_pair(e1: int, m1: int, e2: int, m2: int) -> Tuple[int,int]:
    """
    Solve x ≡ e1 (mod m1), x ≡ e2 (mod m2).
    Returns (x mod lcm, lcm). Raises if inconsistent (i.e., no solution).
    Works even when m1, m2 are not coprime.
    """
    g = math.gcd(m1, m2)
    if (e2 - e1) % g != 0:
        raise ValueError(f"CRT inconsistency: x≡{e1}(mod {m1}) and x≡{e2}(mod {m2})")
    # Reduce to coprime moduli
    m1p, m2p = m1 // g, m2 // g
    # We want m1 * t ≡ (e2 - e1) (mod m2) -> m1p * t ≡ (e2 - e1)/g (mod m2p)
    rhs = (e2 - e1) // g
    inv = modinv(m1p % m2p, m2p)  # guaranteed to exist
    t = (rhs * inv) % m2p
    x = e1 + m1 * t
    l = (m1 // g) * m2  # lcm
    return (x % l), l

def crt_many(offsets: List[int], moduli: List[int]) -> Tuple[int,int]:
    """
    Solve x ≡ offsets[i] (mod moduli[i]) for all i.
    Returns (x mod L, L) where L = lcm(moduli).
    Raises ValueError if inconsistent.
    """
    if not offsets:
        return (0, 1)
    x, m = offsets[0] % moduli[0], moduli[0]
    for a, n in zip(offsets[1:], moduli[1:]):
        x, m = crt_pair(x, m, a % n, n)
    return x, m

# core attack: offsets -> exps (via CRT)  
def recover_offset_on_cycle(C: Perm, cycle: Sequence[int]) -> int:
    start = cycle[0]
    dst = C[start]
    L = len(cycle)
    for e in range(L):
        if cycle[e] == dst:
            return e
    raise ValueError("destination not on provided cycle")

def exps_from_pub_and_cipher(pub_layers: List[Dict], cipher_layers: List[Perm], gen_order: Optional[List[str]]) -> List[int]:
    """
    For each generator on each layer:
      - enumerate all PUBLIC cycles of h
      - measure offset_i = shift that C induces on head of cycle_i
      - solve x ≡ offset_i (mod len_i) across all cycles_i via CRT
      - take representative x in [0, LCM-1] as the exponent value to feed into HKDF pipeline
    """
    if len(pub_layers) != len(cipher_layers):
        raise ValueError("Layer count mismatch")
    if gen_order is None:
        gen_order = list(pub_layers[0]["gens"].keys())

    all_exps: List[int] = []
    for Lidx, (Lpub, C) in enumerate(zip(pub_layers, cipher_layers)):
        gens: Dict[str, Perm] = {nm: tuple(p) for nm, p in Lpub["gens"].items()}
        for nm in gen_order:
            h = gens[nm]
            cycles = perm_to_cycles(h)
            if not cycles:
                e_val = 0
            else:
                offs = [recover_offset_on_cycle(C, cyc) for cyc in cycles]
                mods = [len(cyc) for cyc in cycles]
                # generalized CRT across all (offset, modulus) pairs
                e_val, L = crt_many(offs, mods)  # e_val is canonical in [0, L-1]
            all_exps.append(int(e_val))
    return all_exps

# unsalt: recover r from J=r^d 
def lcm_many(vals: List[int]) -> int:
    L = 1
    for v in vals:
        L = (L * v) // math.gcd(L, v)
    return L

def recover_r_from_Jd(J: Perm, d: int) -> Perm:
    cyc = perm_to_cycles(J)
    L = lcm_many([len(c) for c in cyc]) if cyc else 1
    d_inv = modinv(d % L, L)
    return pow_perm(J, d_inv)

def unsalt_cipher_layers(cipher_layers: List[Perm], salt_meta) -> List[Perm]:
    out = []
    for C, meta in zip(cipher_layers, salt_meta):
        J = tuple(meta["J"]); d = int(meta["d"])
        r = recover_r_from_Jd(J, d)
        out.append(compose(r, compose(C, inverse(r))))  # r C r^{-1}
    return out

# mixing mod M 
def mat_vec_mul_mod(A: List[List[int]], x: List[int], M: int) -> List[int]:
    n, m = len(A), len(A[0])
    assert m == len(x)
    out = [0]*n
    for i in range(n):
        s = 0
        Ai = A[i]
        for j in range(m):
            s = (s + (Ai[j] % M) * (x[j] % M)) % M
        out[i] = s
    return out

def hkdf_key_from_exponents(exps: List[int], info: bytes, key_len: int = 32) -> bytes:
    raw = bytes(exps)
    hkdf = HKDF(algorithm=hashes.SHA256(), length=key_len, salt=None, info=info)
    return hkdf.derive(raw)

def aead_open(key: bytes, blob: dict, aad: bytes) -> bytes:
    nonce = base64.b64decode(blob["nonce"])
    ct = base64.b64decode(blob["ct"])
    return AESGCM(key).decrypt(nonce, ct, aad)

def solve(handout_path: str) -> str:
    H = json.load(open(handout_path, "r"))
    pub_layers = H["pub"]["layers"]
    gen_order = H["kem"].get("gen_order")
    cipher_layers = [tuple(p) for p in H["kem"]["cipher"]]
    kem_info = H["kem"].get("kem_info", "Rubik-KEM-v2")
    params = H.get("params", {})

    # 1) unsalt if present
    salt_meta = params.get("salt")
    if salt_meta:
        cipher_layers = unsalt_cipher_layers(cipher_layers, salt_meta)

    # 2) exps from public cycles (with CRT)
    exps = exps_from_pub_and_cipher(pub_layers, cipher_layers, gen_order)

    # 3) mixing if present
    mix = params.get("mix")
    if mix:
        M = int(mix["M"])
        A = mix["A"]
        exps = mat_vec_mul_mod(A, exps, M)
        info = b"Rubik-KEM-v2"
    else:
        info = b"Rubik-KEM-v2"

    # 4) derive key and open
    key = hkdf_key_from_exponents(exps, info=info)
    pt = aead_open(key, H["sealed_flag"], aad=b"Rubik-CTF-v2")
    try:
        return pt.decode("utf-8")
    except UnicodeDecodeError:
        import base64
        return base64.b64encode(pt).decode()

def main():
    ap = argparse.ArgumentParser(description="Solve Rubik-ish KEM hard-mode handout (public-only, CRT-aware)")
    ap.add_argument("handout", help="handout.json")
    args = ap.parse_args()
    flag = solve(args.handout)
    print(flag)

if __name__ == "__main__":
    main()
