# Crypto on the Rocks Writeup

**Challenge Author**: supasuge
**Difficulty**: Hard

This challenge was inspired by [CVE-2024-31497](https://www.cert.europa.eu/publications/security-advisories/2024-039/pdf).

Within PuTTY, when utilizing the NIST P-521 elliptic curve, the implementation generates nonces with the first 9 bits set to zero. PuTTY's technique worked by making a SHA-512 hash and then reducing it mod $q$, where $q$ is the order of the group used in the ECDSA system.

## Introduction

This challenge involves breaking the ECDSA (Elliptic Curve Digital Signature Algorithm) using a lattice-based attack. The vulnerability arises from the biased nonce values ($k$) used during the signing process. By exploiting these biases, we can recover the private key and thus derive the AES key to successfully decrypt the encrypted flag. This writeup will provide a detailed explanation of the steps involved in solving the challenge.


### Challenge Source Code
- `chal.py`: Source code is provided to participants for analysis.
```python
from sage.all import *
from typing import Tuple
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import re
p = 0x01ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
K = GF(p)
a = K(0x01fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffc)
b = K(0x0051953eb9618e1c9a1f929a21a0b68540eea2da725b99b315f3b8b489918ef109e156193951ec7e937b1652c0bd3bb1bf073573df883d2c34f1ef451fd46b503f00)
E = EllipticCurve(K, (a, b))
G = E(0x00c6858e06b70404e9cd9e3ecb662395b4429c648139053fb521f828af606b4d3dbaa14b5e77efe75928fe1dc127a2ffa8de3348b3c1856a429bf97e7e31c2e5bd66, 0x011839296a789a3bc0045c8a5fb42c7d1bd998f54449579b446817afbd17273e662c97ee72995ef42640c550b9013fad0761353c7086a272c24088be94769fd16650)
E.set_order(0x01fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffa51868783bf2f966b7fcc0148f709a5d03bb5c9b8899c47aebb6fb71e91386409 * 0x1)
n = G.order()


FLAG: str = open('flag.txt', 'r').read().strip()
KEY: int = randint(1, n - 1)
Q: int = KEY*G
AES_KEY = hashlib.sha256(long_to_bytes(KEY)).digest()

INVALID_ATTEMPTS = 0

def banner() -> str:
    banner = """\n
██████████╗░░█████╗░░█████╗░███████╗█
[=] ------------ Menu------------ [=]
[+] !1: Get Public Key            [+]
[+] !2: Sign a message            [+]
[+] !3: Verify a signature        [+]
[+] !4: Get the encrypted flag    [+]
[+] !5: Exit                      [+]
[=] ------------------------------[=]
██████████╗░░█████╗░░█████╗░███████╗█
\r\n"""
    return banner
def get_k() -> int:
    return int.from_bytes(hashlib.sha512(os.urandom(512//8)).digest(), byteorder='big') % n

def digest(msg) -> int:
    if isinstance(msg, str):
        msg = msg.encode()
    return int.from_bytes(hashlib.sha256(msg).digest(), byteorder='big')


def ecdsa_verify(Q, m, r, s) -> bool:
    e = digest(m)
    w = pow(s, -1, n)
    u1 = int((e * w) % n)  
    u2 = int((r * w) % n)  
    P = (u1 * G) + (u2 * Q)
    return r == int(P.xy()[0])


def ecdsa_sign(d: int, m: str) -> Tuple[int, int]:
    e = digest(m)
    k = get_k()
    P = k * G
    r_i = int(P.xy()[0])
    s_i = (pow(k, -1, n) * (e+r_i*d)) % n
    return (r_i, s_i)

def send_flag() -> str:
        flag = FLAG.encode()
        iv = get_random_bytes(16)
        cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
        ct = cipher.encrypt(pad(flag, AES.block_size))
        return (iv + ct).hex()

def handle_signing() -> tuple:
    while True:
        try:
            inp = input("Enter message to sign. (`!exit`) to return to the main menu.\n\n>> ")
            if inp == "!exit":
                break
            r,s = ecdsa_sign(KEY, inp)
            print(f"Signature (r,s): {(r, s)}")
            
        except Exception as e:
            print(f"Error during signing: {e}")
            continue

def is_valid_format(inp) -> bool:
    pattern = r"^\([^,]+,\d+,\d+\)$"
    match = re.match(pattern, inp)
    return bool(match)

def handle_verfication():
    while True:
        inp = input("Enter the message you want to verify in the format `message,r,s` (`!exit` to return to the main menu).\n\n>> ")
        if inp == '!exit':
            break
        valid = is_valid_format(inp)
        if not valid:
            print("Invalid input format. Please try again.\n")
            continue
        message, r, s = inp.split(',')
        print(f"message: {message}\nr: {r}\ns: {s}\n")
        try:
            i_r, i_s = int(r), int(s)
            valid = ecdsa_verify(Q, message, i_r, i_s)
            result = "Signature is valid\n" if valid else "Signature is invalid\n"
            print(result)
        except Exception as e:
            print(f"Error during verification: {e}")
            continue
        


def process_option(option: str) -> str:
    global INVALID_ATTEMPTS
    if option == '!1':
        INVALID_ATTEMPTS = 0
        public_key_info = f"Public Key (X, Y): {Q.xy()}\n"
        print(public_key_info)
    elif option == '!2':
        INVALID_ATTEMPTS = 0
        handle_signing()
    elif option == '!3':
        INVALID_ATTEMPTS = 0
        handle_verfication()
    elif option == '!4':
        INVALID_ATTEMPTS = 0
        enc_flag = send_flag()
        print(f"Encrypted Flag: {enc_flag}\n")
    elif option == '!5':
        print("Goodbye!\n")
        return False
    else:
        INVALID_ATTEMPTS += 1
        print("Invalid option... Try again\n")
        if INVALID_ATTEMPTS >= 3:
            print("Too many invalid attempts. Exiting.\n")
            return False
    return True
        



def main():
    try:
        b = banner()
        print(b+"\n")
        while True:
            
            inp = input(">> ")
            if not process_option(inp):
                sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}, please try again later.\n")
        pass
    
    finally:
        sys.exit(0)

if __name__ == '__main__':
    main()
```

#### Explaination

1. **Retrieves Public key**: Allows users to obtain the server's public key.
2. **Signature Generation**: Generates ECDSA signatures for user-supplied messages, returned in the form (r, s).
3. **Signature Verification**: Verifies signature validity.
4. **Encrypted Flag Retrieval**: Retrieve an AES-CBC-256 encrypted flag.

---

**Solution Source Code**
- `solution/exploit.py`
```python
from pwn import *
from sage.all import *
import hashlib
from utils import PartialInteger, attack, dsa_known_msb, check_public_key, curve
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib, re
from Crypto.Util.number import long_to_bytes, bytes_to_long
import sys
p = 0x01ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
K = GF(p)
a = K(0x01fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffc)
b = K(0x0051953eb9618e1c9a1f929a21a0b68540eea2da725b99b315f3b8b489918ef109e156193951ec7e937b1652c0bd3bb1bf073573df883d2c34f1ef451fd46b503f00)
E = EllipticCurve(K, (a, b))
G = E(0x00c6858e06b70404e9cd9e3ecb662395b4429c648139053fb521f828af606b4d3dbaa14b5e77efe75928fe1dc127a2ffa8de3348b3c1856a429bf97e7e31c2e5bd66, 0x011839296a789a3bc0045c8a5fb42c7d1bd998f54449579b446817afbd17273e662c97ee72995ef42640c550b9013fad0761353c7086a272c24088be94769fd16650)
E.set_order(0x01fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffa51868783bf2f966b7fcc0148f709a5d03bb5c9b8899c47aebb6fb71e91386409 * 0x1)
n = G.order()
DEFAULT_HOST,DEFAULT_PORT = '172.17.0.2', 1337
host = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HOST
port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
n_sigs = int(sys.argv[3]) if len(sys.argv) > 3 else 100
def hasher(m):
    hashed = int.from_bytes(hashlib.sha256(m.encode()).digest(), byteorder='big')
    return hashed

def parse_sig(input_string):
    pattern = r"Signature \(r,\s*s\):\s*\((\d+),\s*(\d+)\)"
    match = re.search(pattern, input_string)
    if match:
        r = int(match.group(1))
        s = int(match.group(2))
        return (r, s)
    else:
        return None

def parse_pub(s):
    x = int(re.findall(r"Public Key \(X, Y\): \((\d+),", s)[0])
    y = int(re.findall(r"Public Key \(X, Y\): \(\d+, (\d+)\)", s)[0])
    return (x, y)

def get_pub(r):
    r.recvuntil(b">> ")
    r.sendline(b"!1")
    pub = r.recvline().strip().decode()
    xy_pub = parse_pub(pub)
    print(f"[+] Public Key Received: {xy_pub} [+]")
    return xy_pub, pub

def get_sigs(n, r):
    sigs = []
    r.recvuntil(b">> ")
    r.sendline(b'!2')
    for i in range(n):
        r.recvuntil(b">> ")
        r.sendline(b"message")
        sig_line = r.recvline().strip().decode()
        parsed_sig = parse_sig(sig_line)
        if parsed_sig:
            sigs.append(parsed_sig)
        else:
            print(f"[-] Failed to parse signature: {sig_line} [-]")
    r.sendline(b"!exit")
    print(f"[+] Total Parsed Signatures: {len(sigs)} [+]")
    return sigs

def get_flag(r):
    r.recvuntil(b">> ")
    
    r.sendline(b"!4")
    dat = r.recv(1024).strip().decode()
    stripped = re.findall(r"Encrypted Flag: ([a-f0-9]+)", dat)
    print(dat)
    print(f"[+] Received Encrypted Flag: {stripped} [+]")
    if len(stripped) == 0:
        r.recvuntil(b">> ")
        r.sendline(b"!4")
        dat2 = r.recvline().strip().decode()
        print(dat2)
        stripped = re.findall(r"Encrypted Flag: ([a-f0-9]+)", dat2)[0]
        print(f"[+] Received Encrypted Flag: {stripped} [+]")
    return stripped

def decrypt_flag(ciphertext, key):
    ciphertext = bytes.fromhex(ciphertext)
    iv = ciphertext[:16]
    ciphertext = ciphertext[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ciphertext), AES.block_size)

def main(n_sigs:int):
    r = remote(host, port)
    print("[+] Connection established with the server. [+]")
    try:
        # list of k's
        k_i = []
        # list of hashed messages
        h_i = []
        # list of r's from ecdsa signatures
        r_i = []
        # list of s' from ecdsa signatures
        s_i = []
        msg = "message"
        hashed = hasher(msg)
        # get public key
        pub, _ = get_pub(r)
        # get n signatures
        sigs = get_sigs(n_sigs, r)
        # get the encrypted flag
        flag = get_flag(r)
        # partial integer for biased k's
        ks = PartialInteger.from_bits_be("000000000"+("?"*512))
        for r_s, s in sigs:
            r_s_i = str(r_s).replace(",", "")
            s_i.append(int(s))
            r_i.append(int(r_s_i))
            k_i.append(ks)
            h_i.append(hashed)
        print(f"[+] Arrays lengths\n-> h_i: {len(h_i)}\n-> r_i: {len(r_i)}\n-> s_i: {len(s_i)}\n-> k_i: {len(k_i)}\n[+]")
        
        for d_, _ in dsa_known_msb(n, h_i, r_i, s_i, k_i):
            if check_public_key(int(d_), curve, pub[0], pub[1]):
                print("[+] Success: Correct private key found. [+]")
                print(f"[+] Private Key: {d_} [+]")
                print(f"[+] AES_KEY: {hashlib.sha256(long_to_bytes(int(d_))).hexdigest()} [+]")
                dec_flag = decrypt_flag(flag, hashlib.sha256(long_to_bytes(int(d_))).digest())
                print(f"[+] Decrypted Flag: {dec_flag.decode()} [+]")
                print(f"/[+]\\After {n_sigs} signatures, private key has been successfully recovered and the flag decrypted /[+]\\")
                break
            else:
                print("Unsuccessful attack on attempt #")
    finally:
        r.close()
        print("Connection closed.")

if __name__ == "__main__":
    main(n_sigs)
```

- `solution/utils.py`
```python
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from sage.all import matrix, QQ
import hashlib
import re
from math import log2
curve = ec.SECP521R1()

def parse_pub(inp):
    try:
        match = re.search(r"Public Key \(X, Y\): \((\d+), (\d+)\)", inp)
        if match:
            x = int(match.group(1))
            y = int(match.group(2))
            return x, y
    except Exception as e:
        return None
def parse_sig(data):
    match = re.search(r'Signature \(r, s\): \((\d+), (\d+)\)', data)
    #print(data)
    #print(match)
    if match:
        return int(match.group(1)), int(match.group(2))
    else:
        return None



def hashmsg(m):
    """ Hash a message using SHA-256 and return the integer representation. """
    if isinstance(m, str):
        m = m.encode()
    return int.from_bytes(hashlib.sha256(m).digest(), byteorder='big')

def check_public_key(private_int, curve, known_x, known_y):
    private_key = ec.derive_private_key(private_int, curve, default_backend())
    public_key = private_key.public_key()
    public_numbers = public_key.public_numbers()
    return (public_numbers.x == known_x) and (public_numbers.y == known_y)

def int_to_openssh(private_int, curve):
    private_key = ec.derive_private_key(private_int, curve, default_backend())
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption()
    )
    return pem.decode()
def shortest_vectors(B):
    B = B.LLL()

    for row in B.rows():
        if not row.is_zero():
            yield row


# Source: https://github.com/jvdsn/crypto-attacks/blob/master/attacks/hnp/lattice_attack.py
def attack(a, b, m, X):
    """
    Solves the hidden number problem using an attack based on the shortest vector problem.
    The hidden number problem is defined as finding y such that {xi = {aij * yj} + bi mod m}.
    :param a: the aij values
    :param b: the bi values
    :param m: the modulus
    :param X: a bound on the xi values
    :return: a generator generating tuples containing a list of xi values and a list of yj values
    """
    assert len(a) == len(b), "a and b lists should be of equal length."

    n1 = len(a)
    n2 = len(a[0])
    B = matrix(QQ, n1 + n2 + 1, n1 + n2 + 1)
    for i in range(n1):
        for j in range(n2):
            B[n1 + j, i] = a[i][j]

        B[i, i] = m
        B[n1 + n2, i] = b[i] - X // 2

    for j in range(n2):
        B[n1 + j, n1 + j] = X / QQ(m)

    B[n1 + n2, n1 + n2] = X

    for v in shortest_vectors(B):
        xs = [int(v[i] + X // 2) for i in range(n1)]
        ys = [(int(v[n1 + j] * m) // X) % m for j in range(n2)]
        if all(y != 0 for y in ys) and v[n1 + n2] == X:
            yield xs, ys
# Source: https://github.com/jvdsn/crypto-attacks/blob/master/attacks/hnp/lattice_attack.py
def dsa_known_msb(n, h, r, s, k):
    """
    Recovers the (EC)DSA private key and nonces if the most significant nonce bits are known.
    :param n: the modulus
    :param h: a list containing the hashed messages
    :param r: a list containing the r values
    :param s: a list containing the s values
    :param k: a list containing the partial nonces (PartialIntegers)
    :return: a generator generating tuples containing the possible private key and a list of nonces
    """
    assert len(h) == len(r) == len(s) == len(k), "h, r, s, and k lists should be of equal length."
    a = []
    b = []
    X = 0
    for hi, ri, si, ki in zip(h, r, s, k):
        msb, msb_bit_length = ki.get_known_msb()
        shift = 2 ** ki.get_unknown_lsb()
        a.append([(pow(si, -1, n) * ri) % n])
        b.append((pow(si, -1, n) * hi - shift * msb) % n)
        X = max(X, shift)

    for k_, x in attack(a, b, n, X):
        yield x[0], [ki.sub([ki_]) for ki, ki_ in zip(k, k_)]

# Source: https://github.com/jvdsn/crypto-attacks/blob/master/shared/partial_integer.py
class PartialInteger:
    """
    Represents positive integers with some known and some unknown bits.
    """

    def __init__(self):
        """
        Constructs a new PartialInteger with total bit length 0 and no components.
        """
        self.bit_length = 0
        self.unknowns = 0
        self._components = []

    def add_known(self, value, bit_length):
        """
        Adds a known component to the msb of this PartialInteger.
        :param value: the value of the component
        :param bit_length: the bit length of the component
        :return: this PartialInteger, with the component added to the msb
        """
        self.bit_length += bit_length
        self._components.append((value, bit_length))
        return self

    def add_unknown(self, bit_length):
        """
        Adds an unknown component to the msb of this PartialInteger.
        :param bit_length: the bit length of the component
        :return: this PartialInteger, with the component added to the msb
        """
        self.bit_length += bit_length
        self.unknowns += 1
        self._components.append((None, bit_length))
        return self
    .
    ,
...
[SNIP]
...
```

### Challenge Overview

1. **Public Key Retrieval**: The challenge provides an option to retrieve the public key.
2. **Signature Generation**: The user can generate multiple ECDSA signatures.
3. **Signature Verification**: The user can verify the validity of given signatures.
4. **Encrypted Flag Retrieval**: The challenge provides an option to retrieve an encrypted flag.

The goal is to recover the private key used for signing messages by leveraging biased nonces in the ECDSA signature process. Once the private key is obtained, it can be used to derive the AES key, which is then used to decrypt the flag.

### Technical Details

#### ECDSA Signature Scheme

In ECDSA, a signature for a message $m$ is generated as follows:

1. Compute the hash of the message, $e = \text{HASH}(m)$.
2. Generate a random nonce $k$.
3. Compute the elliptic curve point $P = kG$, where $G$ is the base point of the curve.
4. The signature components are:
   - $r = x_P \mod n$, where $x_P$ is the x-coordinate of $P$
   - $s = k^{-1}(e + rd) \mod n$, where $d$ is the private key.
5. The signature is $(r, s)$.

The public key $Q$ is computed as $Q = dG$.

#### Challenge Implementation

The provided `challenge.py` script performs the ECDSA signing and encryption of the flag. The `ecdsa_sign` function generates signatures using a biased nonce $k$ where the $9$ most significant bits (MSBs) are zero. This is a common mistake with the NIST P-521 Curve as it can be easily mistaken for $512$ instead of $521$.

**Vulnerability**
```python
def get_k() -> int:
    return int.from_bytes(hashlib.sha512(os.urandom(512//8)).digest(), byteorder='big') % n

def ecdsa_sign(d: int, m: str) -> Tuple[int, int]:
    e = digest(m)
    k = get_k()
    P = k * G
    r_i = int(P.xy()[0])
    s_i = (pow(k, -1, n) * (e + r_i * d)) % n
    return (r_i, s_i)
```

#### Lattice Attack: Exploiting the Bias

**Hidden Number Problem**: The bias k transforms the ECDSA signing equation into a hidden number problem(HNP). Each signature $(r^{i}, s^{i})$ for message hash $h^{i}$ gives us the equation:
```
kᵢ - sᵢ⁻¹rᵢd - sᵢ⁻¹hᵢ ≡ 0 (mod n)
```
Since we know the most significant bits of kᵢ are zero, this becomes an HNP instance, where d is the hidden number.

The lattice attack leverages the structure of the signature equations to recover the private key. Given several signatures $(r_i, s_i)$ for messages $m_i$:

1. Compute the hash of each message $e_i = \text{HASH}(m_i)$.
2. For each signature, express $s_i$ as:
   $$s_i = k_i^{-1}(e_i + r_i d) \mod n$$
   Rearrange to get:
   $$k_i = s_i^{-1}(e_i + r_i d) \mod n$$
3. Using the biased $k$ values, we know the MSBs are zero. This can be modeled as a hidden number problem (HNP).
4. Construct a lattice basis to solve for the private key $d$ using the Lenstra–Lenstra–Lovász (LLL) algorithm.

#### Solution Script

The `exploit.py` script performs the following steps to recover the private key and decrypt the flag:

1. **Retrieve Public Key**:
   ```python
   pub, _ = get_pub(r)
   ```

2. **Retrieve Signatures**:
   ```python
   sigs = get_sigs(n_sigs, r)
   ```

3. **Retrieve Encrypted Flag**:
   ```python
   flag = get_flag(r)
   ```

4. **Construct Partial Integers for Biased k Values**:
   ```python
   ks = PartialInteger.from_bits_be("000000000" + ("?" * 512))
   ```

5. **Set Up Arrays for Lattice Attack**:
   ```python
   for r_s, s in sigs:
       r_s_i = str(r_s).replace(",", "")
       s_i.append(int(s))
       r_i.append(int(r_s_i))
       k_i.append(ks)
       h_i.append(hashed)
   ```

6. **Perform Lattice Attack**:
   ```python
   for d_, _ in dsa_known_msb(n, h_i, r_i, s_i, k_i):
       if check_public_key(int(d_), curve, pub[0], pub[1]):
           # Private key found
           break
   ```

7. **Decrypt Flag**:
   ```python
   dec_flag = decrypt_flag(flag, hashlib.sha256(long_to_bytes(int(d_))).digest())
   ```

#### Explanation of Lattice Construction

Constructing the Lattice
The lattice construction for solving the hidden number problem (HNP) with LLL involves several key steps. The matrix construction $M$ is based on the relations from the ECDSA signatures and the bias in the nonces.

1. **Signature Equations:**
   For each signature $(r_i, s_i)$, the relation is:
   $r_i d = k_i s_i - e_i \mod n$

2. **Partial Information:**
   Given that the nonces $k_i$ have the first 9 bits set to zero, we can model this as a HNP where $k_i$ is partially known.

3. **Lattice Construction:**
   Construct the matrix $M$ with dimensions $(m + 2) \times (m + 2)$:

$$
M = \begin{bmatrix}
n & 0 & 0 & \cdots & 0 & 0 \\
0 & n & 0 & \cdots & 0 & 0 \\
\vdots & \vdots & \vdots & \ddots & \vdots & \vdots \\
0 & 0 & 0 & \cdots & n & 0 \\
r_1 & r_2 & r_3 & \cdots & r_m & B/n \\
s_1 & s_2 & s_3 & \cdots & s_m & 0 \\
0 & 0 & 0 & \cdots & 0 & B \\
\end{bmatrix}
$$

4. **LLL Reduction**: Applying the LLL algorithm to $M$ yields a reduced basis, and the shortest vector of this bases is expected to reveal the hidden number $d$ (the private key) along with the unknown parts of the nonces $k_{i}$
#### Conclusion

This challenge demonstrates the practical application of lattice-based cryptanalysis to break ECDSA when nonces are biased. By carefully analyzing the signatures and constructing a suitable lattice, the private key can be recovered, allowing for the decryption of the flag. This attack underscores the importance of using strong, unbiased random values in cryptographic protocols.


##### Script in use
[exploit.py](https://github.com/supaaasuge/CTF-Challenges/blob/main/crypto-on-the-rocks/solution/exploit.py)
```bash
python exploit.py 
[+] Opening connection to 172.17.0.2 on port 1337: Done
[+] Connection established with the server. [+]
[+] Public Key Received: (3109980590986919311287046533887492002477811552891909791863089310727982955200855447689228284912554348477907370491007162534350370090834859510917441206285191833, 1849341532655318689606938160662082719013085154529414983552465624971698466645605396348569232219887646346509053390109036465552085426099099404907799665353982020) [+]
[+] Total Parsed Signatures: 100 [+]
██████████╗░░█████╗░░█████╗░███████╗█
[=] ------------ Menu------------ [=]
[+] !1: Get Public Key            [+]
[+] !2: Sign a message            [+]
[+] !3: Verify a signature        [+]
[+] !4: Get the encrypted flag    [+]
[+] !5: Exit                      [+]
[=] ------------------------------[=]
██████████╗░░█████╗░░█████╗░███████╗█


>>
[+] Received Encrypted Flag: [] [+]
Encrypted Flag: 4bce8bc72f8ed73016a7fa8b3c0543e863dbb4ac382707d3f916b49450faa64c3324aed5f5052917901c35ba1b1a03f01b60a098b8965511be9b461d2d447fc3
[+] Received Encrypted Flag: 4bce8bc72f8ed73016a7fa8b3c0543e863dbb4ac382707d3f916b49450faa64c3324aed5f5052917901c35ba1b1a03f01b60a098b8965511be9b461d2d447fc3 [+]
[+] Arrays lengths
-> h_i: 100
-> r_i: 100
-> s_i: 100
-> k_i: 100
[+]
[+] Success: Correct private key found. [+]
[+] Private Key: 4382437925999591767510550313910999914971677081144417715676670125599319162854128772342173165773504391470287477162386441738612489510063693972385644281868216440 [+]
[+] AES_KEY: c10216d682898955ef6fbb64afeca03c9bb5a68b4bcaaa9ca792991371b2214c [+]
[+] Decrypted Flag: L3AK{9_b1ts_12_m0r3_th4n_3n0ugh} [+]
```

###### Sources
- https://www.chiark.greenend.org.uk/~sgtatham/putty/wishlist/vuln-p521-bias.html
- https://www.cert.europa.eu/publications/security-advisories/2024-039/pdf
- https://www.openwall.com/lists/oss-security/2024/04/15/6
- https://github.com/jvdsn/crypto-attacks
- https://github.com/advisories/GHSA-6p4c-r453-8743
