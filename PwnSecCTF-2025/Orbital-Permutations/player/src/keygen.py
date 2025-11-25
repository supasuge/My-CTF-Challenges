#!/usr/bin/python3
from __future__ import annotations
import math
import random
from typing import Dict, List, Tuple, Optional
from rbktypes import Perm, GenMap, LayerPub, LayerPriv, PublicKey, PrivateKey
from perms import identity, compose, inverse, pow_perm
from rubik import unit_moves_5x5_layers

def _makeGen(
    n: int,
    gen_names: List[str],
    replicas_per_gen: int = 1,
    seed: Optional[int] = None,
    face_size: int = 5,
) -> Tuple[GenMap, Dict]:
    """
    Constraints:
      n must be >= 25 * replicas_per_gen * len(gen_names)
    """
    unit_n = face_size * face_size  # 25
    need = unit_n * replicas_per_gen * len(gen_names)
    if n < need:
        raise ValueError(f"n too small for layer generators: need >= {need}, got {n}")

    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    face_cycles = unit_moves_5x5_layers(face_size=face_size)  # cycles (not perms)
    available = list(range(n))
    rng.shuffle(available)

    gen_map: GenMap = {}
    meta = {
        "mode": "rubik-5x5-layers",
        "unit_n": unit_n,
        "replicas_per_gen": replicas_per_gen,
        "supports": {},
        "orders": {},
    }

    for name in gen_names:
        if name not in face_cycles:
            raise ValueError(f"Unknown generator name '{name}' for 5x5 layers")
        local_cycles = face_cycles[name]  # list of cycles

        perm_global = identity(n)
        blocks = []
        for _ in range(replicas_per_gen):
            base = available[:unit_n]
            del available[:unit_n]
            p = list(range(n))
            for cyc in local_cycles:
                L = len(cyc)
                for k in range(L):
                    p[base[cyc[k]]] = base[cyc[(k + 1) % L]]
            perm_global = compose(tuple(p), perm_global)
            gcycles = []
            for cyc in local_cycles:
                gcycles.append([base[i] for i in cyc])
            blocks.append({"base": base, "cycles": gcycles})

        gen_map[name] = perm_global
        supports = []
        for b in blocks:
            supports.extend(b["cycles"])
        meta["supports"][name] = supports
        orders = 1
        for cyc in local_cycles:
            orders = (orders * len(cyc)) // math.gcd(orders, len(cyc))
        meta["orders"][name] = orders

    return gen_map, meta


def keygen_layers(
    layers: int = 5,
    replicas_per_gen: int = 1,
    seed: Optional[int] = None,
) -> Tuple[PrivateKey, PublicKey, int, List[str]]:
    face_size = 5
    unit_n = face_size * face_size
    base_names: List[str] = []
    for X in ["U", "D", "R", "L", "F", "B"]:
        base_names.extend([X, X.lower(), X + X.lower()])
    gen_names = base_names[:]
    size = unit_n * replicas_per_gen * len(gen_names)

    priv_layers: List[LayerPriv] = []
    pub_layers: List[LayerPub] = []

    for ell in range(layers):
        base, meta = _makeGen(
            n=size,
            gen_names=gen_names,
            replicas_per_gen=replicas_per_gen,
            seed=None if seed is None else (seed + 1000 * ell + 7),
            face_size=face_size,
        )
        order_map = meta.get("orders", {})
        s_map: Dict[str, int] = {}
        rng = random.Random(None if seed is None else (seed + 5000 * ell + 11))
        for nm in base.keys():
            ord_g = order_map.get(nm, 1)
            cop = [x for x in range(1, ord_g) if math.gcd(x, ord_g) == 1] or [1]
            s_map[nm] = int(rng.choice(cop))
        rng_k = random.Random(None if seed is None else (seed + 1000 * ell + 999))
        k_list = list(range(size))
        rng_k.shuffle(k_list)
        k = tuple(k_list)
        kinv = inverse(k)
        pub_gens: GenMap = {}
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