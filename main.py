import sys
import os
import io
import requests
import time
import crayons
import json
import threading
import urllib.parse
from datetime import datetime

# Set the default encoding to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

def is_url_encoded(url):
    decoded_url = urllib.parse.unquote(url)
    reencoded_url = urllib.parse.quote(decoded_url)
    return reencoded_url == url

def url_decode(encoded_url):
    return urllib.parse.unquote(encoded_url)

def print_banner():
    print("███████  █████  ██    ██  █████  ███    ██ ")
    print("██      ██   ██ ██    ██ ██   ██ ████   ██ ")
    print("███████ ███████ ██    ██ ███████ ██ ██  ██ ")
    print("     ██ ██   ██  ██  ██  ██   ██ ██  ██ ██ ")
    print("███████ ██   ██   ████   ██   ██ ██   ████ ")
    print(" made and written by savan || @savanop")
    print("Join telegram channel: https://t.me/savanop121")

def log(message, level="INFO"):
    levels = {
        "INFO": crayons.cyan,
        "ERROR": crayons.red,
        "SUCCESS": crayons.green,
        "WARNING": crayons.yellow
    }
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{crayons.white(current_time)} | {levels.get(level, crayons.cyan)(level)} | {message}")

class MoonBix:
    def __init__(self, token, proxy=None):
        self.session = requests.Session()
        self.session.headers.update({
            'authority': 'www.binance.info',
            'accept': '*/*',
            'accept-language': 'en-EG,en;q=0.9,ar-EG;q=0.8,ar;q=0.7,en-GB;q=0.6,en-US;q=0.5',
            'clienttype': 'web',
            'content-type': 'application/json',
            'lang': 'en',
            'origin': 'https://www.binance.info',
            'referer': 'https://www.binance.info/en/game/tg/moon-bix',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        })
        
        if proxy:
            self.session.proxies.update({'http': proxy, 'https': proxy})

        self.token = token
        self.game_response = None
        self.task = None

    def login(self):
        try:
            response = self.session.post(
                'https://www.binance.info/bapi/growth/v1/friendly/growth-paas/third-party/access/accessToken',
                json={'queryString': self.token, 'socialType': 'telegram'},
            )
            if response.status_code == 200:
                self.session.headers['x-growth-token'] = response.json()['data']['accessToken']
                log("Logged in successfully!", level="SUCCESS")
                return True
            else:
                log("Failed to login", level="ERROR")
                return False
        except Exception as e:
            log(f"Error during login: {e}", level="ERROR")
            return False

    def user_info(self):
        try:
            response = self.session.post(
                'https://www.binance.info/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/user/user-info',
                json={'resourceId': 2056},
            )
            return response.json()
        
        except Exception as e:
            log(f"Error during get info: {e}", level="ERROR")
            return None

    def game_data(self):
        try:
            max_retries = 100
            for _ in range(max_retries):
                responses = requests.post('https://app.winsnip.xyz/play', json=self.game_response).text
                try:
                    response = json.loads(responses)
                except json.JSONDecodeError:
                    continue
                if response['message'] == 'success' and response['game']['log'] >= 100:
                    self.game = response['game']
                    return True
                time.sleep(2)  # Wait for 2 seconds before retrying
            log("Failed to get valid game data after multiple attempts", level="ERROR")
            return False
        except Exception as e:
            log(f"Error getting game data: {e}", level="ERROR")
            return False

    def solve_task(self):
        try:
            res = self.session.post("https://www.binance.info/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/task/list",json={"resourceId": 2056})
            if not res or not res.json():
                log(f"Failed to fetch tasks!", level="ERROR")
                return False
            tasks_datas = res.json()
            tasks_data = tasks_datas["data"]["data"][0]["taskList"]["data"]
            resource_ids = [entry['resourceId'] for entry in tasks_data
                    if entry['status'] != 'COMPLETED' and entry['type'] != 'THIRD_PARTY_BIND']
            for idx, resource_id in enumerate(resource_ids, start=1):
                ress = self.session.post("https://www.binance.info/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/task/complete", json={"resourceIdList": [resource_id], "referralCode": None}).json()
                if(ress["code"] == "000000"):
                    log(f"Success complete task id {resource_id}", level="SUCCESS")
                else:
                    log(f"Failed complete task id {resource_id}", level="ERROR")
            return True
        except Exception as e:
            log(f"Error completing tasks: {e}", level="ERROR")
            return False

    def set_proxy(self, proxy=None):
        self.ses = requests.Session()
        if proxy is not None:
            self.ses.proxies.update({"http": proxy, "https": proxy})

    def complete_game(self):
        try:
            response = self.session.post(
                'https://www.binance.info/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/game/complete',
                json={'resourceId': 2056, 'payload': self.game['payload'], 'log': self.game['log']},
            )
            if response.json()['success']:
                log(f"Game completed! Earned + {self.game['log']}", level="SUCCESS")
            return response.json()['success']
        except Exception as e:
            log(f"Error during complete game: {e}", level="ERROR")
            return False

    def start_game(self):
        try:
            max_retries = 100
            for _ in range(max_retries):
                response = self.session.post(
                    'https://www.binance.info/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/game/start',
                    json={'resourceId': 2056},
                )
                self.game_response = response.json()
                if self.game_response['code'] == '000000':
                    log("Game started successfully!", level="INFO")
                    return True
                elif self.game_response['code'] == '116002':
                    log('Attempts not enough! Switching to the next account.', level="WARNING")
                    return False
                log("ERROR! Cannot start game. Retrying...", level="ERROR")
                time.sleep(2)  # Wait for 2 seconds before retrying
            log("Failed to start game after multiple attempts", level="ERROR")
            return False
        except Exception as e:
            log(f"Error during start game: {e}", level="ERROR")
            return False

    def start(self):
        if not self.login():
            log("Login failed.", level="ERROR")
            return False
        if not self.user_info():
            log("Failed to get user data.", level="ERROR")
            return False
        if not self.solve_task():
            log("Failed to solve task.", level="ERROR")
            return False
        while self.start_game():
            if not self.game_data():
                log("Failed to generate game data!", level="ERROR")
                continue
            sleep(45)
            if not self.complete_game():
                log("Failed to complete game", level="ERROR")
            sleep(15)
        return True

