# Getting Started (50 Points)
**Description:** Given the file `data.txt` submit the SHA256 hashsum of the file as the flag in the format: `GrizzCTF{................................}`


## Solution
```bash
echo -n "GrizzCTF{"$(sha256sum data.txt | awk '{print $1}')"}" 
```

### Explanation
- `echo -n GrizzCTF{"` - Do not output new lines, wrap in GrizzCTF{................................}
- `$(sha256sum data.txt | awk '{print $1}')"}` - Get the SHA256 hashsum of the file and parse the SHA256 hashsum using `awk '{print $1}'`.

