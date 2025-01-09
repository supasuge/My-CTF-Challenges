from sympy import Matrix
from colorama import Fore, Style, just_fix_windows_console
import string
just_fix_windows_console()
def decrypt(matrix, words):
    alph = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789_{}"
    char_to_index = {c: i for i, c in enumerate(alph)}
    inverse_matrix = Matrix(matrix).inv_mod(64)
    # this one liner took much longer than I would like to admit to write and get right. Bathe in its glory
    plaintext = ''.join( 
        alph[int(x) % 64]  
        for block_start in range(0, len(words), 8)
        for x in (inverse_matrix * Matrix([char_to_index.get(c, 0) for c in words[block_start:block_start + 8]])).tolist()
        for x in x  
    )
    return plaintext



if __name__ == '__main__':
    SECRET_KEY = [
        [49, 47, 39, 23, 20, 58, 19, 15],
        [53, 14, 48, 23, 16, 17, 12, 22],
        [14, 28, 19, 2, 22, 54, 13, 62],
        [60, 55, 51, 7, 8, 32, 11, 10],
        [13, 52, 29, 14, 18, 48, 5, 16],
        [50, 7, 51, 16, 27, 14, 9, 9],
        [60, 47, 35, 9, 19, 21, 28, 33],
        [13, 16, 59, 35, 57, 39, 48, 58],
    ]

    Ciphertext = "zL9JBZ8k{XCEGC}uioKacFA1EKXrPA}H"

    pt = decrypt(SECRET_KEY, Ciphertext).rstrip('x')
    print(Fore.GREEN + Style.BRIGHT + pt + Style.RESET_ALL)