def sleep(seconds):
    while seconds > 0:
        time_str = time.strftime('%H:%M:%S', time.gmtime(seconds))
        time.sleep(1)
        seconds -= 1
        print(f'\rWaiting {time_str}', end='', flush=True)
    print()

def run_account(index, token, proxy=None):
    if(is_url_encoded(token)):
        tokens = url_decode(token)
    else:
        tokens = token
    log(f"=== Account {index} ===", level="INFO")
    x = MoonBix(tokens, proxy)
    x.start()
    log(f"=== Account {index} Done ===", level="SUCCESS")
    sleep(10)

def add_query():
    query = input("Enter your query: ")
    with open('data.txt', 'a', encoding='utf-8') as f:
        f.write(query + '\n')
    log("Query added!", level="SUCCESS")

def add_proxy():
    proxy = input("Enter your proxy: ")
    with open('proxy.txt', 'a', encoding='utf-8') as f:
        f.write(proxy + '\n')
    log("Proxy added!", level="SUCCESS")

def reset_query():
    open('data.txt', 'w').close()
    log("Query file reset!", level="SUCCESS")

def reset_proxy():
    open('proxy.txt', 'w').close()
    log("Proxy file reset!", level="SUCCESS")

def start_game():
    # Load tokens
    tokens = [line.strip() for line in open('data.txt', encoding='utf-8') if line.strip()]

    # Check if 'proxy.txt' exists
    if os.path.exists('proxy.txt'):
        proxies = [line.strip() for line in open('proxy.txt', encoding='utf-8') if line.strip()]
    else:
        log("'proxy.txt' not found, continuing without proxies.", level="WARNING")
        proxies = []

    while True:
        for i, token in enumerate(tokens, start=1):
            if proxies:
                proxy = proxies[i % len(proxies)]
            else:
                proxy = None
            run_account(i, token, proxy)
        log("Completed all accounts. Starting over...", level="INFO")
        sleep(10)

if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    
    while True:
        log("1. Add query")
        log("2. Add proxy")
        log("3. Start game")
        log("4. Reset query")
        log("5. Reset proxy")
        log("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            add_query()
        elif choice == '2':
            add_proxy()
        elif choice == '3':
            start_game()
        elif choice == '4':
            reset_query()
        elif choice == '5':
            reset_proxy()
        elif choice == '6':
            log("Exiting...", level="INFO")
            break
        else:
            log("Invalid choice. Please try again.", level="ERROR")
