import os
import json
import requests
from bs4 import BeautifulSoup
from typing import Optional
from rich.console import Console


def get_config(console: Console) -> Optional[dict]:
    config_path = os.path.join(os.path.expanduser("~"), "codeforces.uwu")
    if not config_path:
        console.print("[bold red]ERROR: [/]Config file not found.\nPlease run `cf config`\n")
        return

    if not os.path.isfile(config_path):
        console.print("[bold red]ERROR: [/]Config file not found.\nPlease run `cf config`\n")
        return

    data = None
    with open(config_path, "r+") as f:
        data = json.loads("".join(f.readlines()))

    return data


def get_bp(lang: str) -> Optional[str]:
    bp_dir = os.path.join(os.path.expanduser("~"), "cf_boilerplates")

    if not os.path.isdir(bp_dir):
        return
    template_path = os.path.join(bp_dir, "template." + lang)
    if not os.path.isfile(template_path):
        return

    with open(template_path, "r") as f:
        return f.read()


class CFClient:
    def __init__(self, username: str):
        self.username = username
        self.session = requests.Session()
        self.console = Console()

    def login(self) -> bool:
        # First, try to use saved cookies
        if self._load_cookies():
            if self._verify_login():
                return True
            # Cookies expired or invalid, need fresh login

        # Need to open browser for login
        try:
            import undetected_chromedriver as uc
        except ImportError:
            self.console.print("[bold red]ERROR:[/] undetected-chromedriver not installed. Run: uv add undetected-chromedriver")
            return False

        self.console.print("\n[bold cyan]Opening browser for login...[/]")
        self.console.print("[dim]Please login to Codeforces in the browser window that opens.[/]")
        self.console.print("[dim]The browser will close automatically once you're logged in.[/]\n")

        try:
            import time

            options = uc.ChromeOptions()
            options.add_argument('--no-first-run')
            options.add_argument('--no-service-autorun')
            options.add_argument('--password-store=basic')

            driver = uc.Chrome(options=options, use_subprocess=True)
            driver.get("https://codeforces.com/enter")

            # Wait for login to complete by checking for the username in the page
            # Poll every second for up to 5 minutes
            max_wait = 300  # 5 minutes
            for _ in range(max_wait):
                time.sleep(1)
                try:
                    content = driver.page_source.lower()
                except Exception:
                    continue
                # Check if user is logged in (username appears in header/lang-chooser)
                if self.username.lower() in content and "logout" in content:
                    # Extract cookies for requests session
                    cookies = driver.get_cookies()
                    for cookie in cookies:
                        self.session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain', '.codeforces.com'))

                    # Save cookies for future use
                    self._save_cookies(cookies)

                    self.console.print("[bold green]Login successful![/]")
                    driver.quit()
                    return True

            # Timeout
            self.console.print("[bold red]ERROR:[/] Login timed out (5 minutes). Please try again.")
            driver.quit()
            return False

        except Exception as e:
            self.console.print(f"[bold red]ERROR:[/] Login failed.")
            self.console.print(f"[dim]Details: {e}[/dim]")
            if 'driver' in locals():
                driver.quit()
            return False

    def _verify_login(self) -> bool:
        """Check if current session cookies are valid by making a request."""
        try:
            # Add browser-like headers
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            })
            r = self.session.get("https://codeforces.com", timeout=10)
            return self.username.lower() in r.text.lower() and "logout" in r.text.lower()
        except Exception:
            return False

    def _save_cookies(self, cookies: list) -> None:
        """Save cookies to config for future authenticated requests."""
        cookie_path = os.path.join(os.path.expanduser("~"), "codeforces.cookies")
        with open(cookie_path, "w") as f:
            json.dump(cookies, f)

    def _load_cookies(self) -> bool:
        """Load saved cookies into the session. Returns True if cookies were loaded."""
        cookie_path = os.path.join(os.path.expanduser("~"), "codeforces.cookies")

        if not os.path.isfile(cookie_path):
            return False

        try:
            with open(cookie_path, "r") as f:
                cookies = json.load(f)
            for cookie in cookies:
                self.session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain', '.codeforces.com'))
            return True
        except Exception:
            return False

    def get_csrf(self, url) -> str:
        r = self.session.get(url)
        s = BeautifulSoup(r.text, "html.parser")
        return s.find_all("span", {"class": "csrf-token"})[0]["data-csrf"]
