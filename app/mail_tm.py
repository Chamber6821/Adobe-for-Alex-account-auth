import time
import requests
from datetime import datetime, timezone, timedelta
from loguru import logger
from dateutil import parser
import re

class MailTM:
    def __init__(self, address: str, password: str):
        self.address = address
        self.password = password
        self.base_url = "https://api.mail.tm"
        self.token = self.get_mail_token()

    def get_mail_token(self) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/token",
                json={"address": self.address, "password": self.password},
            )
            response.raise_for_status()
            return response.json()["token"]
        except Exception as e:
            logger.error(f"Failed to get MailTM token: {e}")
            raise

    def get_mail_code(self) -> str:
        time_gap = timedelta(minutes=1)
        time_edge = datetime.now(timezone.utc) - time_gap
        tries = 5
        while tries > 0:
            tries -= 1
            response = requests.get(
                f"{self.base_url}/messages",
                headers={"Authorization": f"Bearer {self.token}"},
            )
            response.raise_for_status()
            messages = response.json().get("hydra:member", [])
            if not messages:
                logger.info("No messages received, retrying...")
                time.sleep(5)
                continue
            last_message = messages[0]
            updated_at = parser.parse(last_message["updatedAt"]).astimezone(timezone.utc)
            if last_message["seen"] or updated_at < time_edge:
                logger.info(f"Skipping message updated at {updated_at} (already seen or outdated)")
                time.sleep(5)
                continue
            message_id = last_message["id"]
            requests.patch(
                f"{self.base_url}/messages/{message_id}",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/merge-patch+json",
                },
                json={"seen": True},
            )
            message_text = last_message["intro"] + last_message.get("text", "")
            logger.debug(f"Checking message content: {message_text}")
            match = re.search(r"\b\d{6}\b", message_text)
            if match:
                logger.info("Verification code found")
                return match.group(0)
            else:
                logger.info("Verification code not found, retrying...")
                time.sleep(5)
        logger.error("Timeout waiting for email code")
        raise TimeoutError
