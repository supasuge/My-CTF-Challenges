# Combined multiple recursive ... what? 

# Introduction

This challenge involve's attacking the linearity of a CMRG (Combined Multiple Recursive Generator). You can find the original attack paper in section 5 of [this](https://eprint.iacr.org/2021/1204.pdf) paper. I'd like to note I didn't create the original source code for this challenge and I don't want to take credit for someone else's work. The source code for this challenge was from an older CTF a few years ago (2021), and if you do some research you'll find they are basically the same aside from parameters being changed slightly to make the challenge a bit easier and obviously the flag. The writeup's available are all in foreign langauges I don't understand and I'm too lazy to translate via google translate becease when LaTex is involved it's always a headache... I was able to understand what the author/s implied via the math  though, so that was more-so the core inspiration of the challenge.

While sadly this challenge didn't get any solves throughout the hackathon,  below is the explaination as to the solution of this challenge + solution code: 


## CMRG

CMRG is a PRNG (Pseudo Random Number Generator) that combines two Linear Congruential Generators (LCGs). Given two coprime moduli, $m_1$ and $m_2$, the structure is as follows:

$$
x_i = a_{11} x_{i-1} + a_{12} x_{i-2} + a_{13} x_{i-3} \mod m_1
$$
$$
y_i = a_{21} y_{i-1} + a_{22} y_{i-2} + a_{23} y_{i-3} \mod m_2
$$
$$
z_i = x_i - y_i \mod m_1
$$

The output is $z_i$, and the values of $m_1$ and $m_2$ are of similar size. This setup raises two important questions:

1. Does the expression $z_i = x_i - y_i \mod m_1$ always resolve correctly without needing further adjustments like $z_i = x_i - y_i + m_1 \mod m_1$?
2. Can the Chinese Remainder Theorem (CRT) be applied to exploit the coprimality of $m_1$ and $m_2$?

---

## Attack steps:
- Part 1: Chinese Remainder Theorem
- Part 2: LLL
- Part 3: Solving using Kannan Embedding

### Part 1 - CRT

Let’s address the second question first. We can define $X_i$ modulo $m_1m_2$ by combining $x_i \mod m_1$ and $y_i \mod m_2$, leveraging the Chinese Remainder Theorem. Let's define $A$, $B$, $C$ as follows:

$$
A = a_{11} \mod m_1, \quad A = a_{21} \mod m_2
$$

$$
B = a_{12} \mod m_1, \quad B = a_{22} \mod m_2
$$

$$
C = a_{13} \mod m_1, \quad C = a_{23} \mod m_2
$$

