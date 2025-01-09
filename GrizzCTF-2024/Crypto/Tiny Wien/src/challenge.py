from Crypto.Util.number import long_to_bytes,bytes_to_long
import Crypto
import json
from math import isqrt

from sympy import *
import random
def get_prime(bits):
	p = Crypto.Util.number.getPrime(bits, randfunc=Crypto.Random.get_random_bytes)
	return(p)

def create_keypair(size):
    while True:
        p = get_prime(size // 2)
        q = get_prime(size // 2)
        if q < p < 2*q:
            break

    N = p * q
    phi_N = (p - 1) * (q - 1)

    max_d = isqrt(isqrt(N))// 3

    max_d_bits = max_d.bit_length() - 1

    while True:
        d = random.randint(0,2**max_d_bits)
        try:
            e = pow(d,-1,phi_N)
        except: 
            continue
        if (e * d) % phi_N == 1:
            break

    return  N, e, d, p, q

def challenge():
    flag = b"GrizzCTF{FAKE_FLAG}"
    
    bits=1024


    m=  bytes_to_long(flag)

    N, e, d, p, q = create_keypair(bits)

    C=pow(m,e,N)
    with open("parameters.txt", "w") as f:
        f.write(f'Bob uses RSA to send an encrypted message to Alice...\n\nThe public exponent (e) is {e}\n\nThe public modulus (N) is {N}\n\nCiphertext: {C}\r\nCan you decrypt the ciphertext?')
        f.close()

if __name__ == "__main__":
    challenge()
