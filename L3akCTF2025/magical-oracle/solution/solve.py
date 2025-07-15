#!/usr/local/bin/sage -python
import re, base64, time
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from pwn import remote, context, log, process
from sage.all import Matrix, vector, QQ, ZZ

context.log_level = 'info'
HOST, PORT = 'localhost', 1338

def build_basis(p, t_vals):
    d = len(t_vals)
    rows = [[(p if i == j else 0) for j in range(d)] + [0] for i in range(d)]
    rows.append(list(t_vals) + [QQ(1)/QQ(p)])
    return Matrix(QQ, rows)

def babai_cvp(B, y):
    L = B.LLL(); G,_ = L.gram_schmidt(); m = L.ncols(); v = vector(ZZ, y)
    for i in reversed(range(m)):
        coef = (v * G[i]) / (G[i] * G[i]); coef = coef.round(); v -= L[i] * coef
    return (y - v).coefficients()

def main():
    start_time = time.perf_counter()
    # run the challenge locally from its own directory so that flag.txt is found
    conn = process(['python3', 'chal.py'], cwd='../src')
    banner = conn.recvuntil(b'Choose option:').decode()
    p = int(re.search(r"Prime \(p\): (\d+)", banner).group(1))
    n = int(re.search(r"Bit length \(n\): (\d+)", banner).group(1))
    k = int(re.search(r"MSB leak \(k\): (\d+)", banner).group(1))
    d = int(re.search(r"Max queries: (\d+)", banner).group(1))
    log.info(f"Params: p={p}, n={n}, k={k}, d={d}")

    # fetch encrypted flag
    conn.sendline(b'2')
    enc_resp = conn.recvuntil(b'Choose option:').decode()
    b64 = re.search(r"Flag: ([A-Za-z0-9+/=]+)", enc_resp).group(1)
    data = base64.b64decode(b64); iv, ct = data[:16], data[16:]

    # leak samples
    samples = []
    for i in range(d):
        conn.sendline(b'1'); resp = conn.recvuntil(b'Choose option:')
        t, z = map(int, re.search(rb"t=(\d+), z=(\d+)", resp).groups())
        log.info(f"[+] Query #{i+1}/{d} | t={t}, z={z}")
        samples.append((t, z))
    t_vals, z_vals = zip(*samples)

    # lattice attack
    B = build_basis(p, t_vals)
    target = vector(QQ, list(z_vals) + [0])
    coeffs = babai_cvp(B, target)
    alpha = int(coeffs[-1] * p) % p
    log.success(f"Recovered alpha = {alpha}")

    # decrypt flag
    key = sha256(str(alpha).encode()).digest()
    pt = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(ct), AES.block_size)
    print("\n*** FLAG: ", pt.decode())
    log.info(f"Time taken: {time.perf_counter() - start_time:.2f}s")
    conn.close()

if __name__ == '__main__': 
    main()
