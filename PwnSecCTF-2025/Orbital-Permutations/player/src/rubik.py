#!/usr/bin/python3
from __future__ import annotations
from typing import Dict, List, Tuple, Sequence
from rbktypes import Perm
from perms import compose

def face_index(face: int, r: int, c: int, face_size: int = 5) -> int:
    return face * (face_size * face_size) + r * face_size + c

def ring_positions_on_face(face_size: int, ring: int) -> List[Tuple[int, int]]:
    if ring not in (0, 1):
        raise ValueError("ring must be 0 (outer) or 1 (inner)")
    n = face_size - 2 * ring
    offset = ring
    if n <= 1:
        return []
    coords: List[Tuple[int, int]] = []

    for c in range(offset, offset + n):
        coords.append((offset, c))

    for r in range(offset + 1, offset + n - 1):
        coords.append((r, offset + n - 1))

    if n > 1:
        for c in range(offset + n - 1, offset - 1, -1):
            coords.append((offset + n - 1, c))

    for r in range(offset + n - 2, offset, -1):
        coords.append((r, offset))
    uniq: List[Tuple[int, int]] = []
    seen = set()
    for rc in coords:
        if rc not in seen:
            seen.add(rc)
            uniq.append(rc)
    return uniq

def face_ring_cycle(face_idx: int, ring: int, face_size: int = 5) -> List[int]:
    """Return the cycle (list of linear indices) for rotating that ring clockwise."""
    coords = ring_positions_on_face(face_size, ring)
    idxs = [face_index(0, r, c, face_size) for (r, c) in coords]
    return idxs

def unit_moves_5x5_layers(face_size: int = 5) -> Dict[str, List[List[int]]]:
    """
    Build the per-face ring "unit" cycles for a 5x5 face block (25 local indices).
    Returns cycles (not permutations) to be mapped into global permutations by keygen.
    """
    faces = ["U", "D", "R", "L", "F", "B"]
    moves: Dict[str, List[List[int]]] = {}
    outer = face_ring_cycle(face_idx=0, ring=0, face_size=face_size)  # length 24
    inner = face_ring_cycle(face_idx=0, ring=1, face_size=face_size)  # length 8

    def cycles_to_perm_in_block(cycles: List[List[int]], block_size: int) -> Perm:
        p = list(range(block_size))
        for cyc in cycles:
            L = len(cyc)
            for i in range(L):
                p[cyc[i]] = cyc[(i + 1) % L]
        return tuple(p)

    block_size = face_size * face_size
    perm_outer = cycles_to_perm_in_block([outer], block_size)
    perm_inner = cycles_to_perm_in_block([inner], block_size)
    perm_both = compose(perm_outer, perm_inner)  

    for X in faces:
        moves[X] = [outer]
        moves[X + "'"] = [list(reversed(outer))]
        moves[X.lower()] = [inner]
        moves[X.lower() + "'"] = [list(reversed(inner))]
        moves[X + X.lower()] = [outer, inner]
        moves[X + X.lower() + "'"] = [list(reversed(outer)), list(reversed(inner))]

    return moves