Using this, we derive the following [recurrence relation](https://en.wikipedia.org/wiki/Recurrence_relation):

$$
X_i = A X_{i-1} + B X_{i-2} + C X_{i-3} \mod m_1m_2
$$

Although we don’t directly know the values of $x_i$ and $y_i$, this formulation allows us to proceed with the attack by reconstructing $X_i$.

### Part 2 - LLL

Now, let’s address the first question about brute-forcing the values of $x_i - y_i$. Since $m_1$ and $m_2$ are of similar size, it’s feasible to brute-force $x_i - y_i$ over a range of potential values.

Let’s define:

$$
z_i' = x_i - y_i
$$

From this, we know that $z_i' = z_i$ or $z_i' = z_i - m_1$. Given $k$ outputs, we can try $2^k$ combinations to identify the correct sequence.

Next, observe that for integers $k_i$ and $\hat{k_i}$, we know:

$$
X_i = k_i m_1 + x_i = \hat{k_i} m_2 + y_i
$$

Since $z_i' = x_i - y_i$, this implies:

$$
z_i' = x_i - y_i = \hat{k_i} m_2 - k_i m_1
$$

Thus, we can compute:

$$
k_i = -z_i' m_1^{-1} \mod m_2
$$

At this point, we can construct a **lattice** to encapsuate these linear relationships and solve for $x_i$, $y_i$, and $z_i$ using the **Lenstra–Lenstra–Lovász (LLL) algorithm**. The lattice is constructed using the relation:

$$
P_i(v_i, v_{i+1}, v_{i+2}, v_{i+3}) = k_{i+3}m_1 + v_{i+3} - A(k_{i+2}m_1 + v_{i+2}) - B(k_{i+1}m_1 + v_{i+1}) - C(k_im_1 + v_i)
$$

This allows us to set up a system of linear equations. The next step is solving this lattice system using LLL.

When defining the basis of the lattice, think about the value $v$ that satisfies it, we can define a lattice based off of this. For example  if we define a lattice for $v_0$, $v_1$, $v_2$, $v_3$, we get:

$$
\begin{pmatrix}
1 & 0 & 0 &  & C \\
0 & 1 & 0 &  & B \\
0 & 0 & 1 &  & A \\
0 & 0 & 0 & m_1 & m_2
\end{pmatrix}
$$

The key point here is that it's not always available through this.. This wont't work. The range of answers that performing LLL reduction can feasibly produce is proportional to the size of the lattice's determinant that you define. If you want to be more precise here, you'll need to increase the size of the lattice. Luckily, it's possible to go one step further and define expressions for $v_0$, $v_1$, $v_2$, $v_3$, $v_4$, and $v_5$. In this case, you can define $v_3$, $v_4$, and $v_5$ as equations for $v_0$, $v_1$, and $v_2$. 

Here's what the resulting lattice basis should look like:


$$
\begin{pmatrix}
1 & 0 & 0 & C & AC & BC + A^{2}C \\
0 & 1 & 0 & B & C & B^{2} + AC \\
0 & 0 & 1 & A & (B + A^{2})C & 2AB + A^{3} \\
0 & 0 & 0 & m_1 m_2 & 0 & 0 \\
0 & 0 & 0 & 0 & m_1 m_2 & 0 \\
0 & 0 & 0 & 0 & 0 & m_1 m_2
\end{pmatrix}
$$

You can go even further with a 7x7 lattice:

$$
\begin{pmatrix}
1 & 0 & 0 & C & AC & BC + A^2C & C^2 + 2ABC + A^3C \\
0 & 1 & 0 & B & C & B^2 + AC & 2BC + AB^2 + A^2C \\
0 & 0 & 1 & A & (B + A^2)C & 2AB + A^3 & 2AC + B^2 + 2A^2B + A^4 \\
0 & 0 & 0 & m_1 m_2 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & m_1 m_2 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & m_1 m_2 & 0
\end{pmatrix}
$$

As you stretch it out, the range of answers is proportional to the size of lattice (sqrt). In other words, the last lattice is $\sqrt 7$, $\sqrt 4$ times more accurate than the first.

### Part 3 (Optional) - Kannan Embedding

- In order to make the challenge slightly easier for participants, because of the parameter adjustment's made, utilizing kannan embedding's is not needed to achieve the level of accuracy needed to get the flag and solve the challenge here, LLL is able recover the parameter's needed to recover the state of the PRNG on it's own just fine here.
 
To improve the accuracy of our solution, we use **Kannan Embedding**, which transforms a **Closest Vector Problem (CVP)** into a **Shortest Vector Problem (SVP)** by embedding the target vector into the lattice, see the pdf from the resources for more info on this. The key idea behind Kannan Embedding is to extend the original lattice by adding an extra row and column, creating an embedding matrix. The embedding factor, $t$, plays a crucial role in scaling the lattice for accurate recovery.

The matrix is extended as follows:

$$
\left( \begin{matrix}
    1 & 0 & 0 & 0 & A & A \cdot C \\
    0 & 1 & 0 & 0 & B & A + C \cdot B \\
    0 & 0 & 1 & 0 & C & B + C^2 \\
    0 & 0 & 0 & 2^{32} & D_4 & C \cdot D_4 + D_5 \\
    0 & 0 & 0 & 0 & m_{123} & 0 \\
    0 & 0 & 0 & 0 & 0 & t
\end{matrix} \right)
$$

Here:

- $A$, $B$, $C$ are the recurrence coefficients from the CMRG.
- $D_4$, $D_5$ are derived from the values of the brute-forced $k_i$ values using the recursive relations.
- $m_{123} = m_1 \cdot m_2 \cdot m_3$ is the product of the moduli involved in the CMRG.
- $t$ is the embedding factor, which helps scale the lattice.

By embedding the target vector $D$ into this extended matrix, we can transform the **CVP** into a **SVP**, which the **LLL algorithm** can solve with greater accuracy. The additional "answer row" ($t$) helps account for the scaling, ensuring that the recovered values for $x_i$, $y_i$, and $z_i$ lie within the correct bounds of the lattice structure. Once we have the recovered state from the reduced lattice that has been reduced via LLL, we can easily predict the next output and then get the flag! Below is my full solution for it.

For more details on Kannan Embedding, refer to rkm’s [Lattice Survey](https://github.com/rkm0959/rkm0959_presents/blob/main/lattice_survey.pdf).


> Note: It's possible some of the math is off in this, I am still learning latex. The paper was pretty complex... To be fair all things considered, a easier challenge likely would've been better suited given the fact people only had 24 hours for both the CTF and making their hackathon projects... Ya live and ya learn

### Extracting the State with LLL 

By applying LLL to the constructed lattice, we aim to recover the values $x_i$, $y_i$, and $z_i$. After obtaining these, the PRNG state can be reconstructed. Given the recovered state, we generate future outputs to verify that we have obtained the original state of the PRNG and use this to predict the next values and successfully decrypt the ciphertext to retrieve the flag.

Below is the solution code used to recover the original state and flag:

**Solution Implementation Code**:

```python
import itertools
import random
import os
from sage.all import matrix, ZZ  

def urand(b):
    return int.from_bytes(os.urandom(b), byteorder='big')

class PRNG:
    def __init__(self):
        # Define moduli for the CMRG-based PRNG
        self.m1 = 2 ** 32 - 107
        self.m2 = 2 ** 32 - 5
        self.m3 = 2 ** 32 - 209
        self.M = 2 ** 64 - 59  # Large modulus for output space

        # Precompute modular products for ease of calculation
        self.m23 = self.m2 * self.m3
        self.m123 = self.m1 * self.m2 * self.m3

        # Modular inverse for solving congruence equations using CRT
        self.u = pow(2 * self.m1**2, -1, self.m23)

        # Random seed for reproducibility in challenge
        rnd = random.Random(b'rbtree')

        # Random coefficients for each PRNG component
        self.a1 = [rnd.getrandbits(20) for _ in range(3)]
        self.a2 = [rnd.getrandbits(20) for _ in range(3)]
        self.a3 = [rnd.getrandbits(20) for _ in range(3)]

     
        self.A = 44560127569626536334684692547
        self.B = 54178077656689068068903612461
        self.C = 2714806752854611792965139512

        # Initial random state values for x, y, z in the PRNG
        self.x = [urand(4) for _ in range(3)]
        self.y = [urand(4) for _ in range(3)]
        self.z = [urand(4) for _ in range(3)]

        # Storage for values needed for LLL and lattice calculations
        self._x = []
        self.k = []
        self._o = []
        self.D = []

    def out(self):
        # Compute the next output as a function of the current PRNG state
        _o = 2 * self.m1 * self.x[0] - self.m3 * self.y[0] - self.m2 * self.z[0]
        self._o.append(_o)

        # Compute the "k" value based on modular inverse of m1
        k = -self.u * _o % self.m23
        self.k.append(k)

        # Compute the actual output modulo M
        o = _o % self.M

        # Store the first x value for lattice attack
        self._x.append(self.x[0])

        # Update x, y, and z values using LCG recurrence relation
        self.x = self.x[1:] + [sum(x * y for x, y in zip(self.x, self.a1)) % self.m1]
        self.y = self.y[1:] + [sum(x * y for x, y in zip(self.y, self.a2)) % self.m2]
        self.z = self.z[1:] + [sum(x * y for x, y in zip(self.z, self.a3)) % self.m3]

        return _o  # Return the unmodded value for lattice attack


def solve(outs):
    # Initialize a PRNG instance to retrieve moduli and coefficients
    prng = PRNG()

    a1 = prng.a1
    a2 = prng.a2
    a3 = prng.a3

    # Extract moduli values from PRNG
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

    ks = []  # Store k values
    Ds = []  # Store D values

    # Step 1: Compute 'k' values and 'D' differences
    for o in outs:
        k = -u * o % m23
        ks.append(k)

        if len(ks) > 3:
            ki3, ki2, ki1, ki = ks[-4:]  # Use the last 4 values for recursion
            # Calculate the difference D using the recursive relations from CMRG
            D = (-ki * m1 + A * ki3 * m1 + B * ki2 * m1 + C * ki1 * m1) % m123
            Ds.append(D)

    if len(Ds) < 2:
        return None  # Not enough D values to proceed with lattice attack

    # Step 2: Set up the matrix for LLL and Kannan Embedding
    D4, D5 = Ds[0:2]

    size = 6
    mat = [
        [0 for _ in range(size)] for _ in range(size)
    ]

    # Set up the diagonal of the matrix
    mat[0][0] = 1
    mat[1][1] = 1
    mat[2][2] = 1
    mat[3][3] = 2**32  # Scale for LLL
    mat[4][4] = m123  # Moduli product for lattice relations
    mat[5][5] = m123

    # Fill in off-diagonal elements based on CMRG recurrence
    mat[0][4] = A
    mat[1][4] = B
    mat[2][4] = C
    mat[3][4] = D4

    # Kannan Embedding to improve lattice precision
    mat[0][5] = (A * C) % m123
    mat[1][5] = (A + C * B) % m123
    mat[2][5] = (B + C**2) % m123
    mat[3][5] = (C * D4 + D5) % m123

    # Convert to SageMath matrix and apply LLL algorithm
    mat = matrix(ZZ, mat)

    # Step 3: Solve using LLL and extract potential solutions
    for b in mat.LLL():
        if abs(b[3]) == 2**32:  # We expect this from the structure of the lattice
            # Recover potential x values
            x1, x2, x3 = list(map(abs, b[:3]))
            X1 = x1 + ks[0] * m1
            X2 = x2 + ks[1] * m1
            X3 = x3 + ks[2] * m1

            # Recover y and z values mod m2 and m3
            y1, y2, y3 = X1 % m2, X2 % m2, X3 % m2
            z1, z2, z3 = X1 % m3, X2 % m3, X3 % m3

            # Create a new PRNG instance with recovered state
            new_prng = PRNG()
            new_prng.x = [x1, x2, x3]
            new_prng.y = [y1, y2, y3]
            new_prng.z = [z1, z2, z3]

            # Verify if the PRNG produces the correct outputs
            _outs = [new_prng.out() for _ in range(12)]
            if _outs[:len(outs)] == outs:
                print(f"Recovered state: x={new_prng.x}, y={new_prng.y}, z={new_prng.z}")
                return new_prng

    return None  # No solution found


def main():
    hint = "8fa6cfc262ce445e6406634ed9ea8635a5e5b997cac47e00cb3061230ba605a51b381a897f4418096b4494d7e1f86121399bd1ffaf25e5c7e5e1df7c443808da79148828517523aab83411b22488ac5975cdc7ed588f69181cdab52135426f7d"
    c = "63437082a76ba7ee56fb0b89b2312d4bf075da3fa43fb55e6b37ea5c1c118cb05a32f07e4cbb4731818152c5c57f8bceefbd261ba1871508"

    hint = bytes.fromhex(hint)
    c = bytes.fromhex(c)

    orig_outs = [int.from_bytes(hint[8*i:8*i+8], "big") for i in range(len(hint) // 8)]

    print("Original outputs:", orig_outs)

    M = 2 ** 64 - 59

    # Iterate over possible k offsets to adjust output values
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
```
**Output**
```bash
$ sage -python solve.sage
Original outputs: [10351189227345953886, 7207557443967682101, 11954164847517924864, 14641309191728661925, 1961346815567861769, 7729466515404644641, 4151142377637406151, 16564766629258856666, 8724748084870194090, 13273253458582482009, 8488660694870223128, 2079173332216999805]
Recovered state: x=[2419149198, 3192020048, 141140992], y=[1471382717, 683754360, 2693572653], z=[3179792952, 523571653, 3240750066]
PRNG state successfully recovered!
Recovered flag: hd3{cis_building_in_the_uc_abcdef_0000thisisfillerspace}
```
### Conclusion

By applying CRT, LLL, and Kannan Embedding for improved accuracy, the attack successfully breaks the CMRG-based PRNG to retrieve the flag.

#### Resources Used

- [Lattice Attacks on Pseudo-Random Number Generators](https://eprint.iacr.org/2021/1204.pdf)
- [Lattice Survey by rkm](https://github.com/rkm0959/rkm0959_presents/blob/main/lattice_survey.pdf)



