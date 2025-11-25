from __future__ import annotations
import json
import math
import os
import random
from typing import Optional, List, Dict
from rbktypes import Perm, LayerPub, LayerPriv, PublicKey, PrivateKey
from perms import compose, inverse, perm_order, pow_perm
from keygen import keygen_layers
from kem import encapsulate, hkdf_key_from_exponents, aead_seal, aead_open, serialize_cipher, deserialize_cipher
from modlinalg import lcm_many as _lcm_many, random_invertible_matrix_mod as _random_invertible_matrix_mod, mat_vec_mul_mod as _mat_vec_mul_mod
from salt import random_perm as _random_perm, salt_layer_cipher as _salt_layer_cipher


def create_handout(flag: str, out_pub: str, out_priv: str,seed: Optional[int]) -> None:
    priv, pub, n, gen_order = keygen_layers(layers=5, replicas_per_gen=1, seed=seed)
    cipher, exps = encapsulate(pub)
    rng = random.SystemRandom()
    salted_cipher = []
    salt_meta = []
    for C, L in zip(cipher, pub.layers):
        r = _random_perm(n, rng)
        ord_r = perm_order(r)
        while True:
            d = rng.randrange(2, max(5, 2 * ord_r))
            if math.gcd(d, ord_r) == 1:
                break
        J = pow_perm(r, d)
        salted_cipher.append(_salt_layer_cipher(C, r))
        salt_meta.append({"d": int(d), "J": list(J)})

    orders: List[int] = []
    for L in pub.layers:
        om = L.meta.get("orders", {})
        for nm in gen_order:
            orders.append(int(om.get(nm, 24)))
    M = _lcm_many(orders) if orders else 1
    A = _random_invertible_matrix_mod(len(exps), M, seed=(None if seed is None else seed + 4242))
    e_prime = _mat_vec_mul_mod(A, exps, M)
    kem_info = b"Rubik-KEM-v2"
    key = hkdf_key_from_exponents(e_prime, info=kem_info)
    aead = aead_seal(key, flag.encode("utf-8"), aad=b"Rubik-CTF-v2")

    handout = {
        "pub": {
            "layers": [{
                "gens": {nm: list(p) for nm, p in L.gens.items()},
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

    data_priv = {
        "priv": [{
            "k": list(L.k),
            "base": {nm: list(p) for nm, p in L.base.items()},
            "meta": L.meta
        } for L in priv.layers],
        "pub": [{
            "gens": {nm: list(p) for nm, p in L.gens.items()},
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
            "base": {nm: list(p) for nm, p in L.base.items()},
            "meta": L.meta
        } for L in priv.layers],
        "pub": [{
            "gens": {nm: list(p) for nm, p in L.gens.items()},
            "meta": L.meta
        } for L in pub.layers]
    }
    with open(out_priv, "w") as f:
        json.dump(data_priv, f)
    with open(out_pub, "w") as f:
        json.dump({"layers": [{
            "gens": {nm: list(p) for nm, p in L.gens.items()},
            "meta": L.meta
        } for L in pub.layers]}, f)

def cmd_encapsulate(in_pub: str, out_kem: str) -> None:
    pubdata = json.load(open(in_pub, "r"))
    if "layers" in pubdata:
        layers = [LayerPub(gens={nm: tuple(p) for nm, p in L["gens"].items()}, meta=L.get("meta", {}))
                  for L in pubdata["layers"]]
    else:
        layers = [LayerPub(gens={nm: tuple(p) for nm, p in L["gens"].items()}, meta=L.get("meta", {}))
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
    layers: List[LayerPriv] = []
    for L in privdata["priv"]:
        layers.append(LayerPriv(k=tuple(L["k"]), base={nm: tuple(p) for nm, p in L["base"].items()}, meta=L["meta"]))
    priv = PrivateKey(layers=layers)  # noqa: F841
    blob = json.load(open(in_kem, "r"))
    cipher = deserialize_cipher(blob["cipher"])  # noqa: F841
    print("[!] decapsulate: use public-only solver on handout, or implement private decap as in your original.")

def cmd_seal(in_pub: str, message: Optional[str], infile: Optional[str], out_file: str) -> None:
    pubdata = json.load(open(in_pub, "r"))
    layers = [LayerPub(gens={nm: tuple(p) for nm, p in L["gens"].items()}, meta=L.get("meta", {}))
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
    raise NotImplementedError("This is for you to do!!!")

