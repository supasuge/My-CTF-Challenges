# Mersenne Mayhem
- **Author**: [supasuge](https://github.com/supasuge) 
- **Difficulty**: Hard
- **Category**: Cryptography
- **500 Points**

## Challenge inspiration

https://eprint.iacr.org/2024/2080.pdf



- Challenge present's a slightly modified version of the AJPS Cryptosystem in order to facilitate the attack describe in ["Improved Lattice-Based Attack on Mersenne Low Hamming Ratio Search Problem"](https://eprint.iacr.org/2024/2080.pdf).

## Description

- Ever wondered what happens when Mersenne primes hit the gym? In this challenge, you'll put $f$ and $g$ through a brutal popcount workout, then rip them apart with your lattice reduction deadlift... I suppose? Just roll with it.

## Distributable Files

Archive to distribute: `dist/mersenne-mayhem.tar.xz`

**Contents**:

- `build/chal.py`: The challenge generation script
- `build/output.txt`: The challenge output

## Flag
L3ak{4jp2_n0t_s0_str0ng}

## Build

*None... Static challenge*

## Solution

[solve.py](./solution/solve.py)
- Run with: `sage -python solve.py`

**Output from `solve.py`**

```bash
[+] Starting attack with p = 28141120136973731333…67391476087696392191 (len=3376), h = 14205552563390290076…27648438450206074052 (len=3376), xi1 = 0.31, xi2 = 0.69, w = 10
[+] Attempting s = 5 (small roots approach) with X=24507320357134538577…01532531280973922304 (len=1047), Y=11482740555423139906…61487542019554279424 (len=2330)
[+] Generating shifts...
[+] Matrix dimensions: 6 x 6
Matrix Structure: (X=non-zero, O=zero)
00 X X X X X X ~
01 0 X X X X X ~
02 0 0 X X X X ~
03 0 0 0 X X X ~
04 0 0 0 0 X X ~
05 0 0 0 0 0 X ~
[+] Reducing a 6 x 6 lattice...
[+] Reducing a 6 x 6 lattice within 0.388 seconds...
[+] Matrix dimensions: 6 x 6
Matrix Structure: (X=non-zero, O=zero)
00 X X X X X X ~
01 X X X X X X 
02 X X X X X X 
03 X X X X X X ~
04 X X X X X X 
05 X X X X X X 
[+] Reconstructing polynomials (divide_original = True, modulus_bound = True, divide_gcd = True)...
[+] Reconstructed 6 polynomials
[+] g = -2163128425954716378…39082633055436800000 (len=50659)
[+] Finding roots within 11.352 seconds...
[+] Found candidate root!
[+] x0 = 12001483498621637948…03976318475074273280 (len=1047)
[+] y0 = 29310043358604083666…09662490459805581313 (len=2329)
[+] Recovered f = 12001483498621637948…03976318475074273280 (len=1047)
[+] Recovered g = 29310043358604083666…09662490459805581313 (len=2329)
[+] Derived AES key (int) = 35176400171217164167…42415126361423216640 (len=3375)
[+] Actual derived AES key (hex) = d22ac31486cebc83af2ad4916db28a67a5d63c5e211fc7dad672e0321daef593
[+] Decrypting ciphertext...
[+] Recovered Flag = L3ak{4jp2_n0t_s0_str0ng}
[+] Total time taken: 12.074 seconds
```

### Writeup coming soon...
