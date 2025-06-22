import requests
import urllib3
import random
import threading
from queue import Queue
import time
import os
from requirements import build_platforms, user_agents, known_found_status, categorized_platforms, known_patterns
# Disable SSL warnings where needed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Terminal colors
GREEN = '\033[92m'
WHITE = '\033[97m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'
os.system('clear')
print(RED+"=============="+RESET)
print(YELLOW+"   Byomkesh   "+RESET)
print(RED+"=============="+RESET)
print('\n\n')
# Request handler
def request_url(url, allow_insecure=False, retries=3):
    time.sleep(random.uniform(0.2, 0.8))
    for _ in range(retries):
        try:
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.google.com/"
            }
            resp = requests.get(url, headers=headers, timeout=5, verify=not allow_insecure)
            return resp.status_code, resp.text, None
        except requests.RequestException as e:
            error_name = e.__class__.__name__
            if error_name in ["ConnectionError", "Timeout"]:
                time.sleep(1)
                continue
            return None, None, error_name
    return None, None, "Connection failed after retries"
# Interpretation per platform
def interpret_status(platform, status_code, html, error):
    if error:
        return "error", error
    if status_code == 200:
        if platform in known_patterns:
            page_text = html.lower()
            for pattern in known_patterns[platform]:
                if pattern.lower() in page_text:
                    return "not found", "matched known 'not found' pattern"
        return "found", ""
    if status_code == 404:
        return "not found", ""
    if platform in known_found_status and status_code in known_found_status[platform]:
        return "found", ""
    return "error", f"status: {status_code}"
# Check each platform
found, not_found, unknown, errors = [], [], [], []
def check_site(platform, url, insecure):
    status_code, html, error = request_url(url, allow_insecure=insecure)
    status, message = interpret_status(platform, status_code, html, error)
    if status == "found":
        print(f"{GREEN}[+] {platform}:{RESET} {url}{RESET}")
        found.append((platform, url))
    elif status == "not found":
        print(f"{RED}[!] {platform}:{RESET} not found{RESET}")
        not_found.append(platform)
    elif status == "unknown":
        print(f"{YELLOW}[?] {platform}:{RESET} {message}{RESET}")
        unknown.append((platform, message))
    elif status == "error":
        print(f"{YELLOW}[?] {platform}:{RESET} error: {message}{RESET}")
        errors.append((platform, message))
# Thread worker
def worker(q):
    while not q.empty():
        platform, (url, insecure) = q.get()
        check_site(platform, url, insecure)
        q.task_done()
# Category mapping for display
def get_category(platform):
    for category, platforms in categorized_platforms.items():
        if platform in platforms:
            return category
    return "Other"
# Main checking function
def check_username(username, num=5):
    platforms = build_platforms(username)
    q = Queue()
    for platform, data in platforms.items():
        q.put((platform, data))
    threads = []
    for _ in range(num):
        t = threading.Thread(target=worker, args=(q,))
        t.start()
        threads.append(t)
    q.join()
    print(f"\n{YELLOW}" + "="*40)
    print(f"{WHITE}Summary of Username Check:{RESET}")
    print(YELLOW+"="*40+"\n")
    summary = {"found": found, "not found": not_found, "unknown": unknown, "error": errors}
    for key in summary:
        if key != "found":
            continue
        entries = summary[key]
        categorized = {}
        for item in entries:
            if isinstance(item, tuple):
                platform = item[0]
            else:
                platform = item
            cat = get_category(platform)
            categorized.setdefault(cat, []).append(item)
        if categorized:
            print(f"\n{WHITE}{key.title()}:{RESET}")
            for cat, items in sorted(categorized.items()):
                print(f"\n  {CYAN}{cat}:{RESET}")
                for entry in items:
                    if isinstance(entry, tuple):
                        print(f"    {entry[0]}: {entry[1]}")
                    else:
                        print(f"    {entry}")
    print(f"{RED}[!] Not Found:{RESET}")
    if summary["not found"]:
        for i in summary["not found"]:
            print(f"    {i}")
    else:
        print("    None")
    print(f"{YELLOW}[?] Unknowns and Errors:{RESET}")
    if summary["unknown"] or summary["error"]:
        for i in summary["unknown"]:
            print(f"    {i}")
        for i in summary["error"]:
            print(f"    {i[0]} ({i[1]})")
    else:
        print('    None')
if __name__ == "__main__":
    user = input(f"{CYAN}[?] Enter a username to check:{RESET} ").strip()
    try:
        num = int(input(f"{CYAN}[?] Enter Number of Threads: {RESET}"))
        if num <= 0:
            raise ValueError
        os.system('clear')
        print(RED+"=============="+RESET)
        print(YELLOW+"   Byomkesh   "+RESET)
        print(RED+"=============="+RESET)
        print('\n\n')
        print(f'Finding {user}...')
        check_username(user, num)
    except:
        print("Using 5 Threads.")
        input('Press Enter: ')
        os.system('clear')
        print(RED+"=============="+RESET)
        print(YELLOW+"   Byomkesh   "+RESET)
        print(RED+"=============="+RESET)
        print('\n\n')
        print(f'Finding {user}...')
        check_username(user)
