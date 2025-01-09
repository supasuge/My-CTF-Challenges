# Source: https://asecuritysite.com/rsa/rsa_ctf05
from Crypto.Util.number import long_to_bytes,bytes_to_long
from Crypto import Random
import Crypto
import sys
from math import isqrt
from sympy import *
def get_prime(bits):
	p = Crypto.Util.number.getPrime(bits, randfunc=Crypto.Random.get_random_bytes)
	return(p)
# Rational numbers have finite a continued fraction expansion.
def get_cf_expansion(n, d):
    e = []
    q = n // d
    r = n % d
    
    e.append(q)

    while r != 0:
        n, d = d, r           
        q = n // d
        r = n % d
        e.append(q)

    return e
def get_convergents(e):
    n = [] # Nominators
    d = [] # Denominators

    for i in range(len(e)):
        if i == 0:
            ni = e[i]
            di = 1
        elif i == 1:
            ni = e[i]*e[i-1] + 1
            di = e[i]
        else: # i > 1 
            ni = e[i]*n[i-1] + n[i-2]
            di = e[i]*d[i-1] + d[i-2]

        n.append(ni)
        d.append(di)
        yield (ni, di)

e=61336805061905097474417011455193524797254971888565645666860365904642741779403477399958927615688492448890022571949798977345765227762189378864176951092164382089441760319241575186982662794859913550335793613730480069338185265005029387527636766435083605441641318234017860128684522772035254944500861589321854851587
N = 89064083881775910820550079914844856977203453886412845001241596026336961628568577688293401882523604026054072081596120516322225801770979877495114585869622430261707927628332858377117246211603069760700155869512330536539174465531778987098787076673452294046885555217663973561674718964832364914081912058870509052651
C=37347626706878089353146924651540581875610509711537951406049498556070969325635825746790654588609775943235597472808879800479975073171100823190151496479163476463301590816394458939604279638812986325794482458980532009666867512884889029654139881985279387567450333815571572723730648891954766697113837917434460587952


print(f' The public exponent (e) is {e}\n\b the public modulus (N) is {N}\n\n Ciphertext: {C}')

cf_expansion = get_cf_expansion(e, N)
convergents = get_convergents(cf_expansion)

for pk, pd in convergents: # pk - possible k, pd - possible d
	if pk == 0:
		continue;

	possible_phi = (e*pd - 1)//pk

	p = Symbol('p', integer=True)
	roots = solve(p**2 + (possible_phi - N - 1)*p + N, p)

	if len(roots) == 2:
		pp, pq = roots # pp - possible p, pq - possible q
		if pp*pq == N:
			print('\n--Found factors of N using Wiener attack--!!--\n')
			d=pow(e,-1,possible_phi)
			print('\nFound d:',d)
			print('\nFound p:',pp)
			print('\nFound q:',pq)
			print('\nFound PHI:',possible_phi)
			print('Now using C^d mod N')
			M=pow(C,d,N)
			print(f"\nDecrypted message found!: {long_to_bytes(M)}")
			sys.exit(0)

print('[-] Wiener\'s Attack failed; Could not factor N')
sys.exit(1)