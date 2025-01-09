# challenge.py

import os
import hashlib
from ecdsa import SigningKey, NIST256p
from ecdsa.util import sigencode_string, sigdecode_string

def hash_message(message):
    """Hashes a message using SHA-256."""
    return hashlib.sha256(message).digest()

def sign_message_with_nonce(sk, message, k):
    """Signs a message with a given ECDSA private key and nonce."""
    digest = hash_message(message)
    sig = sk.sign_digest(digest, sigencode=sigencode_string, k=k)
    return sig

def main():
    sk = SigningKey.generate(curve=NIST256p)
    vk = sk.get_verifying_key()

    message1 = b"Hello, world!"
    message2 = b"Hello, CTF!"

    k = 123456789

    signature1 = sign_message_with_nonce(sk, message1, k)
    signature2 = sign_message_with_nonce(sk, message2, k)

    flag = b"GrizzCTF{FAKE_FLAG_FAKE_FLAG}"
    encrypted_flag = int.from_bytes(flag, byteorder='big') ^ sk.privkey.secret_multiplier

    print(f"Public Key: {vk.to_string().hex()}")
    print(f"Signature 1: {signature1.hex()}")
    print(f"Signature 2: {signature2.hex()}")
    print(f"Encrypted Flag: {encrypted_flag}")
    print(f"Curve Order: {NIST256p.order}")

if __name__ == "__main__":
    main()
