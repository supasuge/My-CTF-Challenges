#!/usr/bin/env python3
import numpy as np
import secrets
import gmpy2

def generate_secret_key(matrix_size=8, alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789_{}"):
    alphabet_size = len(alphabet)
    
    def is_invertible(matrix, modulus):
        det = int(round(np.linalg.det(matrix))) % modulus
        if gmpy2.gcd(det, modulus) != 1:
            return False
        try:
            gmpy2.invert(det, modulus)
        except ZeroDivisionError:
            return False
        return True
    while True:
        matrix = np.array([
            [secrets.randbelow(alphabet_size) for _ in range(matrix_size)]
            for _ in range(matrix_size)
        ])
        if is_invertible(matrix, alphabet_size):
            key_matrix = matrix.tolist()
            return key_matrix

def stov(s, alphabet):
    return [alphabet.index(c) for c in s]

def vtos(x, alphabet):
    return ''.join([alphabet[i] for i in x])

def chunk(s, n):
    return [s[i:i+n] for i in range(0, len(s), n)]

def modinv(matrix, m):
    det = int(round(np.linalg.det(matrix))) % m
    det_inv = int(gmpy2.invert(det, m))
    adjugate = np.round(det * np.linalg.inv(matrix)).astype(int)
    inv_matrix = (det_inv * adjugate) % m
    return inv_matrix

def encrypt(plaintext, alphabet, key_matrix):
    m, n = len(alphabet), len(key_matrix)
    plaintext = plaintext.strip().ljust((len(plaintext) + n - 1) // n * n, 'x')
    return ''.join(
        vtos((np.dot(key_matrix, stov(plaintext[i:i+n], alphabet)) % m).tolist(), alphabet)
        for i in range(0, len(plaintext), n)
    )

def main():
    FLAG = open("flag.txt", "r").read().strip()
    OUT = ""
    M = 8  # 8x8 
    SECRET_KEY = generate_secret_key(M)
    ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789_{}"
    OUT+="SECRET_KEY = [\n"
    for row in SECRET_KEY:
        OUT += f"    {row},\n"
    OUT+="]"
    ct = encrypt(FLAG, ALPHABET, SECRET_KEY)
    with open("output.txt", "w") as f:
        f.write(OUT)
        f.write("\n\n")
        f.write(f"Ciphertext = {ct}")

if __name__ == "__main__":
    main()
