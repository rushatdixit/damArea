import os
from dotenv import load_dotenv
from sentinelhub import SHConfig

load_dotenv()

def get_sh_config() -> SHConfig:
    config = SHConfig()
    config.sh_client_id = os.getenv("SH_CLIENT_ID")
    config.sh_client_secret = os.getenv("SH_CLIENT_SECRET")
    config.instance_id = os.getenv("SH_INSTANCE_ID")
    if not config.sh_client_id or not config.sh_client_secret:
        raise ValueError("Sentinel Hub credentials not found in environment variables.")

    return config

get_sh_config()