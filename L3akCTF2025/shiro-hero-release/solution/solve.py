#!/usr/bin/env python3
from ecc import ECDSA
from cracker import Xoshiro256Predictor
from Crypto.Util.number import long_to_bytes, bytes_to_long, inverse
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib
# Recover private key from r, s, h, n, and our predicted k
def recover_priv(r, s, h, k, n):
    return ((s * k - h) * inverse(r, n)) % n
# Provided challenge data
leaks = ['0x785a1cb672480875', '0x91c1748fec1dd008', '0x5c52ec3a5931f942', '0xac4a414750cd93d7']
public_key = (108364470534029284279984867862312730656321584938782311710100671041229823956830, 
              13364418211739203431596186134046538294475878411857932896543303792197679964862)
message = b"My favorite number is 0x69. I'm a hero in your mother's bedroom, I'm a hero in your father's eyes. What am I?"
r, s = (54809455810753652852551513610089439557885757561953942958061085530360106094036,
        42603888460883531054964904523904896098962762092412438324944171394799397690539)
ciphertext = "404e9a7bbdac8d3912d881914ab2bdb924d85338fbd1a6d62a88d793b4b9438400489766e8e9fb157c961075ad4421fc"

# Step 1: Verify signature validity
H = bytes_to_long(message)
is_valid = ECDSA.ecdsa_verify(H, public_key, (r, s))
print(f"Signature valid: {is_valid}")

# Step 2: Recover PRNG state and predict nonce k
leaks_int = [int(leak, 16) for leak in leaks]
predictor = Xoshiro256Predictor(leaks_int)
predictor.recover_seed()
k_pred = predictor.predict(1)[0] % ECDSA.n
print(f"Predicted nonce k: {k_pred}")

# Step 3: Recover ECDSA private key
d_recovered = recover_priv(r, s, H, k_pred, ECDSA.n)
print(f"Recovered private key: {hex(d_recovered)}")

# Step 4: Decrypt AES-encrypted flag using recovered private key
key = hashlib.sha256(long_to_bytes(d_recovered)).digest()
iv = bytes.fromhex(ciphertext[:32])
ct = bytes.fromhex(ciphertext[32:])
cipher = AES.new(key, AES.MODE_CBC, iv)
flag = unpad(cipher.decrypt(ct), AES.block_size)

# Final output
print(f"Recovered Flag: {flag.decode()}")