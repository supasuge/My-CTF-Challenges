# 🧙‍♂️ Magical Oracle — Write-up

> "What is magic but mathematics that **sleeps**?  
> Wake it up and it becomes cryptanalysis."

The goal of this challenge is to recover the secret number $\alpha$ that the **Magical Oracle** multiplies into every query and, with it, decrypt the flag.

---

## 1. Challenge in a nutshell

1. A 256-bit prime $p$ is chosen.  
2. A random secret $\alpha \in \mathbb{Z}_p$ is fixed.  
3. For each user query the service:  
   - picks  

$$t \xleftarrow{\$} \mathbb{Z}_p^*$$  
   
   - returns one misleading number
   
$$z = \mathrm{MSB\_Oracle}\bigl(\alpha\,t \bmod p\bigr),$$  
   - allows at most  
   
     $$d = 2 \bigl\lceil \sqrt{n}\bigr\rceil + 3$$  
     queries (here $d = 35$).  
4. The flag is encrypted with $\mathrm{key} = \mathrm{SHA256}(\alpha)$ using AES–CBC and shown to the attacker.

The MSB oracle does **not** leak the exact most-significant bits; instead it returns a value *close* to the real product. Internally it draws many random candidates until

$$
  \bigl|x - z\bigr| < \frac{p}{2^{\,k+1}}, 
  \quad 
  k = \bigl\lfloor \sqrt{n}\bigr\rfloor + n + 1.
$$

Hence the error is bounded by

$$
  \bigl|\alpha\,t - z\bigr| < 2^{-\,(k+1)}\,p
  \quad(\bmod\,p).
$$

Because $k$ is large, the error is *tiny* compared to $p$, and we face a variant of the **Hidden Number Problem** (HNP).

---

## 2. Modelling as HNP

For each query we have an unknown signed error $e_i$ with

$$
  z_i \equiv \alpha\,t_i - e_i \pmod{p},\quad |e_i|<\frac{p}{2^{k+1}}.
$$

Bring everything to the integers by choosing representatives in $(-\tfrac p2,\tfrac p2)$:

$$
  \alpha\,t_i - z_i \equiv e_i \pmod{p},\quad |e_i|\ll p.
$$

We now possess $d$ linear equations:

$$
\begin{aligned}
  t_1\,\alpha - z_1 &= e_1,\\
  &\vdots\\
  t_d\,\alpha - z_d &= e_d.
\end{aligned}
$$

Our task is to recover $\alpha$ given small errors $e_i$. Construct the lattice

$$\mathcal{L}= L{\,(p\,e_1,\dots,p\,e_d,\;t_1\alpha - z_1,\dots,t_d\alpha - z_d,\;\alpha)\;\Bigm|\;\alpha\in\mathbb{Z}}\;\subset\;\mathbb{Z}^{d+1}.$$

with the following $(d+1)\times(d+1)$ integer basis:

$$
  B = 
  \begin{pmatrix}
    p     & 0     & \cdots & 0     & 0 \\
    0     & p     & \cdots & 0     & 0 \\
    \vdots&       & \ddots &       & \vdots \\
    0     & 0     & \cdots & p     & 0 \\
    t_1   & t_2   & \cdots & t_d   & p
  \end{pmatrix}.
$$

The target vector is

$$
\text{Target vector: }
\mathbf y = 
\begin{pmatrix}z_1 \\ z_2 \\ \vdots \\ z_d \\ 0\end{pmatrix}
\in\ \mathbb{Z}^{d+1}.
$$


$\mathbf y$ is *almost* in the lattice; the difference encodes the small errors and the secret. Solving the (approximate) **Closest Vector Problem** (CVP) against $\mathcal L$ yields the last coordinate $\alpha$ *for free*.

---

## 3. Solving CVP quickly

1. **Reduce** the basis with LLL.  
2. **Nearest-plane (Babai)**: project the target successively onto the Gram–Schmidt vectors, rounding the coefficients.  
3. Read $\alpha$ from the last coordinate of the resulting lattice vector and reduce $\bmod p$.

Because the matrix is only $36\times36$ and entirely integral, the whole LLL+Babai step takes $\ll1$s on a modern laptop.

---

## 4. Implementation highlights

| File                 | Purpose                                |
| -------------------- | -------------------------------------- |
| `src/chal.py`        | the vulnerable oracle & flag encryptor |
| `solution/solve.py`  | original Sage-based solver             |
| `solution/solve2.py` | annotated & slightly cleaner variant   |

### 🚀 Speed tricks

* **Pipelined queries** — send all `1\n` requests at once to kill network RTT.  
* **Integer basis** — multiply the fractional row by $p$ so LLL works in $\mathbb Z$ not $\mathbb Q$.  
* **Optional**: switch to `fpylll` for up to $10\times$ faster lattice ops.

---

## 5. Usage

```bash
# install deps (Debian/Ubuntu)
apt-get install sage python3-venv
python3 -m venv venv && . venv/bin/activate
pip install -r requirements.txt   # Crypto, pwntools, sage-conf etc.

# local test — launches challenge and solves it
python3 solution/solve2.py

# against remote
python3 solution/solve2.py chall.host 1338
```
Total runtime ≈ **3.6 s**, dominated by the challenge's deliberate \$0.1,\$s delay per query.

---

## 6. References

* Adi Shamir, **How to share a secret**, *Communications of the ACM* 1979.
* Oded Regev, lecture notes on lattices & Babai's nearest-plane, NYU 2004.
* Boneh & Venkatesan, **Breaking RSA given a small fraction of the private key bits**, CRYPTO '98.
