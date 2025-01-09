import string
from collections import defaultdict
from tabulate import tabulate
import itertools


class KasiskiExamination:
    def __init__(self, ciphertext):
        self.ciphertext = ciphertext

    def find_repeated_sequences(self):
        """Finds repeated sequences in the ciphertext and the distances between their occurrences."""
        spacings = defaultdict(list)
        for seq_len in range(3, 6):
            for i in range(len(self.ciphertext) - seq_len):
                seq = self.ciphertext[i:i + seq_len]
                for j in range(i + seq_len, len(self.ciphertext) - seq_len):
                    if self.ciphertext[j:j + seq_len] == seq:
                        spacings[seq].append(j - i)
        return spacings

    def find_key_length(self):
        """Finds the likely key length based on the spacings of repeated sequences."""
        spacings = self.find_repeated_sequences()
        distance_factors = defaultdict(int)
        for seq, spaces in spacings.items():
            for space in spaces:
                for factor in range(2, min(space, 10)):
                    if space % factor == 0:
                        distance_factors[factor] += 1

        likely_key_length = max(distance_factors, key=distance_factors.get)
        return likely_key_length

class VigenereBruteForce:
    def __init__(self, ciphertext, key_length):
        self.ciphertext = ciphertext
        self.key_length = key_length

    def vigenere_decrypt(self, ciphertext, key):
        """Decrypts a Vigenère cipher using the given key."""
        key_length = len(key)
        key_as_int = [ord(i) for i in key]
        ciphertext_int = [ord(i) for i in ciphertext]
        plaintext = ''
        for i in range(len(ciphertext_int)):
            value = (ciphertext_int[i] - key_as_int[i % key_length]) % 26
            plaintext += chr(value + 65)
        return plaintext

    def brute_force_vigenere(self, target_sequence):
        """Brute-force Vigenère cipher, looking for a specific sequence in the plaintext."""
        possible_keys = [''.join(k) for k in itertools.product(string.ascii_uppercase, repeat=self.key_length)]
        results = []

        for key in possible_keys:
            plaintext = self.vigenere_decrypt(self.ciphertext, key)
            if target_sequence in plaintext:
                results.append({"Key": key, "Plaintext": plaintext[:50]})  # Display the first 50 characters
                break  # Assuming we stop at the first successful decryption

        return results

# Using the classes to perform the Kasiski Examination and Brute Force the Vigenere Cipher
sample_ciphertext = 'GSKZAETGQUPWOVHLBIRJIHUJESGGSKZANYCGASUIMQVFIRJBZMABFCRTIRJBZMABFCRTCNEETGOALGSNGHBRPZ'
kasiski = KasiskiExamination(sample_ciphertext)
key_length = kasiski.find_key_length() # extract the key length (greatest common divisor of the spacings)
vigenere = VigenereBruteForce(sample_ciphertext, key_length)
print("key length found: ", key_length, "\nBrute forcing the keyspace now...\n")
# Brute-force the cipher looking for the first occurence of "GRIZZCTF" 
brute_force_results = vigenere.brute_force_vigenere("GRIZZCTF")
print(tabulate(brute_force_results, headers="keys"))