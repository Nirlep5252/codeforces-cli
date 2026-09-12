import os
import json
import re
import sys
import types
import requests
from bs4 import BeautifulSoup
from typing import Optional
from rich.console import Console


def _ensure_distutils_version() -> None:
    """
    Register a minimal `distutils.version` module when the stdlib one is gone.

    `undetected_chromedriver.patcher` does `from distutils.version import
    LooseVersion`, and distutils was removed from the stdlib in Python 3.12.
    Having setuptools installed also papers over this, but it is not a
    dependency of undetected-chromedriver, so ship our own shim instead.
    """
    try:
        import distutils.version  # noqa: F401
        return
    except ImportError:
        pass

    class LooseVersion:
        """Port of the distutils class, only what the patcher actually uses."""

        component_re = re.compile(r"(\d+ | [a-z]+ | \.)", re.VERBOSE)

        def __init__(self, vstring: Optional[str] = None):
            self.vstring = ""
            self.version = []
            if vstring:
                self.parse(vstring)

        def parse(self, vstring: str) -> None:
            self.vstring = vstring
            components = [c for c in self.component_re.split(vstring) if c and c != "."]
            for i, component in enumerate(components):
                try:
                    components[i] = int(component)
                except ValueError:
                    pass
            self.version = components

        def __str__(self):
            return self.vstring

        def __repr__(self):
            return "LooseVersion ('%s')" % str(self)

        def _key(self, other):
            if isinstance(other, str):
                return LooseVersion(other).version
            if isinstance(other, LooseVersion):
                return other.version
            return None

        def __eq__(self, other):
            key = self._key(other)
            return NotImplemented if key is None else self.version == key

        def __lt__(self, other):
            key = self._key(other)
            return NotImplemented if key is None else self.version < key

        def __le__(self, other):
            key = self._key(other)
            return NotImplemented if key is None else self.version <= key

        def __gt__(self, other):
            key = self._key(other)
            return NotImplemented if key is None else self.version > key

        def __ge__(self, other):
            key = self._key(other)
            return NotImplemented if key is None else self.version >= key

    distutils = sys.modules.get("distutils")
    if distutils is None:
        distutils = types.ModuleType("distutils")
        distutils.__path__ = []  # type: ignore[attr-defined]
        sys.modules["distutils"] = distutils

    version_module = types.ModuleType("distutils.version")
    version_module.LooseVersion = LooseVersion  # type: ignore[attr-defined]
    sys.modules["distutils.version"] = version_module
    distutils.version = version_module  # type: ignore[attr-defined]


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
            _ensure_distutils_version()
            import undetected_chromedriver as uc
        except ImportError as e:
            if getattr(e, "name", None) == "undetected_chromedriver":
                self.console.print("[bold red]ERROR:[/] undetected-chromedriver is not installed. Run: pip install undetected-chromedriver")
            else:
                self.console.print("[bold red]ERROR:[/] undetected-chromedriver is installed but could not be imported.")
                self.console.print(f"[dim]Details: {e.__class__.__name__}: {e}[/]")
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
