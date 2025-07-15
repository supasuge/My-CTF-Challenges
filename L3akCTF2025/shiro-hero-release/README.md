# Shiro Hero
- **Author**: [supasuge](https://github.com/supasuge)
- **Difficulty**: Medium


## Build

**None** - static challenge

## Distributable files

`shiro-hero.tar.xz` contains the following files for the challenge:
- `chal.py`: Generates `output.txt` for the challenge.
- `ecc.py`: ECDSA Implementation with the vulnerable PRNG
- `prng.py`: Xorshiro256++ Python implementation
- `output.txt`: Contains a single signature + message pair, the public key, and the encrypted flag.

## Solution

See [solution](./solution/) for more information. The xorshiro256 state recovery is facilitated using the `z3-solver` python module. The goal is to recover the original state used, then predict the `k` value that was generated and used in the signature generation.