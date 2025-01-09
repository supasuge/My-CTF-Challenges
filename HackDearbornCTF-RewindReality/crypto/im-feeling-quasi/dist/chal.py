import hashlib
import random
import string
import re
import os
from typing import List, Tuple

N: int = 137

def flag() -> str:
    pth: str = os.path.abspath("flag.txt")
    try:
        with open(pth, "r") as f:
            flag_content: str = f.read().rstrip()
        if not flag_content:
            raise ValueError("You done goofed.")
        return flag_content
    except Exception as e:
        raise Exception(f"Error reading flag: {e}")

def e(x: int) -> int:
    return (5 * x + 7) % N

def get_hash(message: str) -> List[int]:
    hash_obj = hashlib.sha3_256(message.encode())
    return [hash_obj.digest()[i % 32] % N for i in range(N)]

def generate_Q(random_str: str, flag_start: int = 0) -> List[int]:
    Q: List[int] = [random.randint(0, N-1) for _ in range(N)]
    for i, c in enumerate(random_str):
        if flag_start + i < N:
            Q[flag_start + i] = ord(c)
        else:
            raise ValueError("String too long to embed in Q at the specified start index.")
    return Q

def compute_S(H: List[int], Q: List[int]) -> List[int]:
    return [(e(H[i]) + e(Q[i]) + Q[i]) % N for i in range(N)]

def getRndStr(n: int = 30) -> str:
    shake = hashlib.shake_256() # XOF
    shake.update(os.urandom(16))  
    return shake.hexdigest(90)[:n]  

def main() -> None:
    try:
        w_w: str = flag()
        random_string: str = getRndStr()
        hashed_string: str = hashlib.sha3_256(random_string.encode()).hexdigest()
        print(f"Hashed value to match: {hashed_string}")
        
        message: str = input("Enter your message: ")
        H: List[int] = get_hash(message)
        Q: List[int] = generate_Q(random_string, flag_start=0)
        S: List[int] = compute_S(H, Q)
        
        print("H =", H)
        print("S =", S)
        
        user_input: str = input("Enter the secret string to verify: ")
        if hashlib.sha3_256(user_input.encode()).hexdigest() == hashed_string:
            print(f"Flag: {w_w}")
        else:
            print("Incorrect string.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()