import os
from dotenv import load_dotenv

load_dotenv()
print("Client ID:", os.getenv("SENTINELHUB_CLIENT_ID"))
print("Client Secret set:", bool(os.getenv("SENTINELHUB_CLIENT_SECRET")))