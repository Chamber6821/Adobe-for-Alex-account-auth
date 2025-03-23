import time
import base64
import shutil
import json
import names
from datetime import datetime, UTC
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium_stealth import stealth
import undetected_chromedriver as uc
from loguru import logger
import os
from .mail_tm import MailTM

class Eyes:
    def __init__(self, method: str, email: str, browser: webdriver.Chrome):
        timestamp = datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        self.directory = f"screenshots/{timestamp}-{method}-{email}"
        self.index = 0
        self.browser = browser
        os.makedirs(self.directory, exist_ok=True)

    def look(self):
        try:
            filename = f"{self.directory}/{str(self.index).zfill(2)}.png"
            self.index += 1
            logger.info(f"Capturing screenshot: {filename}")
            screenshot = self.browser.get_screenshot_as_base64()
            with open(filename, "wb") as file:
                file.write(base64.b64decode(screenshot))
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")

    def drop(self):
        try:
            logger.warning(f"Deleting directory: {self.directory}")
            shutil.rmtree(self.directory, ignore_errors=True)
        except Exception as e:
            logger.error(f"Failed to delete directory: {e}")


class Selenium:
    def __init__(self, proxy):
        try:
            options = uc.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument(f"--proxy-server={proxy['host']}:{proxy['port']}")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-notifications")
            options.add_argument("--log-level=0")
            options.add_argument("--verbose")
            self.driver = uc.Chrome(driver_executable_path='/usr/bin/chromedriver', options=options)
            self.eyes = None
            stealth(
                self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
            logger.success("Selenium initialized successfully")
        except Exception as e:
            logger.critical(f"Failed to initialize Selenium: {e}")
            raise

    def login(self, email: str, password: str) -> str:
        self.eyes = Eyes("login", email, self.driver)
        try:
            logger.info("Starting login process")
            self.get_page_without_webdriver_flag("https://adminconsole.adobe.com")
            time.sleep(2)
            email_input = WebDriverWait(self.driver, 180).until(
                EC.presence_of_element_located((By.ID, "EmailPage-EmailField"))
            )
            email_input.send_keys(email, Keys.ENTER)
            self.eyes.look()
            time.sleep(2)
            WebDriverWait(self.driver, 180).until(EC.staleness_of(email_input))
            if not self.driver.find_elements(By.ID, "PasswordPage-PasswordField"):
                logger.info("Waiting for email verification code")
                mail_code_tries = 2
                while mail_code_tries > 0:
                    WebDriverWait(self.driver, 180).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '*[data-id="Page-PrimaryButton"]'))
                    ).click()
                    self.eyes.look()
                    time.sleep(2)
                    if self.driver.find_elements(By.CSS_SELECTOR, '*[data-id="ErrorPage-Title"]'):
                        error_message = self.driver.find_element(By.CSS_SELECTOR, '*[data-id="ErrorPage-Title"]').text
                        self.eyes.look()
                        logger.error(f"New emails temporary deny: {error_message}")
                    try:
                        mail_tm = MailTM(email, password)
                        code = mail_tm.get_mail_code()
                    except Exception as ex:
                        logger.info(f"{ex}")
                        resend_button = WebDriverWait(self.driver, 180).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, '*[data-id="ChallengeCodePage-Resend"]'))
                        )
                        resend_button.click()
                        mail_code_tries -= 1
                        continue
                    code_input = WebDriverWait(self.driver, 180).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '*[data-id="CodeInput-0"]'))
                    )
                    code_input.send_keys(code)
                    break
                if mail_code_tries == 0:
                    logger.error("Failed to get mail code")
                    raise
            password_input = WebDriverWait(self.driver, 180).until(
                EC.presence_of_element_located((By.ID, "PasswordPage-PasswordField"))
            )
            password_input.send_keys(password, Keys.ENTER)
            time.sleep(2)
            self.eyes.look()
            WebDriverWait(self.driver, 180).until(EC.staleness_of(password_input))
            while self.driver.find_elements(By.CSS_SELECTOR, '*[data-id$="-skip-btn"]'):
                self.eyes.look()
                skip_button = self.driver.find_element(By.CSS_SELECTOR, '*[data-id$="-skip-btn"]')
                skip_button.click()
                WebDriverWait(self.driver, 180).until(EC.staleness_of(skip_button))
            self.eyes.look()
            WebDriverWait(self.driver, 180).until(EC.url_contains("https://adminconsole.adobe.com"))
            time.sleep(2)
            token = self.extract_token()
            logger.success("Login successful!")
            self.eyes.look()
            self.eyes.drop()
            return token
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return ""

    def register(self, email: str, password: str) -> str:
        self.eyes = Eyes("register", email, self.driver)
        try:
            logger.info("Starting registration process")
            self.get_page_without_webdriver_flag("https://adminconsole.adobe.com")
            time.sleep(2)
            create_account_link = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '*[data-id="EmailPage-CreateAccountLink"]'))
            )
            create_account_link.click()
            time.sleep(2)
            email_input = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '*[data-id="Signup-EmailField"]'))
            )
            password_input = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '*[data-id="Signup-PasswordField"]'))
            )
            email_input.send_keys(email)
            password_input.send_keys(password)
            time.sleep(2)
            self.eyes.look()
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                '*[data-id="PasswordStrengthRule-notCommonlyUsed"] img[src="/img/generic/check.svg"]'))
            )
            continue_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '*[data-id="Signup-CreateAccountBtn"]'))
            )
            continue_button.click()
            first_name_input = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '*[data-id="Signup-FirstNameField"]'))
            )
            last_name_input = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '*[data-id="Signup-LastNameField"]'))
            )
            first_name_input.send_keys(names.get_first_name())
            last_name_input.send_keys(names.get_last_name())
            time.sleep(2)
            self.eyes.look()
            create_account_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '*[data-id="Signup-CreateAccountBtn"]'))
            )
            create_account_button.click()
            self.eyes.look()
            time.sleep(10)
            self.eyes.look()
            WebDriverWait(self.driver, 30).until(EC.url_contains("https://adminconsole.adobe.com"))
            time.sleep(2)
            token = self.extract_token()
            logger.success("Registration successful!")
            self.eyes.look()
            self.eyes.drop()
            return token
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return ""

    def extract_token(self):
        time.sleep(10)
        storage = self.driver.execute_script("return window.sessionStorage")
        for key in storage:
            if "adobeid_ims_access_token" in key:
                return json.loads(storage[key])["tokenValue"]
        logger.error("Failed to get session token")
        raise

    def get_page_without_webdriver_flag(self, url: str):
        try:
            self.driver.get(url)
        except Exception as e:
            logger.error(f"Failed to load page {url}: {e}")

    def close(self):
        try:
            self.driver.quit()
            logger.success("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")