"""
Rate status CLI command to monitor Sentinel Hub API consumption.
"""

import time
import json
from datetime import datetime, timezone
from sentinel.rate_limiter import tracker
from utils.logger import get_logger

logger = get_logger(__name__)


def show_rate_status(json_format: bool = False, watch: bool = False) -> None:
    """
    Fetches and displays the current Sentinel Hub rate limits.
    """
    logger.info("Fetching rate limits from Sentinel Hub...")

    def fetch_and_print():
        try:
            limits = tracker.fetch_current_limits()
            
            if json_format:
                output = {
                    "limit": limits["limit"],
                    "remaining": limits["remaining"],
                    "reset_at": limits["reset_at"].isoformat() if limits["reset_at"] else None,
                    "pu_spent": limits["pu_spent"],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                print(json.dumps(output, indent=4))
                return

            print("\n" + "=" * 40)
            print(f"{'SENTINEL HUB RATE LIMIT STATUS':^40}")
            print("=" * 40)
            
            if limits["limit"] is not None:
                percent = (limits["remaining"] / limits["limit"]) * 100 if limits["limit"] > 0 else 0
                status_color = "🟢" if percent > 50 else ("🟡" if percent > 10 else "🔴")
                
                print(f" Status:     {status_color} {percent:.1f}% remaining")
                print(f" Requests:   {limits['remaining']} / {limits['limit']} (remaining / total)")
                if limits["reset_at"]:
                    reset_time_local = limits["reset_at"].astimezone()
                    print(f" Resets at:  {reset_time_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            else:
                print(" Could not retrieve rate limit headers.")
                
            print(f" PU Spent:   {limits['pu_spent']:.3f} PU (this session)")
            print("=" * 40)
            
        except Exception as e:
            logger.error(f"Failed to fetch rate limits: {e}")

    if not watch:
        fetch_and_print()
    else:
        print("\nStarting live monitor... (Press Ctrl+C to stop)")
        try:
            while True:
                fetch_and_print()
                time.sleep(10)
        except KeyboardInterrupt:
            print("\nStopped monitoring.")
