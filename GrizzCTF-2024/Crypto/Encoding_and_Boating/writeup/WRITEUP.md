# Encoding and Boating
**Description:** I made a *highly* original decoder, can you decode the string provided below to get the flag?

`KIZUU4DFNZYEIVSFLI3WI3KWPFSVMOJRMJWWY6DEK5LGMWSXGVVGEMSSOBRG2ZD2LAZGQMLBIQ4TS===`

###### Source Code
```python
import json
from base64 import b64encode as honestlynoideawhatimdoing
from base64 import b32encode as geronimo
file_path = '[REDACTED--Unimportant]'
with open(file_path) as f:
    data=json.load(f)
    flag = data['crypto']['flag2']
stringjuan = geronimo(honestlynoideawhatimdoing(flag.encode()))
with open('ciphertext.txt', 'w') as f:
    f.write(stringjuan.decode())
```
To reverse this, simply base32 decode the given string, then base64 decode the output from the previous base32 encoding. This will result in the plaintext flag.

###### Solution
```python
from base64 import b64decode, b32decode
path = '../src/ciphertext.txt'
with open(path, 'r') as f:
    ciphertext = f.read()

# Reverse the encoding steps
decoded_base32 = b32decode(ciphertext)
decoded_base64 = b64decode(decoded_base32)

flag = decoded_base64.decode()
print(flag)
```


- Output from [solve.py](solve.py)
![alt text](image.png)
