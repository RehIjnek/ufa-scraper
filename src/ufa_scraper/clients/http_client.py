import time
import requests
from ufa_scraper.config.settings import settings

class HttpClient:
    def __init__(self):
        self.session = requests.Session()
        self.last_request_time = 0

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < settings.RATE_LIMIT:
            time.sleep(settings.RATE_LIMIT - elapsed)

    def get_frontend(self, url):
        full_url = f"{settings.FRONTEND_BASE_URL}{url}"
        self._rate_limit()

        response = self.session.get(full_url, timeout=10)
        self.last_request_time = time.time()

        response.raise_for_status()
        return response.text

    def get_backend(self, url):
        full_url = f"{settings.BACKEND_BASE_URL}{url}"
        self._rate_limit()

        response = self.session.get(full_url, timeout=10)
        self.last_request_time = time.time()

        response.raise_for_status()
        return response.text