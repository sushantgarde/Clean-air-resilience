from sentinelhub import SHConfig
import os
from dotenv import load_dotenv

load_dotenv()

config = SHConfig()
config.sh_client_id = os.getenv("SENTINELHUB_CLIENT_ID")
config.sh_client_secret = os.getenv("SENTINELHUB_CLIENT_SECRET")
config.sh_base_url = "https://sh.dataspace.copernicus.eu"
config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

if not config.sh_client_id or not config.sh_client_secret:
    raise ValueError("Missing SENTINELHUB_CLIENT_ID / SENTINELHUB_CLIENT_SECRET in .env")

# Debug — confirm the config is actually pointing at CDSE, not the old sinergise service
print("Base URL:", config.sh_base_url)
print("Token URL:", config.sh_token_url)