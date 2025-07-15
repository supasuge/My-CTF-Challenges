#!/usr/bin/env sage -python
# Author: supasuge | https://github.com/supasuge
# Description: Solves the Magical Oracle challenge
# Usage: python3 test.py [HOST] [PORT]
# Example: python3 test.py localhost 1338
# If no arguments are provided, the script will run locally

import time
import re
import base64
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from pwn import remote, context, log, process
from sage.all import Matrix, vector, QQ, ZZ

# Configuration
HOST = 'localhost' # remote server...
PORT = 1338 # port
context.log_level = 'info' # log level


def build_basis(p, t_vals):
    """
    Build (d+1)x(d+1) HNP lattice basis:
      ➤ rows 0..d-1: p * e_i
      ➤ last row: [t1, t2, ..., td, 1/p]
    https://cims.nyu.edu/~regev/teaching/lattices_fall_2004/ln/cvp.pdf
    """
    d = len(t_vals)
    rows = []
    for i in range(d):
        row = [0] * (d + 1)
        row[i] = p
        rows.append(row)
    rows.append(list(t_vals) + [QQ(1)/QQ(p)])
    return Matrix(QQ, rows)


def approximate_closest_vector(basis, target):
    """
    Babai nearest-plane to solve approximate CVP on LLL-reduced basis.
    Returns the lattice vector coordinates.
    Source: https://cims.nyu.edu/~regev/teaching/lattices_fall_2004/ln/cvp.pdf
    """
    L = basis.LLL()
    G, _ = L.gram_schmidt()
    dim = L.ncols()
    v = vector(ZZ, target)
    for i in reversed(range(dim)):
        coef = (v * G[i]) / (G[i] * G[i])
        coef = coef.round()
        v -= L[i] * coef
    # lattice vector = target - remainder (in ZZ)
    coeffs = (target - v).coefficients()
    return coeffs


def parse_banner(text):
    """Extract p, n, k, d from service banner."""
    p = int(re.search(r"Prime \(p\): (\d+)", text).group(1))
    n = int(re.search(r"Bit length \(n\): (\d+)", text).group(1))
    k = int(re.search(r"MSB leak \(k\): (\d+)", text).group(1))
    d = int(re.search(r"Max queries: (\d+)", text).group(1))
    return p, n, k, d


def leak_samples(io, d):
    """Leak d (t,z) pairs from the MSB oracle."""
    samples = []
    for i in range(1, d+1):
        log.info(f"[+] Query #{i}/{d}")
        io.sendline(b'1')
        resp = io.recvuntil(b'Choose option:')
        t, z = map(int, re.search(rb"t=(\d+), z=(\d+)", resp).groups())
        samples.append((t, z))
    t_vals, z_vals = zip(*samples)
    return samples, t_vals, z_vals


def extract_b64_flag(text):
    """
    Extract the base64-encoded blob that follows the string 'Flag: ' in the server response
    """
    m = re.search(r"Flag:\s*([A-Za-z0-9+/=]+)", text)
    if not m:
        raise ValueError("Could not locate base64 flag in server response")
    b64 = m.group(1)
    return base64.b64decode(b64)


def main():
    start_time = time.perf_counter()
    import sys
    if len(sys.argv) >= 3:
        HOST = sys.argv[1]
        PORT = int(sys.argv[2])
        conn = remote(HOST, PORT) 
    else:
        # Launch the challenge locally from its own folder so flag.txt is accessible
        conn = process(['python3', 'chal.py'], cwd='../src')
    raw = conn.recvuntil(b'Choose option:').decode('utf-8', 'ignore')
    log.info("Banner received")
    p, n, k, d = parse_banner(raw)
    log.info(f"Parameters: p={p}, n={n}, k={k}, d={d}")
    conn.sendline(b'2')  # option 2 = Show encrypted data / Flag
    blob = extract_b64_flag(conn.recvuntil(b'Choose option:').decode('utf-8', 'ignore'))
    log.info(f"Extracted base64({len(blob)} (encrypted) flag characters)")
    iv = blob[:16]
    ct = blob[16:]
    log.success(f"IV: {iv.hex()}")
    log.success(f"Ciphertext length: {len(ct)} bytes")
    samples, t_vals, z_vals = leak_samples(conn, d)
    basis = build_basis(p, t_vals)
    target = vector(QQ, list(z_vals) + [0])
    coeffs = approximate_closest_vector(basis, target)
    alpha = int(coeffs[-1] * p) % p
    log.success(f"Recovered alpha = {alpha}")
    key = sha256(str(alpha).encode()).digest()
    aes = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(aes.decrypt(ct), AES.block_size)
    print("\n=== FLAG PLAINTEXT ===")
    print(pt.decode())
    log.info(f"Time taken: {time.perf_counter() - start_time:.2f}s")
    conn.close()

if __name__ == "__main__":
    main()
