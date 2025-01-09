# Wavvy Karate

To create this challenge, I provided the link of the youtube video to: "https://y2down.cc/en/youtube-wav.html"

Then I used `steghide` to embed `flag.txt` using a randomly selected password from `/usr/share/wordlists/rockyou.txt`.

## Solution
```bash
#!/bin/bash
# replace yourfile.wav with the name of the .wav file you are trying to extract data from.
FILE="yourfile.wav" # The file you're trying to extract data from
# rockyou wordlist using the standard kali path for wordlists
WORDLIST="/usr/share/wordlists/rockyou.txt"

while IFS= read -r line; do
  echo "Trying passphrase: $line"
  if steghide extract -sf "$FILE" -p "$line" 2>/dev/null; then
    echo "Success! Passphrase is: $line"
    break
  fi
done < "$WORDLIST"
```
- Note: It may take a while, it depends on how much hardware resources you have allocated.

```
GrizzCTF{lsb_1n_4_w4v_f1l3}
```

Truth be told, I am not entirely sure if `steghide` hides files using LSB Steg (I am going to asssume not)... However I simply forgot to change the flag when I was making the challenge. Happens.
