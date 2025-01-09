flag = '[REDACTED]'
###############################################################################################
#RESOURCES:
#https://inventwithpython.com/hacking/chapter21.html
#https://www.cipherchallenge.org/wp-content/uploads/2020/12/Five-ways-to-crack-a-Vigenere-cipher.pdf
#https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher
###############################################################################################
import string
uppers = string.ascii_uppercase
def encrypt(pt, key):
	ct = ''
	for i in range(len(pt)):
		p = uppers.index(pt[i])
		k = uppers.index(key[i%len(key)])
		c = (p + k) % 26
		ct += uppers[c]
	return ct
KNOWNPLAINTEXT = 'GRIZZLYBEARCTF ILOVEGRIZZLY BEARSGRIZZLY BEARS AND CTF MAKES ME HAPPY'
KNOWNPLAINTEXT = KNOWNPLAINTEXT.replace(' ', '')
enc = encrypt(flag+KNOWNPLAINTEXT, '[REDACTED]')
print(enc)
with open('ciphertext.txt', 'w') as f:
    f.write("Ciphertext: " + enc + '\n\n')
    f.write("Key: " + "[REDACTED]"+ "\n\n")
    f.write("HINT: please note that '{' and '}' have been removed from the flag.\nThe flag format is all capital letters and begins with GRIZZCTF..............")

