from base64 import b64decode, b32decode
path = '../src/ciphertext.txt'
with open(path, 'r') as f:
    ciphertext = f.read()

# Reverse the encoding steps
decoded_base32 = b32decode(ciphertext)
decoded_base64 = b64decode(decoded_base32)

flag = decoded_base64.decode()
print(flag)
