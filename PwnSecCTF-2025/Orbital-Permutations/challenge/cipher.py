#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rubik-ish KEM/DEM with 5x5 LAYER MOVES.
  - Adds full 5x5 layer moves per face: U,u,U',u',Uu,Uu' and the same for D/d, R/r, L/l, F/f, B/b.
    - U   = outer ring (perimeter of 5x5) clockwise
    - u   = inner ring (perimeter of 3x3) clockwise
    - Uu  = wide turn: outer+inner clockwise (composition)
    - primes (') are inverses
    - Implemented *face-local* so orders are deterministic (outer=24, inner=8).
  - SALT (publish J=r^d) + MIX (A·e mod M) + HKDF(info="Rubik-KEM-v2").
Essential commands:
  handout    -> build hard-mode handout.json (public) + author_key.json (private)
  keygen     -> just write keys for QA
  encapsulate/decapsulate -> KEM round-trip (QA)
  seal/open  -> DEM using KEM (QA)
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import os
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple, Sequence, Optional

# ───────────────────────── types ───────────────────────── #
Perm = Tuple[int, ...]
GenMap = Dict[str, Perm]

@dataclass
class LayerPub:
    gens: GenMap
    meta: Dict

@dataclass
class LayerPriv:
    k: Perm
    base: GenMap
    meta: Dict

@dataclass
class PublicKey:
    layers: List[LayerPub]

@dataclass
class PrivateKey:
    layers: List[LayerPriv]

Cipher = List[Perm]

# ────────────────────── permutation helpers ────────────────────── #
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

def cycle_to_perm(n: int, cycle: Sequence[int]) -> Perm:
    out = list(range(n))
    L = len(cycle)
    for i in range(L):
        out[cycle[i]] = cycle[(i+1) % L]
    return tuple(out)

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
        t, nt = nt, t - q*nt
        r, nr = nr, r - q*nr
    if r != 1:
        raise ValueError("no inverse")
    return t % m

# ───────────────────── 5×5 face + layer ring helpers ───────────────────── #
def face_index(face: int, r: int, c: int, face_size: int = 5) -> int:
    """Map (face, row, col) to linear index inside a *face-local* block [0..face_size^2-1] (we’ll rebase per replica)."""
    return face * (face_size*face_size) + r*face_size + c

def ring_positions_on_face(face_size: int, ring: int) -> List[Tuple[int,int]]:
    """
    Return (r,c) perimeter coordinates for a given ring:
      ring=0 -> outer perimeter of the 5x5 (length 24)
      ring=1 -> perimeter of the inner 3x3 (length 8)
    """
    if ring not in (0,1):
        raise ValueError("ring must be 0 (outer) or 1 (inner)")
    n = face_size - 2*ring
    offset = ring
    if n <= 1:
        return []
    coords = []
    # top row
    for c in range(offset, offset+n):
        coords.append((offset, c))
    # right col (skip top)
    for r in range(offset+1, offset+n-1):
        coords.append((r, offset+n-1))
    # bottom row (reverse)
    if n > 1:
        for c in range(offset+n-1, offset-1, -1):
            coords.append((offset+n-1, c))
    # left col (skip top/bottom)
    for r in range(offset+n-2, offset, -1):
        coords.append((r, offset))
    # remove duplicates for 2× n perimeter logic
    # ensure unique cycle ordering (outer: 24, inner: 8)
    uniq = []
    seen = set()
    for rc in coords:
        if rc not in seen:
            seen.add(rc)
            uniq.append(rc)
    return uniq

def face_ring_cycle(face_idx: int, ring: int, face_size: int = 5) -> List[int]:
    """Return the cycle (list of linear indices) for rotating that ring clockwise."""
    coords = ring_positions_on_face(face_size, ring)
    idxs = [face_index(0, r, c, face_size) for (r,c) in coords]  # face-local indices 0..24
    # We construct in a *face-local* block; later we transport to global by replica base mapping.
    return idxs

def unit_moves_5x5_layers(face_size: int = 5) -> Dict[str, List[List[int]]]:
    """
    Build canonical *face-local* cycles for all faces, for moves:
       X (outer ring), x (inner ring), Xx (outer+inner),
    where X in {U,D,R,L,F,B}. Return a dict mapping move name -> list of cycles in a *single face-local* block.
    We later convert to permutations globally by remapping indices into disjoint replica blocks.
    """
    # Build cycles for a single face-local block of 25 indices (0..24), where
    # outer ring perimeter length = 24, inner ring perimeter length = 8.
    # For each face label, the cycles are the same (just names differ).
    faces = ["U","D","R","L","F","B"]
    moves: Dict[str, List[List[int]]] = {}
    outer = face_ring_cycle(face_idx=0, ring=0, face_size=face_size)  # 24
    inner = face_ring_cycle(face_idx=0, ring=1, face_size=face_size)  # 8

    def cycles_to_perm_in_block(cycles: List[List[int]], block_size: int) -> Perm:
        p = list(range(block_size))
        for cyc in cycles:
            # rotate clockwise: shift successor
            L = len(cyc)
            for i in range(L):
                p[cyc[i]] = cyc[(i+1) % L]
        return tuple(p)

    block_size = face_size * face_size
    perm_outer = cycles_to_perm_in_block([outer], block_size)
    perm_inner = cycles_to_perm_in_block([inner], block_size)
    perm_both  = compose(perm_outer, perm_inner)  # do inner then outer (both rings rotate)

    # Provide names across all 6 faces
    for X in faces:
        # In our face-local semantics, U and D etc. share the same ring behavior in the block.
        moves[X]   = [outer]             # outer ring
        moves[X+"'"]= [list(reversed(outer))]  # prime will be handled via inverse later; keep structure only
        moves[X.lower()] = [inner]       # inner ring (lowercase letter)
        moves[X.lower()+"'"] = [list(reversed(inner))]
        moves[X+X.lower()] = [outer, inner]    # wide turn cycles
        moves[X+X.lower()+"'"] = [list(reversed(outer)), list(reversed(inner))]

    return moves

# ───────────────────── rubik-hybrid generator (replicas) ───────────────────── #
def make_rubik_layer_generators(
    n: int,
    gen_names: List[str],
    replicas_per_gen: int = 1,
    seed: Optional[int] = None,
    face_size: int = 5,
) -> Tuple[GenMap, Dict]:
    """
    Create disjoint *replicas* of face-local 5x5 layer moves for the requested gen_names.
    Each replica is a block of size face_size^2 (=25). We concatenate enough blocks into the global n-space.

    Constraints:
      n must be >= 25 * replicas_per_gen * len(gen_names)
    """
    unit_n = face_size * face_size  # 25
    need = unit_n * replicas_per_gen * len(gen_names)
    if n < need:
        raise ValueError(f"n too small for layer generators: need >= {need}, got {n}")
    rng = random.Random(seed) if seed is not None else random.SystemRandom()

    # Prepare cycles in a face-local block
    face_cycles = unit_moves_5x5_layers(face_size=face_size)  # name -> [cycles (face-local indices)]
    # Create available global indices
    available = list(range(n))
    rng.shuffle(available)

    gen_map: GenMap = {}
    meta = {"mode": "rubik-5x5-layers", "unit_n": unit_n, "replicas_per_gen": replicas_per_gen, "supports": {}, "orders": {}}

    for name in gen_names:
        if name not in face_cycles:
            raise ValueError(f"Unknown generator name '{name}' for 5x5 layers")
        local_cycles = face_cycles[name]  # list of cycles (face-local indices)
        # Build global permutation by placing `replicas_per_gen` disjoint blocks
        perm_global = identity(n)
        blocks = []
        for _ in range(replicas_per_gen):
            base = available[:unit_n]
            del available[:unit_n]
            # Construct a permutation p where for each local cycle [i0,i1,...] we map base[i_k] -> base[i_{k+1}]
            p = list(range(n))
            for cyc in local_cycles:
                L = len(cyc)
                for k in range(L):
                    p[base[cyc[k]]] = base[cyc[(k+1) % L]]
            perm_global = compose(tuple(p), perm_global)

            # record global cycles
            gcycles = []
            for cyc in local_cycles:
                gcycles.append([base[i] for i in cyc])
            blocks.append({"base": base, "cycles": gcycles})

        gen_map[name] = perm_global
        # metadata: supports & order (LCM of cycle lengths of local cycles)
        supports = []
        for b in blocks:
            supports.extend(b["cycles"])
        meta["supports"][name] = supports

        # order of a move equals LCM of its cycle lengths
        orders = 1
        for cyc in local_cycles:
            orders = (orders * len(cyc)) // math.gcd(orders, len(cyc))
        meta["orders"][name] = orders

    return gen_map, meta

# ─────────────────────────── keygen (layers=5) ─────────────────────────── #
@dataclass
class LayerPrivOut:
    k: Perm
    base: GenMap
    s_map: Dict[str,int]
    meta: Dict

def keygen_layers(
    layers: int = 5,
    replicas_per_gen: int = 1,
    seed: Optional[int] = None,
) -> Tuple[PrivateKey, PublicKey, int, List[str]]:
    """
    5 layers by default; each layer has disjoint replicas of 5x5 layer moves per face & ring:
      names = [U,u,Uu,D,d,Dd,R,r,Rr,L,l,Ll,F,f,Ff,B,b,Bb] with prime versions implicit via inverses
    (we explicitly publish only the clockwise set; primes are available through pow_perm(...,-1) if needed)
    """
    face_size = 5
    unit_n = face_size * face_size
    # Define generator names we’ll actually publish (clockwise set). We include both outer (X), inner (x), and wide (Xx).
    base_names = []
    for X in ["U","D","R","L","F","B"]:
        base_names.extend([X, X.lower(), X+X.lower()])
    gen_names = base_names[:]  # publish these as clockwise generators

    # total size per generator replica set
    size = unit_n * replicas_per_gen * len(gen_names)

    priv_layers: List[LayerPriv] = []
    pub_layers: List[LayerPub] = []

    for ell in range(layers):
        base, meta = make_rubik_layer_generators(
            n=size,
            gen_names=gen_names,
            replicas_per_gen=replicas_per_gen,
            seed=None if seed is None else (seed + 1000*ell + 7),
            face_size=face_size,
        )
        order_map = meta.get("orders", {})
        s_map: Dict[str,int] = {}
        rng = random.Random(None if seed is None else (seed + 5000*ell + 11))
        for nm in base.keys():
            ord_g = order_map.get(nm, 1)
            cop = [x for x in range(1, ord_g) if math.gcd(x, ord_g) == 1] or [1]
            s_map[nm] = int(rng.choice(cop))

        # random conjugator for the layer (key)
        rng_k = random.Random(None if seed is None else (seed + 1000*ell + 999))
        k_list = list(range(size))
        rng_k.shuffle(k_list)
        k = tuple(k_list)
        kinv = inverse(k)

        pub_gens = {}
        for nm, g in base.items():
            s = s_map[nm]
            g_s = pow_perm(g, s)
            pub_gens[nm] = compose(k, compose(g_s, kinv))

        priv_meta = dict(meta)
        priv_meta["orders"] = order_map
        priv_meta["s_map"] = s_map

        priv_layers.append(LayerPriv(k=k, base=base, meta=priv_meta))
        pub_layers.append(LayerPub(gens=pub_gens, meta={"orders": order_map, "supports": meta["supports"]}))

    return PrivateKey(priv_layers), PublicKey(pub_layers), size, gen_names

# ─────────────────────────── KEM encapsulation ─────────────────────────── #
def encapsulate(pub: PublicKey) -> Tuple[Cipher, List[int]]:
    names = list(pub.layers[0].gens.keys())
    orders = pub.layers[0].meta.get("orders", {})
    exps: List[int] = []
    cipher: List[Perm] = []
    for L in pub.layers:
        n = len(next(iter(L.gens.values())))
        P = identity(n)
        for nm in names:
            ord_nm = orders.get(nm, 24)  # outer ring default order
            e = os.urandom(1)[0] % ord_nm
            exps.append(e)
            if e:
                P = compose(pow_perm(L.gens[nm], e), P)
        cipher.append(P)
    return cipher, exps

# ─────────────────────────── KDF + AEAD ─────────────────────────── #
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def hkdf_key_from_exponents(exps: List[int], info: bytes, key_len: int = 32) -> bytes:
    raw = bytes(exps)
    hkdf = HKDF(algorithm=hashes.SHA256(), length=key_len, salt=None, info=info)
    return hkdf.derive(raw)

def aead_seal(key: bytes, plaintext: bytes, aad: bytes = b"") -> dict:
    nonce = os.urandom(12)
    aead = AESGCM(key)
    ct = aead.encrypt(nonce, plaintext, aad)
    return {"nonce": base64.b64encode(nonce).decode(), "ct": base64.b64encode(ct).decode()}

def aead_open(key: bytes, blob: dict, aad: bytes = b"") -> bytes:
    nonce = base64.b64decode(blob["nonce"])
    ct = base64.b64decode(blob["ct"])
    return AESGCM(key).decrypt(nonce, ct, aad)

# ─────────────────────────── serialization ─────────────────────────── #
def serialize_cipher(cipher: Cipher) -> List[List[int]]:
    return [list(p) for p in cipher]

def deserialize_cipher(obj) -> Cipher:
    return [tuple(p) for p in obj]

# ─────────────────────────── hard-mode utils ─────────────────────────── #
def _lcm_many(vals: List[int]) -> int:
    L = 1
    for v in vals:
        L = (L * v) // math.gcd(L, v)
    return L

def _mat_eye(n: int) -> List[List[int]]:
    return [[1 if i==j else 0 for j in range(n)] for i in range(n)]

def _mat_inv_mod(A: List[List[int]], mod: int) -> List[List[int]]:
    n = len(A)
    M = [row[:] + eye for row, eye in zip(A, _mat_eye(n))]
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
        for j in range(2*n):
            M[r][j] = (M[r][j] * inva) % mod
        for i in range(n):
            if i == r: continue
            f = M[i][c] % mod
            if f == 0: continue
            for j in range(2*n):
                M[i][j] = (M[i][j] - f * M[r][j]) % mod
        r += 1
        if r == n: break
    return [row[n:] for row in M]

def _random_invertible_matrix_mod(n: int, mod: int, seed: Optional[int]) -> List[List[int]]:
    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    while True:
        A = [[rng.randrange(mod) for _ in range(n)] for __ in range(n)]
        for i in range(n):
            if math.gcd(A[i][i], mod) != 1:
                A[i][i] = (A[i][i] | 1)
        try:
            _ = _mat_inv_mod([row[:] for row in A], mod)
            return A
        except Exception:
            continue

def _mat_vec_mul_mod(A: List[List[int]], x: List[int], mod: int) -> List[int]:
    n, m = len(A), len(A[0])
    assert m == len(x)
    out = [0]*n
    for i in range(n):
        s = 0
        Ai = A[i]
        for j in range(m):
            s = (s + (Ai[j] % mod) * (x[j] % mod)) % mod
        out[i] = s
    return out

def _random_perm(n: int, rng: random.Random) -> Perm:
    arr = list(range(n))
    rng.shuffle(arr)
    return tuple(arr)

def _salt_layer_cipher(C: Perm, r: Perm) -> Perm:
    return compose(inverse(r), compose(C, r))  # r^{-1} C r

def recover_r_from_Jd(J: Perm, d: int) -> Perm:
    cyc = perm_to_cycles(J)
    L = _lcm_many([len(c) for c in cyc]) if cyc else 1
    d_inv = modinv(d % L, L)
    return pow_perm(J, d_inv)

# ─────────────────────────── core ops ─────────────────────────── #
def build_hardmode_handout(flag: str, out_pub: str, out_priv: str, seed: Optional[int]) -> None:
    # 1) Keys
    priv, pub, n, gen_order = keygen_layers(layers=5, replicas_per_gen=1, seed=seed)

    # 2) Encapsulate -> raw exps
    cipher, exps = encapsulate(pub)

    # 3) SALT each layer with random r; publish J=r^d and d
    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    salted_cipher = []
    salt_meta = []
    for C, L in zip(cipher, pub.layers):
        r = _random_perm(n, rng)
        ord_r = perm_order(r)
        while True:
            d = rng.randrange(2, max(5, 2*ord_r))
            if math.gcd(d, ord_r) == 1:
                break
        J = pow_perm(r, d)
        salted_cipher.append(_salt_layer_cipher(C, r))
        salt_meta.append({"d": int(d), "J": list(J)})

    # 4) MIX exps for HKDF: compute M = lcm of generator orders across layers
    orders = []
    for L in pub.layers:
        om = L.meta.get("orders", {})
        for nm in gen_order:
            orders.append(int(om.get(nm, 24)))
    M = _lcm_many(orders) if orders else 1
    A = _random_invertible_matrix_mod(len(exps), M, seed=(None if seed is None else seed+4242))
    e_prime = _mat_vec_mul_mod(A, exps, M)

    # 5) KDF + GCM
    kem_info = b"Rubik-KEM-v2"
    key = hkdf_key_from_exponents(e_prime, info=kem_info)
    aead = aead_seal(key, flag.encode("utf-8"), aad=b"Rubik-CTF-v2")

    # 6) Public handout
    handout = {
        "pub": {
            "layers": [{
                "gens": {nm: list(p) for nm,p in L.gens.items()},
                "meta": L.meta
            } for L in pub.layers]
        },
        "kem": {
            "cipher": serialize_cipher(salted_cipher),
            "layers": len(salted_cipher),
            "gen_order": gen_order,
            "kem_info": "Rubik-KEM-v2"
        },
        "sealed_flag": aead,
        "params": {
            "layers": len(pub.layers),
            "rubik_5x5_layers": True,
            "mix": {"M": int(M), "A": A},
            "salt": salt_meta
        },
        "hint": "Unsalt via r from J=r^d; read e from public cycles; e' = A*e mod M; HKDF(info='Rubik-KEM-v2')."
    }
    with open(out_pub, "w") as f:
        json.dump(handout, f)

    # 7) Private author copy
    data_priv = {
        "priv": [{
            "k": list(L.k),
            "base": {nm: list(p) for nm,p in L.base.items()},
            "meta": L.meta
        } for L in priv.layers],
        "pub": [{
            "gens": {nm: list(p) for nm,p in L.gens.items()},
            "meta": L.meta
        } for L in pub.layers]
    }
    with open(out_priv, "w") as f:
        json.dump(data_priv, f)

def write_keys(out_priv: str, out_pub: str, seed: Optional[int]) -> None:
    priv, pub, _, _ = keygen_layers(layers=5, replicas_per_gen=1, seed=seed)
    data_priv = {
        "priv": [{
            "k": list(L.k),
            "base": {nm: list(p) for nm,p in L.base.items()},
            "meta": L.meta
        } for L in priv.layers],
        "pub": [{
            "gens": {nm: list(p) for nm,p in L.gens.items()},
            "meta": L.meta
        } for L in pub.layers]
    }
    with open(out_priv, "w") as f:
        json.dump(data_priv, f)
    with open(out_pub, "w") as f:
        json.dump({"layers": [{
            "gens": {nm: list(p) for nm,p in L.gens.items()},
            "meta": L.meta
        } for L in pub.layers]}, f)

def cmd_encapsulate(in_pub: str, out_kem: str) -> None:
    pubdata = json.load(open(in_pub, "r"))
    # accept either {"layers":[...]} or {"pub":[...]}
    if "layers" in pubdata:
        layers = [LayerPub(gens={nm: tuple(p) for nm,p in L["gens"].items()}, meta=L.get("meta", {}))
                  for L in pubdata["layers"]]
    else:
        layers = [LayerPub(gens={nm: tuple(p) for nm,p in L["gens"].items()}, meta=L.get("meta", {}))
                  for L in pubdata["pub"]]
    pub = PublicKey(layers=layers)
    cipher, exps = encapsulate(pub)
    out = {"cipher": serialize_cipher(cipher),
           "layers": len(cipher),
           "gen_order": list(pub.layers[0].gens.keys()),
           "kem_info": "Rubik-KEM-v2"}
    with open(out_kem, "w") as f:
        json.dump(out, f)

def cmd_decapsulate(in_priv: str, in_kem: str) -> None:
    privdata = json.load(open(in_priv, "r"))
    layers = []
    for L in privdata["priv"]:
        layers.append(LayerPriv(k=tuple(L["k"]), base={nm: tuple(p) for nm,p in L["base"].items()}, meta=L["meta"]))
    priv = PrivateKey(layers=layers)
    blob = json.load(open(in_kem, "r"))
    cipher = deserialize_cipher(blob["cipher"])
    # decapsulation requires private supports & s_map; this demo leaves it out (use solver for handouts)
    print("[!] decapsulate: use public-only solver on handout, or implement private decap as in your original.")
    # (omitted for brevity)

def cmd_seal(in_pub: str, message: Optional[str], infile: Optional[str], out_file: str) -> None:
    pubdata = json.load(open(in_pub, "r"))
    layers = [LayerPub(gens={nm: tuple(p) for nm,p in L["gens"].items()}, meta=L.get("meta", {}))
              for L in (pubdata["pub"] if "pub" in pubdata else pubdata["layers"])]
    pub = PublicKey(layers=layers)
    cipher, exps = encapsulate(pub)
    key = hkdf_key_from_exponents(exps, info=b"Rubik-KEM-v2")
    if infile and infile != "-":
        pt = open(infile, "rb").read()
    else:
        pt = (message or "").encode("utf-8")
    aead_blob = aead_seal(key, pt, aad=b"Rubik-Hybrid-v2")
    out = {"cipher": serialize_cipher(cipher), "aead": aead_blob,
           "params": {"layers": len(cipher), "gen_order": list(pub.layers[0].gens.keys())}}
    with open(out_file, "w") as f:
        json.dump(out, f)

def cmd_open(in_priv: str, sealedfile: str, outfile: Optional[str]) -> None:
    print("[!] open: for public handouts use the solver; this is kept for parity and is not the CTF path.")
    # left intentionally minimal

# ─────────────────────────── CLI (trimmed) ─────────────────────────── #
def build_cli():
    ap = argparse.ArgumentParser(description="Refactored Rubik-ish KEM/DEM (5x5 layer moves), hard-mode handouts")
    sub = ap.add_subparsers(dest="cmd", required=True)

    h = sub.add_parser("handout", help="Generate hard-mode public handout + author key")
    h.add_argument("--flag", required=True, help="Flag string to encrypt (e.g., crypto{...})")
    h.add_argument("--out", default="handout.json")
    h.add_argument("--priv", default="author_key.json")
    h.add_argument("--seed", type=int, default=None)
    h.set_defaults(func=lambda args: build_hardmode_handout(args.flag, args.out, args.priv, args.seed))

    kg = sub.add_parser("keygen", help="Write author/private key + public key (QA)")
    kg.add_argument("--out-priv", default="author_key.json")
    kg.add_argument("--out-pub", default="pub.json")
    kg.add_argument("--seed", type=int, default=None)
    kg.set_defaults(func=lambda args: write_keys(args.out_priv, args.out_pub, args.seed))

    enc = sub.add_parser("encapsulate", help="Encapsulate using a public key file (QA)")
    enc.add_argument("pubfile")
    enc.add_argument("--out", default="kem.json")
    enc.set_defaults(func=lambda args: cmd_encapsulate(args.pubfile, args.out))

    dec = sub.add_parser("decapsulate", help="(QA stub) Decapsulate using a private key + kem.json")
    dec.add_argument("privfile"); dec.add_argument("kemfile")
    dec.set_defaults(func=lambda args: cmd_decapsulate(args.privfile, args.kemfile))

    sl = sub.add_parser("seal", help="Seal a message/file using a public key (QA)")
    sl.add_argument("pubfile")
    g = sl.add_mutually_exclusive_group(required=True)
    g.add_argument("--message")
    g.add_argument("--infile")
    sl.add_argument("--out", default="sealed.json")
    sl.set_defaults(func=lambda args: cmd_seal(args.pubfile, args.message, args.infile, args.out))

    opn = sub.add_parser("open", help="(QA stub) Open a sealed.json using a private key")
    opn.add_argument("privfile"); opn.add_argument("sealedfile")
    opn.add_argument("--outfile")
    opn.set_defaults(func=lambda args: cmd_open(args.privfile, args.sealedfile, args.outfile))

    return ap

def main():
    ap = build_cli()
    args = ap.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
