import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ufa_scraper.config.settings import settings


class HttpClient:
    def __init__(self):
        self.session = requests.Session()
        self.last_request_time = 0

        # ----- Robust Retry Strategy -----
        retry_strategy = Retry(
            total=5,                    # retry 5 times
            backoff_factor=1,           # exponential backoff: 1s, 2s, 4s...
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        # ----- Identify as a real browser -----
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/json,application/xhtml+xml,application/xml;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
        })

    # ----- Soft Rate Limit -----
    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        wait_time = settings.RATE_LIMIT - elapsed
        if wait_time > 0:
            time.sleep(wait_time)

        # Add a small random jitter so you don't hit endpoints rhythmically
        time.sleep(random.uniform(0.25, 0.75))

    # ----- Unified GET with retries -----
    def _get(self, full_url):
        self._rate_limit()

        try:
            response = self.session.get(full_url, timeout=30)
        except requests.exceptions.RequestException as e:
            # Catch connection resets, timeouts, ssl errors, etc.
            print(f"[ERROR] Request failed: {e} → Retrying...")
            time.sleep(2)
            response = self.session.get(full_url, timeout=30)

        self.last_request_time = time.time()

        # Raise HTTP-level errors
        response.raise_for_status()
        return response.text

    # ----- Public Methods -----

    def get_frontend(self, url):
        full_url = f"{settings.FRONTEND_BASE_URL}{url}"
        return self._get(full_url)

    def get_backend(self, url):
        full_url = f"{settings.BACKEND_BASE_URL}{url}"
        return self._get(full_url)
