# Combined Multiple Recursive Generator (CMRG) Attack

## Introduction

This challenge involves attacking the linearity of a Combined Multiple Recursive Generator (CMRG). The original source code dates back to a 2021 CTF; aside from slight parameter adjustments (to make the challenge a bit easier) and a new flag, the core remains the same as in Section 5 of the [Lattice Attacks on Pseudo‑Random Number Generators](https://eprint.iacr.org/2021/1204.pdf) paper. Many write‑ups are in foreign languages and full of LaTeX, so this README provides a self‑contained explanation and solution code.

## CMRG Definition

A CMRG combines three linear congruential generators (LCGs) with pairwise‑coprime moduli $m_1$, $m_2$, and $m_3$:

$$
\begin{aligned}
x_i &= a_{11}\,x_{i-1} + a_{12}\,x_{i-2} + a_{13}\,x_{i-3} \pmod{m_1},\\
y_i &= a_{21}\,y_{i-1} + a_{22}\,y_{i-2} + a_{23}\,y_{i-3} \pmod{m_2},\\
z_i &= a_{31}\,z_{i-1} + a_{32}\,z_{i-2} + a_{33}\,z_{i-3} \pmod{m_3}.
\end{aligned}
$$

The un‑modded internal output is

$$
\tilde{o}_i = 2\,m_1\,x_i \;-\; m_3\,y_i \;-\; m_2\,z_i,
$$

and the public output is

$$
o_i = \tilde{o}_i \bmod M,\quad M = 2^{64} - 59.
$$

## Key Questions

1. **Offset ambiguity**  
   Since we only observe $o_i = \tilde{o}_i \bmod M$, each $o_i$ may differ from $\tilde{o}_i$ by any multiple of $M$. We resolve this by brute‑forcing small offsets $q_i \in \{0,\pm1,\pm2\}$.

2. **CRT consolidation**  
   Because $m_1,m_2,m_3$ are pairwise coprime, we can CRT‑combine the three recurrences into one modulo $m_1 m_2 m_3$. Define

$$
\begin{aligned}
A &\equiv a_{11}\pmod{m_1},\; A\equiv a_{21}\pmod{m_2},\; A\equiv a_{31}\pmod{m_3},\\
B &\equiv a_{12}\pmod{m_1},\; B\equiv a_{22}\pmod{m_2},\; B\equiv a_{32}\pmod{m_3},\\
C &\equiv a_{13}\pmod{m_1},\; C\equiv a_{23}\pmod{m_2},\; C\equiv a_{33}\pmod{m_3},
\end{aligned}
$$

giving the combined recurrence

$$
X_i = A\,X_{i-1} + B\,X_{i-2} + C\,X_{i-3}\quad\pmod{m_1 m_2 m_3}.
$$

## Attack Outline

1. **Recover un‑modded outputs**  
   For each observed $o_i$, try $\tilde{o}_i = o_i + q_i\,M$ with $q_i \in \{0,\pm1,\pm2\}$.

2. **Compute intermediate $k_i$**  
   From $\tilde{o}_i = 2\,m_1\,x_i - m_3\,y_i - m_2\,z_i$, solve for integers $k_i$ via modular inverses in the combined modulus $m_2 m_3$.

3. **Build the lattice**  
   Encode the linear relations among the last few $\tilde{o}_i$ into a lattice basis. For example, a 7×7 Kannan‑embedding matrix might look like:

$$
\begin{pmatrix}
1 & 0 & 0 & 0 & C & A C & B C + A^2 C\\
0 & 1 & 0 & 0 & B & C   & B^2 + A C\\
0 & 0 & 1 & 0 & A & B + A^2 & 2 A B + A^3\\
0 & 0 & 0 & m_1 m_2 m_3 & 0 & 0 & 0\\
0 & 0 & 0 & 0 & m_1 m_2 m_3 & 0 & 0\\
0 & 0 & 0 & 0 & 0 & m_1 m_2 m_3 & 0\\
0 & 0 & 0 & 0 & 0 & 0 & t
\end{pmatrix},
$$

where $t$ is the embedding factor that converts the CVP into an SVP.

4. **Apply LLL**
Run LLL on the constructed matrix. The shortest vectors correspond to the true state differences; from those we recover $(x_i,y_i,z_i)$ and verify by regenerating outputs.

## Solution Code

```python
import itertools
import random
import os
from sage.all import matrix, ZZ

def urand(b):
    return int.from_bytes(os.urandom(b), byteorder='big')

class PRNG:
    def __init__(self):
        # Define moduli
        self.m1 = 2**32 - 107
        self.m2 = 2**32 - 5
        self.m3 = 2**32 - 209
        self.M  = 2**64 - 59

        # Precompute
        self.m23  = self.m2 * self.m3
        self.m123 = self.m1 * self.m2 * self.m3
        self.u    = pow(2 * self.m1**2, -1, self.m23)

        # Fixed CRT coefficients
        self.A = 44560127569626536334684692547
        self.B = 54178077656689068068903612461
        self.C = 2714806752854611792965139512

        # Random state and recurrence taps
        rnd = random.Random(b'rbtree')
        self.a1 = [rnd.getrandbits(20) for _ in range(3)]
        self.a2 = [rnd.getrandbits(20) for _ in range(3)]
        self.a3 = [rnd.getrandbits(20) for _ in range(3)]
        self.x  = [urand(4) for _ in range(3)]
        self.y  = [urand(4) for _ in range(3)]
        self.z  = [urand(4) for _ in range(3)]

        # Storage for analysis
        self._o = []
        self.k  = []

    def out(self):
        _o = 2*self.m1*self.x[0] - self.m3*self.y[0] - self.m2*self.z[0]
        self._o.append(_o)
        k = -self.u * _o % self.m23
        self.k.append(k)
        # Advance state
        self.x = self.x[1:] + [sum(x*y for x,y in zip(self.x, self.a1)) % self.m1]
        self.y = self.y[1:] + [sum(x*y for x,y in zip(self.y, self.a2)) % self.m2]
        self.z = self.z[1:] + [sum(x*y for x,y in zip(self.z, self.a3)) % self.m3]
        return _o

def solve(outs):
    prng = PRNG()
    m1, m23, m123 = prng.m1, prng.m23, prng.m123
    A, B, C = prng.A, prng.B, prng.C
    u = prng.u

    ks, Ds = [], []
    for o in outs:
        k = -u * o % m23
        ks.append(k)
        if len(ks) > 3:
            ki3, ki2, ki1, ki = ks[-4:]
            D = (-ki*m1 + A*ki3*m1 + B*ki2*m1 + C*ki1*m1) % m123
            Ds.append(D)

    if len(Ds) < 2:
        return None

    D4, D5 = Ds[:2]
    size = 6
    mat = [[0]*size for _ in range(size)]
    mat[0][0] = mat[1][1] = mat[2][2] = 1
    mat[3][3] = 2**32
    mat[4][4] = mat[5][5] = m123
    mat[0][4], mat[1][4], mat[2][4], mat[3][4] = A, B, C, D4
    mat[0][5] = (A*C) % m123
    mat[1][5] = (A + B*C) % m123
    mat[2][5] = (B + C*C) % m123
    mat[3][5] = (C*D4 + D5) % m123

    M = matrix(ZZ, mat).LLL()
    for b in M:
        if abs(b[3]) == 2**32:
            x1, x2, x3 = map(abs, b[:3])
            X1 = x1 + ks[0]*m1
            X2 = x2 + ks[1]*m1
            X3 = x3 + ks[2]*m1

            y1, y2, y3 = X1 % prng.m2, X2 % prng.m2, X3 % prng.m2
            z1, z2, z3 = X1 % prng.m3, X2 % prng.m3, X3 % prng.m3

            new_prng = PRNG()
            new_prng.x = [x1, x2, x3]
            new_prng.y = [y1, y2, y3]
            new_prng.z = [z1, z2, z3]

            if [new_prng.out() for _ in range(len(outs))] == outs:
                return new_prng

    return None

def main():
    hint = bytes.fromhex("8fa6cfc262ce445e6406634ed9ea8635a5e5b997cac47e00cb3061230ba605a51b381a897f4418096b4494d7e1f86121399bd1ffaf25e5c7e5e1df7c443808da79148828517523aab83411b22488ac5975cdc7ed588f69181cdab52135426f7d")
    c    = bytes.fromhex("63437082a76ba7ee56fb0b89b2312d4bf075da3fa43fb55e6b37ea5c1c118cb05a32f07e4cbb4731818152c5c57f8bceefbd261ba1871508")
    orig_outs = [int.from_bytes(hint[8*i:8*i+8], 'big') for i in range(len(hint)//8)]
    print("Original outputs:", orig_outs)

    M = 2**64 - 59
    for qs in itertools.product([1, 0, -1, -2], repeat=5):
        outs = [o + q*M for o,q in zip(orig_outs, qs)]
        prng = solve(outs)
        if prng:
            print("PRNG state successfully recovered!")
            break
    else:
        print("Failed to recover PRNG state.")
        return

    stream = b''.join((prng.out() % M).to_bytes(8, 'big') for _ in range(len(c)//8))
    flag = bytes(x ^ y for x,y in zip(c, stream))
    print("Recovered flag:", flag.decode())

if __name__ == "__main__":
    main()
````

To run:

```bash
sage -python solve.py
```

**Example Output:**

```
Original outputs: [10351189227345953886, 7207557443967682101, …]
PRNG state successfully recovered!
Recovered flag: hd3{cis_building_in_the_uc_abcdef_0000thisisfillerspace}
```

## Conclusion

By leveraging CRT, lattice construction, LLL reduction, and optional Kannan embedding, we fully recover the CMRG’s internal state and predict future outputs to decrypt the flag.

## References

- [Lattice Attacks on Pseudo‑Random Number Generators (ePrint 2021/1204)](https://eprint.iacr.org/2021/1204.pdf)
    
- [Lattice Survey by rkm (PDF)](https://github.com/rkm0959/rkm0959_presents/blob/main/lattice_survey.pdf)
    
- [rkm’s CTF Write‑ups](https://github.com/rkm0959/CTFWriteups)
