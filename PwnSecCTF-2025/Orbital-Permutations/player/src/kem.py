#!/usr/bin/python3
from __future__ import annotations
import base64
import os
from typing import List, Tuple, Dict
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from rbktypes import Perm, Cipher, PublicKey, PrivateKey
from perms import compose, inverse, identity, pow_perm

def encapsulate(pub: PublicKey) -> Tuple[Cipher, List[int]]:
    names = list(pub.layers[0].gens.keys())
    orders = pub.layers[0].meta.get("orders", {})
    exps: List[int] = []
    cipher: List[Perm] = []
    for L in pub.layers:
        n = len(next(iter(L.gens.values())))
        P = identity(n)
        for nm in names:
            ord_nm = orders.get(nm, 24)  # default retained
            e = os.urandom(1)[0] % ord_nm
            exps.append(e)
            if e:
                P = compose(pow_perm(L.gens[nm], e), P)
        cipher.append(P)
    return cipher, exps

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

def serialize_cipher(cipher: Cipher) -> List[List[int]]:
    return [list(p) for p in cipher]

def deserialize_cipher(obj) -> Cipher:
    return [tuple(p) for p in obj]
