from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from eth_utils import to_hex
from eth_account import Account
from eth_account.messages import encode_defunct
from fake_useragent import FakeUserAgent
from datetime import datetime, timezone
from colorama import *
import asyncio, secrets, time, uuid, random, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class KlokApp:
    def __init__(self) -> None:
        self.HEADERS = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://klokapp.ai",
            "Referer": "https://klokapp.ai/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://api1-pp.klokapp.ai/v1"
        self.ref_code = "GGQ3GJ46" # U can change it with yours
        self.PAGE_URL = "https://klokapp.ai"
        self.SITE_KEY = "0x4AAAAAABdQypM3HkDQTuaO"
        self.CAPTCHA_KEY = None
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.turnstile_tokens = {}
        self.session_tokens = {}
        self.browser_ids = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Chat {Fore.BLUE + Style.BRIGHT}KlokApp - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_2captcha_key(self):
        try:
            with open("2captcha_key.txt", 'r') as file:
                captcha_key = file.read().strip()

            return captcha_key
        except Exception as e:
            return None
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, token):
        if token not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[token] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[token]

    def rotate_proxy_for_account(self, token):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[token] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy

    def mask_account(self, account):
        mask_account = account[:6] + '*' * 6 + account[-6:]
        return mask_account    

    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address
            
            return address
        except Exception as e:
            raise Exception(f"Generate Addres From Private Key Failed: {str(e)}")
        
    def generate_payload(self, account: str, address: str):
        try:
            nonce = secrets.token_hex(48)
            issued_at = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
            message = f"klokapp.ai wants you to sign in with your Ethereum account:\n{address}\n\n\nURI: https://klokapp.ai/\nVersion: 1\nChain ID: 1\nNonce: {nonce}\nIssued At: {issued_at}"
            
            encoded_message = encode_defunct(text=message)
            signed_message = Account.sign_message(encoded_message, private_key=account)
            signature = to_hex(signed_message.signature)

            payload = {
                "signedMessage":signature,
                "message":message,
                "referral_code":self.ref_code
            }

            return payload
        except Exception as e:
            return None
        
    def generate_browser_id(self):
        browser_id = str(uuid.uuid4())
        return browser_id
    
    def content_lists(self):
        content_lists = [
            "Help me brainstorm startup ideas",
            "Teach me about a topic in depth",
            "Plan a vacation itinerary for me",
            "Tell me a fun fact about fishes",
            "Give me tips to stay focused while studying",
            "Explain quantum physics in simple terms",
            "Write a short story about a time-traveling cat",
            "Suggest a healthy dinner recipe",
            "What's a good book to read this month?",
            "Translate 'I love programming' to Japanese",
            "What are the benefits of meditation?",
            "Summarize the plot of Harry Potter",
            "How do I start a podcast?",
            "Create a workout plan for beginners",
            "Tell me a joke to make my day",
            "What are some fun indoor activities for kids?",
            "Help me write a professional email",
            "What's the capital of Iceland?",
            "Suggest weekend activities for couples",
            "What's the difference between AI and machine learning?",
            "Help me improve my resume",
            "Give me ideas for a birthday party",
            "Explain blockchain like I'm five",
            "What's trending in tech right now?",
            "How do I bake a chocolate cake?",
            "Tell me a historical fact I didn't know",
            "How can I save more money each month?",
            "What are the symptoms of burnout?",
            "Teach me how to play chess",
            "What is a good movie to watch tonight?",
            "Write a poem about the ocean",
            "How can I learn to code fast?",
            "What is the meaning of life?",
            "Give me a quote to inspire me today",
            "Tell me how rainbows form",
            "What is the best way to learn a new language?",
            "Suggest a name for my new puppy",
            "Tell me a riddle to solve",
            "What are some common interview questions?",
            "Give me a recipe for homemade pizza",
            "What is the largest animal in the world?",
            "How do I create a budget?",
            "Describe a futuristic city",
            "Give me ideas for YouTube content",
            "What's the best time to visit Japan?",
            "How do I stay motivated to work out?",
            "Write a haiku about spring",
            "What are the top tourist spots in Paris?",
            "How do plants make food?",
            "What are the rules of football?"
        ]

        return content_lists
    
    def generate_chat_payload(self, address: str, content: str):
        current_datetime = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

        payload = {
            "id":self.browser_ids[address],
            "title":"",
            "messages":[
                {
                    "role":"user",
                    "content":content
                }
            ],
            "sources":[],
            "model":"llama-3.3-70b-instruct",
            "created_at":current_datetime,
            "language":"english",
            "search":False
        }

        return payload
        
    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Monosans Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return choose, rotate
    
    async def check_connection(self, proxy=None):
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url=self.PAGE_URL, headers={}) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            return None
        
    async def solve_cf_turnstile(self, address: str, proxy=None, retries=5):
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:

                    if self.CAPTCHA_KEY is None:
                        return None
                    
                    url = f"http://2captcha.com/in.php?key={self.CAPTCHA_KEY}&method=turnstile&sitekey={self.SITE_KEY}&pageurl={self.PAGE_URL}"
                    async with session.get(url=url) as response:
                        response.raise_for_status()
                        result = await response.text()

                        if 'OK|' not in result:
                            await asyncio.sleep(5)
                            continue

                        request_id = result.split('|')[1]

                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}   >{Style.RESET_ALL}"
                            f"{Fore.BLUE + Style.BRIGHT} Req Id : {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{request_id}{Style.RESET_ALL}"
                        )

                        for _ in range(30):
                            res_url = f"http://2captcha.com/res.php?key={self.CAPTCHA_KEY}&action=get&id={request_id}"
                            async with session.get(url=res_url) as res_response:
                                res_response.raise_for_status()
                                res_result = await res_response.text()

                                if 'OK|' in res_result:
                                    captcha_token = res_result.split('|')[1]
                                    self.turnstile_tokens[address] = captcha_token
                                    return True
                                elif res_result == "CAPCHA_NOT_READY":
                                    self.log(
                                        f"{Fore.MAGENTA + Style.BRIGHT}   >{Style.RESET_ALL}"
                                        f"{Fore.BLUE + Style.BRIGHT} Message: {Style.RESET_ALL}"    
                                        f"{Fore.YELLOW + Style.BRIGHT}Captcha Not Ready, Retrying...{Style.RESET_ALL}"
                                    )
                                    await asyncio.sleep(5)
                                    continue
                                else:
                                    break

            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
        
    async def user_login(self, account: str, address: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/verify"
        data = json.dumps(self.generate_payload(account, address))
        headers = {
            **self.HEADERS,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "X-Turnstile-Token": self.turnstile_tokens[address]
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def user_points(self, address: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/points"
        headers = {
            **self.HEADERS,
            "X-Session-Token": self.session_tokens[address]
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def rate_limit(self, address: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/rate-limit"
        headers = {
            **self.HEADERS,
            "X-Session-Token": self.session_tokens[address]
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
    
    async def perform_chat(self, address: str, content: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/chat"
        data = json.dumps(self.generate_chat_payload(address, content))
        headers = {
            **self.HEADERS,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "X-Session-Token": self.session_tokens[address],
            "X-Turnstile-Token": self.turnstile_tokens[address]
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.text()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
    
    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
        message = "Checking Connection, Wait..."
        if use_proxy:
            message = "Checking Proxy Connection, Wait..."

        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.YELLOW + Style.BRIGHT}{message}{Style.RESET_ALL}",
            end="\r",
            flush=True
        )

        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        if rotate_proxy:
            is_valid = None
            while is_valid is None:
                is_valid = await self.check_connection(proxy)
                if not is_valid:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Proxy  :{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Not 200 OK, {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}Rotating Proxy...{Style.RESET_ALL}"
                    )
                    proxy = self.rotate_proxy_for_account(address) if use_proxy else None
                    await asyncio.sleep(5)
                    continue

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Proxy  :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} 200 OK {Style.RESET_ALL}                  "
                )

                return True

        is_valid = await self.check_connection(proxy)
        if not is_valid:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Not 200 OK {Style.RESET_ALL}          "
            )
            return False
        
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}Proxy  :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} 200 OK {Style.RESET_ALL}                  "
        )

        return True
        
    async def process_user_login(self, account: str, address: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        self.log(f"{Fore.CYAN + Style.BRIGHT}Captcha:{Style.RESET_ALL}")

        cf_solved = await self.solve_cf_turnstile(address, proxy)
        if cf_solved:
            self.log(
                f"{Fore.MAGENTA + Style.BRIGHT}   >{Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT} Message: {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT}Cf Trunstile Solved Successfully{Style.RESET_ALL}"
            )
            
            login = await self.user_login(account, address, proxy)
            if not login:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Login Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Skipping This Account {Style.RESET_ALL}"
                )
                return False

            self.session_tokens[address] = login["session_token"]
            self.browser_ids[address] = self.generate_browser_id()
            return True
        
        self.log(
            f"{Fore.MAGENTA + Style.BRIGHT}   >{Style.RESET_ALL}"
            f"{Fore.BLUE + Style.BRIGHT} Message: {Style.RESET_ALL}"
            f"{Fore.RED+Style.BRIGHT}Solve Cf Turnstile Failed{Style.RESET_ALL}"
            f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.YELLOW+Style.BRIGHT}Skipping This Account{Style.RESET_ALL}"
        )
        return False

    async def process_accounts(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:
            logined = await self.process_user_login(account, address, use_proxy)
            if logined:
                proxy = self.get_next_proxy_for_account(address) if use_proxy else None
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Login Success {Style.RESET_ALL}"
                )

                total_points = "N/A"
                points = await self.user_points(address, proxy)
                if points:
                    total_points = points.get("total_points", 0)

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Points :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {total_points} Mira {Style.RESET_ALL}"
                )

                self.log(f"{Fore.CYAN+Style.BRIGHT}AI Chat:{Style.RESET_ALL}")

                rate_limit = await self.rate_limit(address, proxy)
                if rate_limit:
                    remaining = rate_limit.get("remaining", 0)

                    if remaining > 0:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}   >{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} Have {remaining} Chances {Style.RESET_ALL}"
                        )
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}   >{Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT} Use Llama 3.3 70B Models {Style.RESET_ALL}"
                        )

                        contents = self.content_lists()

                        used_contents = set()

                        count = remaining
                        while remaining > 0:
                            idx = count - remaining

                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}   >{Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT} {idx+1} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}Of{Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT} {count} {Style.RESET_ALL}"
                            )

                            available_contents = [c for c in contents if c not in used_contents]

                            content = random.choice(available_contents)

                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}   >{Style.RESET_ALL}"
                                f"{Fore.YELLOW + Style.BRIGHT} Solving Cf Trunstile... {Style.RESET_ALL}"
                            )

                            solved = await self.solve_cf_turnstile(address, proxy)
                            if solved:
                                self.log(
                                    f"{Fore.MAGENTA + Style.BRIGHT}   >{Style.RESET_ALL}"
                                    f"{Fore.GREEN + Style.BRIGHT} Cf Trunstile Solved Successfully {Style.RESET_ALL}"
                                )

                                self.log(
                                    f"{Fore.MAGENTA + Style.BRIGHT}   >{Style.RESET_ALL}"
                                    f"{Fore.BLUE + Style.BRIGHT} Question : {Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT}{content}{Style.RESET_ALL}"
                                )

                                answer = await self.perform_chat(address, content, proxy)
                                if answer:
                                    self.log(
                                        f"{Fore.MAGENTA + Style.BRIGHT}   >{Style.RESET_ALL}"
                                        f"{Fore.BLUE + Style.BRIGHT} AI Answer: {Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT}{answer}{Style.RESET_ALL}"
                                    )
                                    used_contents.add(content)

                                else:
                                    self.log(
                                        f"{Fore.MAGENTA + Style.BRIGHT}   >{Style.RESET_ALL}"
                                        f"{Fore.BLUE + Style.BRIGHT} AI Answer: {Style.RESET_ALL}"
                                        f"{Fore.RED + Style.BRIGHT}Models Not Responded{Style.RESET_ALL}"
                                    )
                                    break

                                remaining -= 1

                            else:
                                self.log(
                                    f"{Fore.MAGENTA + Style.BRIGHT}   >{Style.RESET_ALL}"
                                    f"{Fore.RED+Style.BRIGHT} Solve Cf Turnstile Failed {Style.RESET_ALL}"
                                )

                            await asyncio.sleep(random.randint(5, 10))

                    else:
                        reset_time = rate_limit.get("reset_time", 0) + int(time.time())
                        reset_wib = datetime.fromtimestamp(reset_time).astimezone(wib).strftime('%x %X %Z')
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}   >{Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT} No Available Chance {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.BLUE + Style.BRIGHT} Reset At {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{reset_wib}{Style.RESET_ALL}"
                        )
                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}   >{Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT} GET Rate Limit Failed {Style.RESET_ALL}"
                    )

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            captcha_key = self.load_2captcha_key()
            if captcha_key:
                self.CAPTCHA_KEY = captcha_key
            
            use_proxy_choice, rotate_proxy = self.print_question()

            while True:
                use_proxy = False
                if use_proxy_choice in [1, 2]:
                    use_proxy = True

                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies(use_proxy_choice)
                
                separator = "=" * 23
                for account in accounts:
                    if account:
                        address = self.generate_address(account)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if not address:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}Error:{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Generate Address Failed, {Style.RESET_ALL}"
                                f"{Fore.YELLOW + Style.BRIGHT}Skipping This Account.{Style.RESET_ALL}"
                            )
                            continue

                        await self.process_accounts(account, address, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*68)
                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed.{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = KlokApp()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] KlokApp - BOT{Style.RESET_ALL}                                       "                              
        )