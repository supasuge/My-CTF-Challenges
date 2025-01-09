from math import gcd
import hashlib

def solve_congruence(a, b, m):
    g = gcd(a, m)
    if g == 1:
        # If gcd(a, m) is 1, there's a unique solution modulo m.
        return [(pow(a, -1, m) * b) % m]
    else:
        # If gcd(a, m) is not 1, the congruence may have no solution or multiple solutions.
        solutions = []
        if b % g == 0:
            # There are g solutions.
            a_, b_, m_ = a // g, b // g, m // g
            x0 = (pow(a_, -1, m_) * b_) % m_
            for i in range(g):
                solutions.append((x0 + i * m_) % m)
        return solutions


def attack(n, m1, r1, s1, m2, r2, s2):
    for k in solve_congruence(s1 - s2, m1 - m2, n):
        for x in solve_congruence(r1, (k * s1 - m1) % n, n):
            yield k, x

def decrypt_flag(encrypted_flag, private_key):
    flag = encrypted_flag ^ private_key
    return flag.to_bytes((flag.bit_length() + 7) // 8, 'big')

def extract_r_s(signature_hex):
    # Assuming each r and s are 32 bytes (256 bits) each in the signature
    signature_bytes = bytes.fromhex(signature_hex)
    r = int.from_bytes(signature_bytes[:32], 'big')
    s = int.from_bytes(signature_bytes[32:], 'big')
    return r, s

def main():
    # Curve Order from the challenge
    n = 115792089210356248762697446949407573529996955224135760342422259061068512044369
    # Convert messages to integers
    m1 = int.from_bytes(hashlib.sha256(b"Hello, world!").digest(), 'big')
    m2 = int.from_bytes(hashlib.sha256(b"Hello, CTF!").digest(), 'big')
    # Extract r and s values from the signatures
    r1, s1 = extract_r_s("fb50388f29498d0a93ad25ec4c34037b9d3cc3cca4787eb6fedabe2b3003eac831f6b06983b9319d1d59c6b86b8b804ded68f6ad52caa0484796796d5a2d5ead")
    r2, s2 = extract_r_s("fb50388f29498d0a93ad25ec4c34037b9d3cc3cca4787eb6fedabe2b3003eac8fa0cc6f02e29e4718b967bd77e0c18f7abf6ebb1a99326c2747837d6f6024800")
    encrypted_flag = 152609699090961940793440336988134262229682075471777384596908276721141014597325348947324970214553348

    # Attempt to recover the nonce and private key
    for k, x in attack(n, m1, r1, s1, m2, r2, s2):
        print(f"Recovered nonce: {k}")
        print(f"Recovered private key: {x}")
        flag = decrypt_flag(encrypted_flag, x)
        try:
            print(f"Decrypted flag: {flag.decode()}")
            break
        except UnicodeDecodeError:
            # If decryption fails, continue trying
            continue

if __name__ == "__main__":
    main()
