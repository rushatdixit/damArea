# test_auth.py

from sentinelhub import SHConfig, SentinelHubSession

config = SHConfig()
config.sh_client_id = "9506c6a1-7b90-4031-95ce-d7eea849eb13"
config.sh_client_secret = "r6ReFeytqnYL4YNxII1WS9CiuicBeAli"

session = SentinelHubSession(config=config)
print("Token acquired successfully")
