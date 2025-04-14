import requests
import re
import logging
from requests.exceptions import HTTPError, RequestException
import time

def validate_username(username):
    """Validate Telegram username: 5-32 chars, letters, numbers, underscores."""
    pattern = r'^[a-zA-Z0-9_]{5,32}$'
    is_valid = bool(re.match(pattern, username))
    return is_valid, "Invalid: 5-32 letters, numbers, underscores" if not is_valid else ""

def check_availability(username):
    """Check Telegram username availability via web scraping."""
    url = f"https://t.me/{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html"
    }
    
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
            text_snippet = response.text[:1000]
            logging.debug(f"Telegram response for {username}: status={response.status_code}, text_snippet={text_snippet}")
            if "If you have Telegram, you can contact" not in response.text and "tgme_page_title" not in response.text:
                return True, "Available"
            return False, "Taken"
        except HTTPError as e:
            status_code = e.response.status_code if e.response else "Unknown"
            logging.error(f"Telegram HTTP Error for {username}: {e}")
            if status_code == 429:
                return False, "Rate Limited"
            return False, f"Error {status_code}"
        except RequestException as e:
            error_msg = (
                "Error DNS" if "NameResolutionError" in str(e) else
                "Error Timeout" if "ConnectTimeout" in str(e) else
                "Error Network"
            )
            logging.error(f"Telegram Request Exception for {username}: {e}")
            return False, error_msg
        time.sleep(2 ** attempt)
    logging.error(f"Telegram max retries reached for {username}")
    return False, "Error MaxRetries"