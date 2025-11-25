#!/usr/bin/python3
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Sequence, Optional
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
class LayerPrivOut:
    k: Perm
    base: GenMap
    s_map: Dict[str,int]
    meta: Dict

@dataclass
class PublicKey:
    layers: List[LayerPub]

@dataclass
class PrivateKey:
    layers: List[LayerPriv]

Cipher = List[Perm]
