#!/usr/bin/python3
# 
from random import SystemRandom
from math import gcd
from Crypto.Util.number import inverse
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from hashlib import sha3_256
m_prime = 11213     
xi1 = 0.31     
xi2 = 0.69    
w = 10      

rand = SystemRandom()

def hamming_weight(a):
    return a.bit_count()

def get_number(n, h):
    if not (1 <= h <= n):
        raise ValueError(f"Cannot set {h} bits in {n}-bit number")
    low_positions = rand.sample(range(n - 1), h - 1)
    positions = low_positions + [n - 1]
    a = 0
    for pos in positions:
        a |= 1 << pos
    return a

def gen_params(n, w, xi1, xi2, af=1):
    p = 2**n - 1
    bf = int(n * xi1)
    bg = int(n * xi2 * af)
    f = get_number(bf, w)
    g = get_number(bg, w)
    while gcd(f, g) != 1:
        g = get_number(bg, w)
    h = inverse(g, p) * f % p
    return p, f, g, h

def main():
    p, f, g, h = gen_params(m_prime, w, xi1, xi2)
    secret = (f * g ) % p
    secret_bytes = secret.to_bytes((secret.bit_length() + 7)//8, byteorder='big') 
    flag = open('flag.txt', 'rb').read()
    key = sha3_256(secret_bytes).digest()
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext_raw = iv +cipher.encrypt(pad(flag, 16))
    ciphertext_hex = ciphertext_raw.hex()
    print(f"Ciphertext = {ciphertext_hex}")
    print(f"p   = {p}")
    print(f"h   = {h}")
    print(f"xi1 = {xi1}")
    print(f"xi2 = {xi2}")
    print(f"w   = {w}")



if __name__ == "__main__":
    main()

