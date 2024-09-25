from datetime import datetime
import os
import requests
import time
import crayons
import json
import threading
import urllib.parse

def is_url_encoded(url):
    decoded_url = urllib.parse.unquote(url)
    reencoded_url = urllib.parse.quote(decoded_url)
    return reencoded_url == url

def url_decode(encoded_url):
    return urllib.parse.unquote(encoded_url)

def print_banner():
    print(crayons.yellow('███████  █████  ██    ██  █████  ███    ██ '))
    print(crayons.yellow('██      ██   ██ ██    ██ ██   ██ ████   ██ '))
    print(crayons.yellow('███████ ███████ ██    ██ ███████ ██ ██  ██ '))
    print(crayons.yellow('     ██ ██   ██  ██  ██  ██   ██ ██  ██ ██ '))
    print(crayons.yellow('███████ ██   ██   ████   ██   ██ ██   ████ '))
    print("Custom Banner with your credits")
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

# Function to add a query to data.txt
def add_query():
    query = input("Enter query: ")
    with open("data.txt", "a") as file:
        file.write(query + "\n")
    log(f"Query '{query}' added to data.txt", level="SUCCESS")

# Function to add a proxy to proxy.txt
def add_proxy():
    proxy = input("Enter proxy: ")
    with open("proxy.txt", "a") as file:
        file.write(proxy + "\n")
    log(f"Proxy '{proxy}' added to proxy.txt", level="SUCCESS")

# Function to reset (clear) the queries in data.txt
def reset_query():
    with open("data.txt", "w") as file:
        pass
    log("All queries have been reset.", level="SUCCESS")

# Function to reset (clear) the proxies in proxy.txt
def reset_proxy():
    with open("proxy.txt", "w") as file:
        pass
    log("All proxies have been reset.", level="SUCCESS")

class MoonBix:
    def __init__(self, token, proxy=None):
        self.session = requests.session()
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

    def user_info(self):
        try:
            response = self.session.post(
                'https://www.binance.info/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/user/user-info',
                json={'resourceId': 2056},
            )
            return response.json()
        except Exception as e:
            log(f"Error during get info: {e}", level="ERROR")

    def game_data(self):
        try:
            while True:
                responses = requests.post(
                    'https://app.winsnip.xyz/play', json=self.game_response).text
                try:
                    response = json.loads(responses)
                except json.JSONDecodeError:
                    continue
                if response['message'] == 'success' and response['game']['log'] >= 100:
                    self.game = response['game']
                    return True
        except Exception as e:
            log(f"Error getting game data: {e}", level="ERROR")

    def solve_task(self):
        try:
            res = self.session.post(
                "https://www.binance.info/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/task/list", 
                json={"resourceId": 2056}
            )
            if not res or not res.json():
                log("Failed to fetch tasks!", level="ERROR")
                return
            tasks_datas = res.json()
            tasks_data = tasks_datas["data"]["data"][0]["taskList"]["data"]
            resource_ids = [
                entry['resourceId'] for entry in tasks_data 
                if entry['status'] != 'COMPLETED' and entry['type'] != 'THIRD_PARTY_BIND'
            ]
            for idx, resource_id in enumerate(resource_ids, start=1):
                ress = self.session.post(
                    "https://www.binance.info/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/task/complete", 
                    json={"resourceIdList": [resource_id], "referralCode": None}
                ).json()
                if ress["code"] == "000000":
                    log(f"Success complete task id {resource_id}", level="SUCCESS")
                else:
                    log(f"Failed complete task id {resource_id}", level="ERROR")
            return True
        except Exception as e:
            log(f"Error completing tasks: {e}", level="ERROR")

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

    def start_game(self):
        try:
            while True:
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
                log("ERROR! Cannot start game.", level="ERROR")
                return False
        except Exception as e:
            log(f"Error during start game: {e}", level="ERROR")

    def start(self):
        if not self.login():
            log("Login failed.", level="ERROR")
            return
        if not self.user_info():
            log("Failed to get user data.", level="ERROR")
            return
        if not self.solve_task():
            log("Failed to solve task.", level="ERROR")
            return
        while self.start_game():
            if not self.game_data():
                log("Failed to generate game data!", level="ERROR")
                return
            time.sleep(45)  # Remove sleep in the loop for account switching
            if not self.complete_game():
                log("Failed to complete game", level="ERROR")

def run_account(index, token, proxy=None):
    if is_url_encoded(token):
        tokens = url_decode(token)
    else:
        tokens = token
    log(f"Starting account {index} with token: {tokens} using proxy: {proxy}", level="INFO")
    moonbix = MoonBix(tokens, proxy=proxy)
    moonbix.start()

def main():
    print_banner()
    # Ensure necessary files exist
    if not os.path.exists("proxy.txt"):
        with open("proxy.txt", "w") as f:
            pass
    if not os.path.exists("data.txt"):
        with open("data.txt", "w") as f:
            pass

    proxies = []
    with open("proxy.txt", "r") as file:
        proxies = [line.strip() for line in file.readlines() if line.strip()]

    queries = []
    with open("data.txt", "r") as file:
        queries = [line.strip() for line in file.readlines() if line.strip()]

    if not queries:
        log("No queries found. Please add queries.", level="ERROR")
        return

    while True: 
        print(crayons.green("\nSelect an option:"))
        print(crayons.cyan("1. Add Query"))
        print(crayons.cyan("2. Add Proxy"))
        print(crayons.cyan("3. Start Gameplay"))
        print(crayons.cyan("4. Reset Queries"))
        print(crayons.cyan("5. Reset Proxies"))
        print(crayons.cyan("6. Exit"))

        choice = input("Enter your choice: ")

        if choice == "1":
            add_query()
        elif choice == "2":
            add_proxy()
        elif choice == "3":
            log("Starting gameplay...", level="INFO")
            index = 1
            while True:
                for token in queries:
                    if index <= len(proxies):
                        proxy = proxies[index - 1]
                    else:
                        proxy = None
                    run_account(index, token, proxy)
                    index += 1
                    if index > len(queries):
                        index = 1
        elif choice == "4":
            reset_query()
        elif choice == "5":
            reset_proxy()
        elif choice == "6":
            log("Exiting...", level="INFO")
            break
        else:
            log("Invalid choice! Please select a valid option.", level="ERROR")

if __name__ == "__main__":
    main()
