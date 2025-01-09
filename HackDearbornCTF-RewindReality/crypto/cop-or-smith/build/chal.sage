from sage.all import *
from random import randint
from Crypto.Util.number import bytes_to_long

def rsa(msg,e,n):
    return pow(bytes_to_long(msg),e,n)

flag = open('flag.txt','r').read().strip().encode()
tmp = randint(2**1023, 2**1024)
e = 65537
p = next_prime(0xBEEF*tmp+randint(2, 2**500))
q = next_prime(0xDEAD*tmp+randint(2, 2**500))
N =  p*q
print('msg1 = '+str(rsa(b"Can't factor the modulus",e,N)))
print('msg2 = '+str(rsa(b"If you don't know the modulus... ;)",e,N)))
print('flag = '+str(rsa(flag,e,N)))
    