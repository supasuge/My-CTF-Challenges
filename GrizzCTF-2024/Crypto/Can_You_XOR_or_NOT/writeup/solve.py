from pwn import xor

ciphertext = "20000000002f2d19190b501116380a590825014100533a134a2c5f5d5107"
key = b"grizzly_bears"


# Perform XOR decryption
flag_bytes = xor(bytes.fromhex(ciphertext), key)

# Print the flag
print(flag_bytes.decode("utf-8"))

