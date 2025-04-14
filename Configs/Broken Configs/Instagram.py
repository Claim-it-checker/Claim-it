import requests
import re
import logging
from requests.exceptions import HTTPError, RequestException
import time

def validate_username(username):
    """Validate Instagram username: 1-30 chars, letters, numbers, periods, underscores."""
    pattern = r'^[a-zA-Z0-9._]{1,30}$'
    is_valid = bool(re.match(pattern, username))
    return is_valid, "Invalid: 1-30 letters, numbers, periods, underscores" if not is_valid else ""

def check_availability(username):
    """Check Instagram username availability via web scraping."""
    url = f"https://www.instagram.com/{username}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html"
    }
    
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
            text_snippet = response.text[:1000]
            logging.debug(f"Instagram response for {username}: status={response.status_code}, text_snippet={text_snippet}")
            if "Page Not Found" in response.text or response.status_code == 404:
                return True, "Available"
            return False, "Taken"
        except HTTPError as e:
            status_code = e.response.status_code if e.response else "Unknown"
            logging.error(f"Instagram HTTP Error for {username}: {e}")
            if status_code == 429:
                return False, "Rate Limited"
            return False, f"Error {status_code}"
        except RequestException as e:
            error_msg = (
                "Error DNS" if "NameResolutionError" in str(e) else
                "Error Timeout" if "ConnectTimeout" in str(e) else
                "Error Network"
            )
            logging.error(f"Instagram Request Exception for {username}: {e}")
            return False, error_msg
        time.sleep(2 ** attempt)
    logging.error(f"Instagram max retries reached for {username}")
    return False, "Error MaxRetries"