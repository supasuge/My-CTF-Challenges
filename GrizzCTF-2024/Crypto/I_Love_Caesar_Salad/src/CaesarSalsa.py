 
import json
file_path = '[REDACTED--Unimportant]'
with open(file_path) as f:
    data=json.load(f)
    flag = data['crypto']['flag1']

NOTCAESAR = lambda char, shift: (
    chr((ord(char) - 65 + shift) % 26 + 65) if char.isupper() else
    chr((ord(char) - 97 + shift) % 26 + 97) if char.islower() else
    str((int(char) + shift) % 10) if char.isdigit() else char)

shift = 3
cipher = ''.join(NOTCAESAR(char, shift) for char in flag)
print('flag: ', cipher)
with open('ciphertext.txt', 'w') as f:
    f.write(cipher)
    f.close()
