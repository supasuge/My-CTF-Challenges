# I love caesar salad
**150 Points**

*Difficulty:* Easy

**Description**: Can you decrypt the given ciphertext? `JulccFWI{4_7op35w_wu4fn6g_b37}`.

## Source Code
```python
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
```

#### Code Analysis

The provided Python script encrypts a flag using a modified Caesar cipher and writes the ciphertext to a file named `ciphertext.txt`. The encryption process is defined by the `NOTCAESAR` lambda function, which takes a character and a shift value as inputs and returns the encrypted character based on the following rules:

1. **For Uppercase Letters**: If the character is uppercase (`A-Z`), it subtracts `65` from its ASCII value (to normalize `A` to `0`), adds the shift value, applies modulo `26` to ensure the result stays within the alphabet range, and then adds `65` back to return to the ASCII range for uppercase letters.

2. **For Lowercase Letters**: If the character is lowercase (`a-z`), it performs a similar operation as for uppercase letters but subtracts and adds `97` instead, to normalize `a` to `0`.

3. **For Digits**: If the character is a digit (`0-9`), it adds the shift value, applies modulo `10` to ensure the result is a single digit, and then converts it back to a string.

4. **For Other Characters**: If the character does not fall into the above categories, it is left unchanged.

The script encrypts the flag with a shift of `3` and saves the resulting ciphertext.

#### Explanation of the Caesar Cipher

The Caesar cipher is a type of substitution cipher in which each letter in the plaintext is shifted a certain number of places down or up the alphabet. For example, with a shift of `3`, `A` would be encrypted to `D`, `B` to `E`, and so on. The cipher wraps around the alphabet, so with a shift of `3`, `Z` would be encrypted to `C`.

#### Differences from the Traditional Caesar Cipher

The `NOTCAESAR` function in the script differs from the traditional Caesar cipher in several ways:

1. **Digit Handling**: Traditional Caesar ciphers do not typically handle numeric digits. The `NOTCAESAR` function extends the Caesar cipher concept to digits, shifting them within the range of `0-9`.

2. **Special Character Handling**: The function leaves special characters (e.g., punctuation, spaces) unchanged, which is a common practice in many Caesar cipher implementations to preserve readability and formatting.

3. **Bidirectional Shift**: By allowing positive and negative shift values, the function can encrypt and decrypt messages, assuming the correct shift value is known.

#### Solution

To decrypt the given ciphertext `JulccFWI{4_7op35w_wu4fn6g_b37}`, we need to reverse the encryption process. Since the encryption used a shift of `3`, decryption requires a shift of `-3`. Modifying the `NOTCAESAR` function to use a shift of `-3` will decrypt the ciphertext back to the original flag.

Here's the modified decryption code snippet:

```python
# Decryption function with a shift of -3
NOTCAESAR = lambda char, shift: (
    chr((ord(char) - 65 + shift) % 26 + 65) if char.isupper() else
    chr((ord(char) - 97 + shift) % 26 + 97) if char.islower() else
    str((int(char) + shift) % 10) if char.isdigit() else char)

shift = -3  # Shift for decryption
ciphertext = "JulccFWI{4_7op35w_wu4fn6g_b37}"
flag = ''.join(NOTCAESAR(char, shift) for char in ciphertext)
print('Decrypted flag: ', flag)
```

Executing this code will decrypt the ciphertext and reveal the original flag. 
```
Decrypted flag:  GrizzCTF{1_4lm02t_tr1ck3d_y04}
```
___

