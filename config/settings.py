import os
from dotenv import load_dotenv

load_dotenv()

PROXY_TEST_URL = os.getenv("PROXY_TEST_URL")
PROXY_TEST_TIMEOUT = os.getenv("PROXY_TEST_TIMEOUT")
PROXY_LIST = os.getenv("PROXY_LIST_URL")

if PROXY_LIST:
    proxies = PROXY_LIST.split(";")
else:
    proxies = []
