import os
from dotenv import load_dotenv

load_dotenv()

PROXY_TEST_URL = os.getenv("PROXY_TEST_URL")
PROXY_TEST_TIMEOUT = int(os.getenv("PROXY_TEST_TIMEOUT"))
PROXY_LIST_URL = os.getenv("PROXY_LIST_URL")
