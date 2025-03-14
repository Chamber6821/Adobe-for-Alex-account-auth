import random
import requests
from loguru import logger
from config.settings import PROXY_LIST_URL, PROXY_TEST_URL, PROXY_TEST_TIMEOUT


def fetch_proxies():
    try:
        response = requests.get(PROXY_LIST_URL, timeout=PROXY_TEST_TIMEOUT)
        response.raise_for_status()
        proxies = response.json()
        return [{"host": p.split(":")[0], "port": int(p.split(":")[1])} for p in proxies]
    except requests.RequestException as e:
        logger.error(f"Error loading the proxy list: {e}")
        return []


def is_proxy_valid(proxy):
    try:
        proxy_url = f"http://{proxy['host']}:{proxy['port']}"
        proxies_dict = {"http": proxy_url, "https": proxy_url}
        response = requests.get(PROXY_TEST_URL, proxies=proxies_dict, timeout=PROXY_TEST_TIMEOUT)
        if response.status_code == 200:
            logger.success(f"Proxy {proxy['host']}:{proxy['port']} is working.")
            return True
    except requests.RequestException as e:
        logger.error(f"Proxy {proxy['host']}:{proxy['port']} is not working: {e}")
    return False


def get_working_proxy():
    while True:
        proxies = fetch_proxies()
        if not proxies:
            logger.critical("Failed to load the proxy.")
            continue
        random.shuffle(proxies)
        for proxy in proxies:
            if is_proxy_valid(proxy):
                return proxy
        logger.warning("All proxies are not working, we repeat the request.")
