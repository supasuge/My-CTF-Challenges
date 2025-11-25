# RBKem-ish? 

- **Author**: [supasuge](https://github.com/supasuge) -- Evan Pardon
- **Difficulty**: $\boxed{\text{Medium}}$
Description: Rubik-ish KEM/DEM with 5x5 layer moves

## Directory

```
/challenge   # Contains {challenge.yml, cipher.py original source, requirements.txt, author_key.json (private/public key pair for the challenge handout)} <-- This is the OG source for the challenge

/player      #  {cipher.py, handout.json} <-- These are the files to distribute to the players for download

/solution    # Solution script
```

## Handout

- `./player/handout.json`: Contains the ciphertext, public key, and necessary metadata to get the flag.
- `./player/cipher.py`: Truncated implementation of the cipher (*CLI removed among other functions*) necessary to reverse/solve.

## Solution

- `./solution/solve.py`: Solution script

```bash
RBKem-V2/solution » ls
handout.json  solve.py
RBKem-V2/solution » ./solve.py handout.json 
flag{...}
```

### Flag format

`flag{...}`


#### Real Flag

```
flag{RBK3m_12_s1mpl3_crt_c0njug4t3}
```

---