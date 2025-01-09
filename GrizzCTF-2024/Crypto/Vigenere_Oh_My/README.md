# Vigenere?! Oh my...
*250 Points*
**Description:** You have been provided the partial plaintext + the ciphertext, can you solve for the missing plaintext given this information and retrieve the flag?

#### What is the Vigenere Cipher?
This is simply a 26x26 grid version of the caesar cipher (to put it simply).
This cipher works as folows:
(**Vigener Tableu**)
```plaintext
1  ABCDEFGHIJKLMNOPQRSTUVWXYZ
2  BCDEFGHIJKLMNOPQRSTUVWXYZA
3  CDEFGHIJKLMNOPQRSTUVWXYZAB
4  DEFGHIJKLMNOPQRSTUVWXYZABC
5  EFGHIJKLMNOPQRSTUVWXYZABCD
6  FGHIJKLMNOPQRSTUVWXYZABCDE
7  GHIJKLMNOPQRSTUVWXYZABCDEF
8  HIJKLMNOPQRSTUVWXYZABCDEFG
9  IJKLMNOPQRSTUVWXYZABCDEFGH
10 JKLMNOPQRSTUVWXYZABCDEFGHI
11 KLMNOPQRSTUVWXYZABCDEFGHIJ
12 LMNOPQRSTUVWXYZABCDEFGHIJK
13 MNOPQRSTUVWXYZABCDEFGHIJKL
14 NOPQRSTUVWXYZABCDEFGHIJKLM
15 OPQRSTUVWXYZABCDEFGHIJKLMN
16 PQRSTUVWXYZABCDEFGHIJKLMNO
17 QRSTUVWXYZABCDEFGHIJKLMNOP
18 RSTUVWXYZABCDEFGHIJKLMNOPQ
19 STUVWXYZABCDEFGHIJKLMNOPQR
20 TUVWXYZABCDEFGHIJKLMNOPQRS
21 UVWXYZABCDEFGHIJKLMNOPQRST
22 VWXYZABCDEFGHIJKLMNOPQRSTU
23 WXYZABCDEFGHIJKLMNOPQRSTUV
24 XYZABCDEFGHIJKLMNOPQRSTUVW
25 YZABCDEFGHIJKLMNOPQRSTUVWX
26 ZABCDEFGHIJKLMNOPQRSTUVWXY
```
The Vigenere cipher is defined as a periodic **polyalphabetic substitution cipher**. In simpler terms, this simply means that there are different alphabet ordering's used based on the key. To explain how this cipher works, let's replace the characters of the key and the characters of the plaintext by integers, where A=0, B=1, ..., Z=25. The length of the key let's call period or $L$. So the key is just a set of numbers $k^0, k^1, ... k^{L-1}$. Next take the plaintext and express it also as a list of numbers $p^0, p^1, p^2, ...$
The text is encrypted by adding a number from the key $mod (26)$ to a number from the plaintext, where we run through the key over and over again as needed as we run through the plaintext. As an equation, the $i^{th}$ character is encrypted as follows:
$$c_i = (p_i+k_i \mod L) \mod (26)$$


##### Source Code Example
```python
uppers = string.ascii_uppercase  

def encrypt(pt, key):
   ct = ''
   for i in range(len(pt)):
       p = uppers.index(pt[i])  # Get the numeric position of the plaintext letter
       k = uppers.index(key[i % len(key)])  # Get numeric position of keyword letter  
       c = (p + k) % 26 # Calculate shifted position, ensuring it's within 0-25
       ct += uppers[c]  # Get the letter at the calculated position
   return ct

```
