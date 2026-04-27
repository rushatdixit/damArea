"""
Configuration auditor to show the effective pipeline config.
"""

import os
from pathlib import Path
from sentinel.config import get_sh_config
from utils.logger import get_logger

logger = get_logger(__name__)


def show_config(json_format: bool = False) -> None:
    """
    Reads all configuration values across constants.py, .env, and hardcoded
    parameters, and displays them in a single table or JSON object.
    """
    import json
    import constants
    
    config_dict = {}
    
    # Load from constants.py
    for key in dir(constants):
        if not key.startswith("__") and key.isupper():
            config_dict[key] = {
                "value": getattr(constants, key),
                "source": "constants.py"
            }
            
    # Load from .env
    env_keys = ["SH_CLIENT_ID", "SH_CLIENT_SECRET", "SH_INSTANCE_ID"]
    for key in env_keys:
        val = os.getenv(key)
        if val:
            if key == "SH_CLIENT_SECRET":
                val = "****" + val[-4:] if len(val) > 4 else "****"
            config_dict[key] = {
                "value": val,
                "source": ".env"
            }
            
    # Hardcoded values known in the codebase
    config_dict["Coarse resolutions (unc sweep)"] = {
        "value": "[100, 200, ..., 1000]",
        "source": "orchestration.py:167"
    }
    config_dict["Threshold epsilon (unc sweep)"] = {
        "value": "0.05",
        "source": "orchestration.py:149"
    }
    config_dict["Retry backoff base"] = {
        "value": "2s",
        "source": "request.py:27"
    }
    config_dict["Retry max attempts"] = {
        "value": "5",
        "source": "request.py:27"
    }
    config_dict["Max cloud cover"] = {
        "value": "0.2",
        "source": "request.py:97"
    }
    config_dict["ThreadPoolExecutor workers"] = {
        "value": "5 (1 if debug)",
        "source": "timeseries_analysis.py:153"
    }
    config_dict["Tile size (streaming)"] = {
        "value": "2000m",
        "source": "tile_stream.py:60"
    }
    config_dict["Rate limit sleep (debug mode)"] = {
        "value": "1.5s",
        "source": "raw_data.py:77"
    }

    if json_format:
        output = {k: v["value"] for k, v in config_dict.items()}
        print(json.dumps(output, indent=4))
        return

    print("\nEffective Pipeline Configuration:")
    print("-" * 80)
    print(f"{'Parameter':<35} | {'Value':<20} | {'Source':<20}")
    print("-" * 80)
    for key, data in config_dict.items():
        print(f"{key:<35} | {str(data['value']):<20} | {data['source']:<20}")
    print("-" * 80)
