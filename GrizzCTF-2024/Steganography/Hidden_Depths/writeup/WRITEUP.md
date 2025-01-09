# Hidden Depths
*100 Points*
- **Description:** This challenge presents a simple `steghide` challenge in which the file `flag.txt` has been embedded into the image. The goal of this challenge is to extract `flag.txt` from the image, and then submit the flag. 


### How to Approach

- Acquire Steghide
- Use Steghide's capabilities to reveal and retrieve the hidden `flag.txt`.
- The simplest path might just lead to success — no passwords needed here.


```bash
$ steghide extract -sf cpu_closeup.jpg
```

...

```bash
'$ flag.txt has been extracted...'
cat flag.txt
```



