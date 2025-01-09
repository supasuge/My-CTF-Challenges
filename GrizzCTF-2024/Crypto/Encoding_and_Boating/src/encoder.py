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
