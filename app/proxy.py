import random
import requests
from loguru import logger
from config.settings import proxies, PROXY_TEST_URL, PROXY_TEST_TIMEOUT

def load_proxies():
    valid_proxies = []
    for proxy in proxies:
        host, port = proxy.split(":")
        proxy_info = {"host": host, "port": int(port)}
        valid_proxies.append(proxy_info)
    return valid_proxies

def get_random_proxy(proxies):
    if not proxies:
        logger.critical("There are no available proxies!")
        raise ValueError
    while proxies:
        proxy = random.choice(proxies)
        if is_proxy_valid(proxy):
            return proxy
        else:
            proxies.remove(proxy)
    logger.critical("All proxies are non-working!")
    raise ValueError

def is_proxy_valid(proxy):
    try:
        proxy_url = f"http://{proxy['host']}:{proxy['port']}"
        proxies_dict = {
            "http": proxy_url,
            "https": proxy_url
        }
        response = requests.get(PROXY_TEST_URL, proxies=proxies_dict, timeout=int(PROXY_TEST_TIMEOUT))
        if response.status_code == 200:
            logger.success(f"Proxy {proxy['host']}:{proxy['port']} works.")
            return True
        else:
            return False
    except requests.RequestException as e:
        logger.error(f"Error checking proxy {proxy['host']}:{proxy['port']}: {e}")
        return False
