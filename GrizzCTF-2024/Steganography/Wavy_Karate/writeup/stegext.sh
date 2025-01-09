#!/bin/bash

FILE="linux_users.wav" # The file you're trying to extract data from
WORDLIST="/usr/share/wordlists/rockyou.txt"

while IFS= read -r line; do
  echo "Trying passphrase: $line"
  if steghide extract -sf "$FILE" -p "$line" 2>/dev/null; then
    echo "Success! Passphrase is: $line"
    break
  fi
done < "$WORDLIST"