from Crypto.Util.number import *
flag = b"GrizzCTF{FAKE_FLAG}"
p = getPrime(512)
q = getPrime(512)
n = p*q
phi = (p-1)*(q-1)
e = 65537


with open('parameters.txt', 'w') as f:
    f.write(f'p = {p}\nq = {q}\ne = {e}\nn = {n}\n\nciphertext = {pow(bytes_to_long(flag), e, n)}\n\n')
