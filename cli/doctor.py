"""
API health checks and credential validation.
"""

import sys
import os
import time
from pathlib import Path
from sentinelhub import SHConfig, SentinelHubCatalog
from utils.logger import get_logger

logger = get_logger(__name__)


def check_env_file() -> bool:
    """
    Checks if the .env file exists and contains the required keys.

    :return: True if valid, False otherwise.
    :rtype: bool
    """
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        logger.error("❌ .env file not found.")
        return False

    required_keys = ["SH_CLIENT_ID", "SH_CLIENT_SECRET"]
    missing_keys = []
    
    with open(env_path, "r") as f:
        content = f.read()
        for key in required_keys:
            if f"{key}=" not in content:
                missing_keys.append(key)
                
    if missing_keys:
        logger.error(f"❌ .env file is missing keys: {', '.join(missing_keys)}")
        return False
        
    logger.info("✅ .env file exists and contains required keys.")
    return True


def check_api_credentials() -> bool:
    """
    Attempts to authenticate with Sentinel Hub and perform a free catalog search.

    :return: True if authentication and API call succeed, False otherwise.
    :rtype: bool
    """
    from sentinel.config import get_sh_config
    
    try:
        config = get_sh_config()
    except Exception as e:
        logger.error(f"❌ Failed to load SHConfig: {e}")
        return False
        
    try:
        catalog = SentinelHubCatalog(config=config)
        # perform a minimal free catalog search to verify credentials
        catalog.get_collections()
        logger.info("✅ Sentinel Hub API authentication successful.")
        return True
    except Exception as e:
        logger.error(f"❌ Sentinel Hub API authentication failed: {e}")
        return False


def check_cache_dir() -> bool:
    """
    Checks if the joblib cache directory exists and is writable.

    :return: True if valid, False otherwise.
    :rtype: bool
    """
    cache_dir = Path(__file__).parent.parent / ".cache"
    
    if not cache_dir.exists():
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("✅ Created .cache directory.")
        except Exception as e:
            logger.error(f"❌ Failed to create .cache directory: {e}")
            return False
            
    if not os.access(cache_dir, os.W_OK):
        logger.error("❌ .cache directory is not writable.")
        return False
        
    size_bytes = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
    size_mb = size_bytes / (1024 * 1024)
    logger.info(f"✅ Cache directory is writable (Current size: {size_mb:.2f} MB)")
    return True


def check_nominatim_api() -> bool:
    """
    Pings the OpenStreetMap Nominatim API to ensure it's reachable.

    :return: True if reachable, False otherwise.
    :rtype: bool
    """
    import requests
    
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "DamAreaMeasure/0.1 (research project)"}
    params = {"q": "Hoover Dam", "format": "json", "limit": 1}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        logger.info("✅ OpenStreetMap Nominatim API is reachable.")
        return True
    except Exception as e:
        logger.error(f"❌ Nominatim API check failed: {e}")
        return False


def run_doctor_checks() -> None:
    """
    Runs all health checks and reports the overall status.
    """
    logger.info("\nRunning DamArea Doctor Checks...\n")
    
    checks = [
        check_env_file,
        check_api_credentials,
        check_cache_dir,
        check_nominatim_api
    ]
    
    success = True
    for check in checks:
        if not check():
            success = False
            
    print("-" * 40)
    if success:
        logger.info("🩺 All checks passed! The pipeline is ready to run.")
    else:
        logger.error("⚠️ Some checks failed. Please resolve the issues above before running the pipeline.")
        sys.exit(1)
