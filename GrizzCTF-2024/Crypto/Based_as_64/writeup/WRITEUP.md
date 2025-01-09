# Based as 64
Provided in the challenge:
Encoded String:
`R3JpenpDVEZ7YmFzZTY0X2lzX3MwX2JhczNkfQ==`

Can you decode this to obtain the flag?
```powershell
C:EP\> [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("R3JpenpDVEZ7YmFzZTY0X2lzX3MwX2JhczNkfQ=="))

GrizzCTF{base64_is_s0_bas3d}
```
OR for unix:
```bash
$ echo 'R3JpenpDVEZ7YmFzZTY0X2lzX3MwX2JhczNkfQ==' | base64 -d
GrizzCTF{base64_is_s0_bas3d}
```


This is an amazing example of why Linux > Windows.

