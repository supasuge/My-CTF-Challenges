# Strings Concealed (250 Points)
**Description**: Upon this image is a concealed string, can you find the flag within this image?



To solve this challenge simply run the command:

```bash
strings desktopBG.png | grep -i 'grizzctf{'
```
- `strings`: Searches for all printable strings within the file.
- `grep -i grizzctf{`: Filters printable strings for 'grizzctf{' from the output of the strings command (`-i` omits case specification... Case insensitive.)