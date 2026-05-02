"""
Rate limit tracker singleton and Sentinel Hub API header querying.
"""

import time
import requests
from datetime import datetime, timezone
from sentinel.config import get_sh_config
from utils.logger import get_logger

logger = get_logger(__name__)


class RateLimitTracker:
    """
    Singleton to track and fetch Sentinel Hub rate limits.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RateLimitTracker, cls).__new__(cls)
            cls._instance.remaining = None
            cls._instance.limit = None
            cls._instance.reset_at = None
            cls._instance.pu_spent = 0.0
            cls._instance.token = None
            cls._instance.token_expiry = 0
        return cls._instance

    def _ensure_token(self):
        """
        Ensures a valid OAuth token is available.
        """
        now = time.time()
        if not self.token or now > self.token_expiry - 60:
            config = get_sh_config()
            
            data = {
                "grant_type": "client_credentials",
                "client_id": config.sh_client_id,
                "client_secret": config.sh_client_secret
            }
            url = "https://services.sentinel-hub.com/oauth/token"
            resp = requests.post(url, data=data, timeout=10)
            resp.raise_for_status()
            token_data = resp.json()
            
            self.token = token_data.get("access_token")
            self.token_expiry = now + token_data.get("expires_in", 3600)

    def fetch_current_limits(self) -> dict:
        """
        Makes a lightweight API call to fetch current rate limit headers.
        
        :return: Dictionary of parsed rate limit headers.
        :rtype: dict
        """
        self._ensure_token()
        
        url = "https://services.sentinel-hub.com/api/v1/catalog/collections"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code >= 500:
                logger.debug(f"Sentinel Hub rate limit endpoint is temporarily unavailable ({e.response.status_code}). Using cached limits.")
                return {
                    "limit": self.limit,
                    "remaining": self.remaining,
                    "reset_at": self.reset_at,
                    "pu_spent": self.pu_spent
                }
            raise
        
        # Parse headers
        # Sentinel Hub returns: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
        r_limit = resp.headers.get("X-RateLimit-Limit")
        r_remain = resp.headers.get("X-RateLimit-Remaining")
        r_reset = resp.headers.get("X-RateLimit-Reset")
        pu_spent = resp.headers.get("X-ProcessingUnits-Spent", "0")
        
        try:
            if r_limit is not None:
                self.limit = int(r_limit)
            if r_remain is not None:
                self.remaining = int(r_remain)
            if r_reset is not None:
                self.reset_at = datetime.fromtimestamp(int(r_reset), tz=timezone.utc)
            if pu_spent is not None:
                self.pu_spent += float(pu_spent)
        except ValueError as e:
            logger.debug(f"Failed to parse rate limit headers: {e}")
            
        return {
            "limit": self.limit,
            "remaining": self.remaining,
            "reset_at": self.reset_at,
            "pu_spent": self.pu_spent
        }

    def throttle_if_needed(self, min_remaining: int = 10, sleep_time: int = 2) -> None:
        """
        Proactively pauses execution if the remaining request quota drops below the threshold.
        """
        # Fetch fresh limits occasionally or rely on recent calls
        self.fetch_current_limits()
        
        if self.remaining is not None and self.remaining < min_remaining:
            logger.warning(f"⚠️ Approaching rate limit ({self.remaining}/{self.limit} remaining). Throttling execution.")
            time.sleep(sleep_time)

tracker = RateLimitTracker()
