## Tine Wien Writeup

### Source Code

```python
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
```

#### RSA Review

N is the product of two randomly chosen prime numbers $p$ and $q$. The private key, $d$, is the decryption exponent:
$$d = e^{-1} \mod ((p-1)(q-1)) = e^{-1} \mod \varphi(N)$$

Where $\varphi(N)$ is Euler’s totient function.

That is, there exists an integer $k$ such that $ed - k\varphi(N) = 1$, therefore:
$$\varphi(N) = \frac{ed - 1}{k}$$

### Solution
```python
from Crypto.Util.number import long_to_bytes,bytes_to_long
import sys
from math import isqrt
from sympy import *

e = 74055340431099766408882267936707642776010581650226201435272792497407293550292032013365925471952817567082880719598406769094568979789928119562145914243280878464502052173375594901651274318376175184252526143746832711593099473243252199500624302661789011938943589291504715025871829888318478230201298680279927185733
N = 97838914831828271794696554308495184238240010208735264833579555635753067640434614260046620044873849882180913747606655702840215394750887109650142301939794552635889224306341701134323183224147183747372000979247618403209966043006121584995372147645237890163928903207087981410772075930324948247238594610177554797321
C = 16861587669946001223376806426754973317306019873744431685975187231903035170674446121012586442191625287148010783417525587119378816364236506893049174859369649958165190503787679501681754293043786718562966424512787855312521596063364606668169962695198065691250458367098623875931167644186298697657888093564424546097

def get_cf_expansion(n, d):
    e = []
    q = n // d
    r = n % d
    
    e.append(q)

    while r != 0:
        n, d = d, r           
        q = n // d
        r = n % d
        e.append(q)

    return e
def get_convergents(e):
    n = [] # Nominators
    d = [] # Denominators

    for i in range(len(e)):
        if i == 0:
            ni = e[i]
            di = 1
        elif i == 1:
            ni = e[i]*e[i-1] + 1
            di = e[i]
        else: # i > 1 
            ni = e[i]*n[i-1] + n[i-2]
            di = e[i]*d[i-1] + d[i-2]

        n.append(ni)
        d.append(di)
        yield (ni, di)
# Step 1: Calculate the Continued Fraction Expansion
cf_expansion = get_cf_expansion(e, N)

# Step 2: Generate Convergents
convergents = get_convergents(cf_expansion)

# Step 3: Test Convergents to Try Decrypting
for pk, pd in convergents:  # pk - possible k, pd - possible d
    if pk == 0:
        continue;

    possible_phi = (e*pd - 1)//pk

    # Step 4: Solve for Potential Primes (p and q) 
    p = Symbol('p', integer=True)
    roots = solve(p**2 + (possible_phi - N - 1)*p + N, p)  

    if len(roots) == 2:
        pp, pq = roots  # pp - possible 'p', pq - possible 'q'
        if pp*pq == N:
            print('\n--Found factors of N using Wiener attack--!!--\n')
            d = pow(e, -1, possible_phi)  # Calculate the private exponent 'd'
            print('\nFound d:', d)
            print('\nFound p:', pp)
            print('\nFound q:', pq)
            print('\nFound PHI:', possible_phi)
            print('Now using C^d mod N')
            M = pow(C, d, N)  # Decrypt the message
            print(f"\nDecrypted message found!: {long_to_bytes(M)}")  
            sys.exit(0)  

# If we still haven't found p and q...
print('[-] Wiener\'s Attack failed; Could not factor N')
sys.exit(1) 
```


# Explanation
#### RSA Parameters
- $e$, $N$, and $C$ are the RSA public exponent, modulus, and ciphertext, respectively, specific to this challenge.

#### Wiener's Attack Process
1. **Continued Fraction Expansion**: The function `get_cf_expansion(e, N)` calculates the continued fraction expansion of $$\frac{e}{N}$$ A continued fraction for a real number $x$ is expressed as:
   $$x = a_0 + \cfrac{1}{a_1 + \cfrac{1}{a_2 + \cfrac{1}{a_3 + \cdots}}}$$
   where $a_0, a_1, a_2, \ldots$ are integers. For $\frac{e}{N}$, this expansion helps in finding fractions that approximate the true value of $\frac{e}{N} $.

2. **Compute Convergents**: The convergents are computed using the expansion, with each convergent providing a fraction that approximates $\frac{e}{N}$ more closely. The $i^{th}$ convergent $\frac{n_i}{d_i}$ is calculated using the recursive formulas:
   - $n_i = a_i \cdot n_{i-1} + n_{i-2}$
   - $d_i = a_i \cdot d_{i-1} + d_{i-2}$
   with initial conditions $n_{-2} = 0, n_{-1} = 1, d_{-2} = 1, d_{-1} = 0$

3. **Iterate Over Convergents**: For each convergent $\frac{n_i}{d_i}$, the script attempts to decrypt the ciphertext by:
   - Calculating a potential $\phi(N)$ using the relation $\phi(N) = (e \cdot d_i - 1) / n_i$
   - Solving the quadratic equation $p^2 + ( \phi(N) - N - 1 ) \cdot p + N = 0$ to find potential prime factors $p$  and $q$ of $N$.

4. **Verification and Decryption**: If the product of the computed primes equals $N$, the correct factors have been found. The private exponent $d$ is then calculated, and the original message is decrypted using $M = C^d \mod N$.

#### Success and Failure Messages
- Upon successfully finding $p$, $q$, and $d$, the script prints the decrypted message.
- If the attack fails to find the factors, it indicates Wiener's attack was unsuccessful.

###### Resources
- [Classic Wieners Attack](https://sagi.io/crypto-classics-wieners-rsa-attack/)
