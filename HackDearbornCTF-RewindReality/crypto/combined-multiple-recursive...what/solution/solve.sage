import itertools
import random
import os
from sage.all import matrix, ZZ  

def urand(b):
    return int.from_bytes(os.urandom(b), byteorder='big')

class PRNG:
    def __init__(self):
        self.m1 = 2 ** 32 - 107
        self.m2 = 2 ** 32 - 5
        self.m3 = 2 ** 32 - 209
        self.M = 2 ** 64 - 59
        self.m23 = self.m2 * self.m3
        self.m123 = self.m1 * self.m2 * self.m3
        self.u = pow(2 * self.m1**2, -1, self.m23)  # Use built-in pow for modular inverse

        rnd = random.Random(b'rbtree')

        self.a1 = [rnd.getrandbits(20) for _ in range(3)]
        self.a2 = [rnd.getrandbits(20) for _ in range(3)]
        self.a3 = [rnd.getrandbits(20) for _ in range(3)]
        
        self.A = 44560127569626536334684692547
        self.B = 54178077656689068068903612461
        self.C = 2714806752854611792965139512

        self.x = [urand(4) for _ in range(3)]
        self.y = [urand(4) for _ in range(3)]
        self.z = [urand(4) for _ in range(3)]

        self._x = []
        self.k = []
        self._o = []
        self.D = []

    def out(self):
        _o = 2 * self.m1 * self.x[0] - self.m3 * self.y[0] - self.m2 * self.z[0]
        self._o.append(_o)
        k = -self.u * _o % self.m23
        self.k.append(k)
        o = _o % self.M

        self._x.append(self.x[0])

        self.x = self.x[1:] + [sum(x * y for x, y in zip(self.x, self.a1)) % self.m1]
        self.y = self.y[1:] + [sum(x * y for x, y in zip(self.y, self.a2)) % self.m2]
        self.z = self.z[1:] + [sum(x * y for x, y in zip(self.z, self.a3)) % self.m3]

        return _o

def solve(outs):
    prng = PRNG()

    a1 = prng.a1
    a2 = prng.a2
    a3 = prng.a3

    m1 = prng.m1
    m2 = prng.m2
    m3 = prng.m3
    m23 = prng.m23
    m123 = prng.m123
    M = prng.M

    u = prng.u
  
    A = prng.A
    B = prng.B
    C = prng.C

    ks = []
    Ds = []

    for o in outs:
        k = -u * o % m23
        ks.append(k)

        if len(ks) > 3:
            ki3, ki2, ki1, ki = ks[-4:]
            D = (-ki * m1 + A * ki3 * m1 + B * ki2 * m1 + C * ki1 * m1) % m123
            Ds.append(D)

    if len(Ds) < 2:
        return None  # Not enough D values to proceed

    D4, D5 = Ds[0:2]

    size = 6
    mat = [
        [0 for _ in range(size)] for _ in range(size)
    ]

    mat[0][0] = 1
    mat[1][1] = 1
    mat[2][2] = 1
    mat[3][3] = 2**32
    mat[4][4] = m123
    mat[5][5] = m123

    mat[0][4] = A
    mat[1][4] = B
    mat[2][4] = C
    mat[3][4] = D4

    mat[0][5] = (A * C) % m123
    mat[1][5] = (A + C * B) % m123
    mat[2][5] = (B + C**2) % m123
    mat[3][5] = (C * D4 + D5) % m123

    mat = matrix(ZZ, mat)

    for b in mat.LLL():
        if abs(b[3]) == 2**32:
            x1, x2, x3 = list(map(abs, b[:3]))
            X1 = x1 + ks[0] * m1
            X2 = x2 + ks[1] * m1
            X3 = x3 + ks[2] * m1

            y1, y2, y3 = X1 % m2, X2 % m2, X3 % m2
            z1, z2, z3 = X1 % m3, X2 % m3, X3 % m3

            new_prng = PRNG()
            new_prng.x = [x1, x2, x3]
            new_prng.y = [y1, y2, y3]
            new_prng.z = [z1, z2, z3]

            # Verify the state by generating outputs
            _outs = [new_prng.out() for _ in range(12)]
            if _outs[:len(outs)] == outs:
                print(f"Recovered state: x={new_prng.x}, y={new_prng.y}, z={new_prng.z}")
                return new_prng

    return None

def main():
    hint = "8fa6cfc262ce445e6406634ed9ea8635a5e5b997cac47e00cb3061230ba605a51b381a897f4418096b4494d7e1f86121399bd1ffaf25e5c7e5e1df7c443808da79148828517523aab83411b22488ac5975cdc7ed588f69181cdab52135426f7d"
    c = "63437082a76ba7ee56fb0b89b2312d4bf075da3fa43fb55e6b37ea5c1c118cb05a32f07e4cbb4731818152c5c57f8bceefbd261ba1871508"

    hint = bytes.fromhex(hint)
    c = bytes.fromhex(c)

    orig_outs = [int.from_bytes(hint[8*i:8*i+8], "big") for i in range(len(hint) // 8)]

    print("Original outputs:", orig_outs)

    M = 2 ** 64 - 59

    # Iterate over possible k offsets
    for qs in itertools.product([1, 0, -1, -2], repeat=5):
        outs = [o + q * M for o, q in zip(orig_outs, qs)]
        new_prng = solve(outs)

        if new_prng is not None:
            print("PRNG state successfully recovered!")
            break
    else:
        print("Failed to recover PRNG state.")
        return

    # Generate the stream to decrypt the flag
    stream = b''
    for i in range(len(c) // 8):
        stream += (new_prng.out() % M).to_bytes(8, "big")
    
    # XOR the stream with the ciphertext to get the flag
    out = bytes([x ^ y for x, y in zip(c, stream)])
    print("Recovered flag:", out.decode())

if __name__ == "__main__":
    main()
