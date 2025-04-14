import requests
import re
import logging
from requests.exceptions import HTTPError, RequestException
import random

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
]

def validate_username(username):
    """Validate X username: 4-15 chars, letters, numbers, underscores."""
    pattern = r'^[a-zA-Z0-9_]{4,15}$'
    is_valid = bool(re.match(pattern, username))
    return is_valid, "Invalid: 4-15 letters, numbers, underscores" if not is_valid else ""

def check_availability(username):
    """Check X username availability via web request."""
    url = f"https://x.com/{username}"
    for attempt in range(3):
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        try:
            response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
            text_snippet = response.text[:500]
            logging.debug(f"X response for {username}: status={response.status_code}, text_snippet={text_snippet}")
            if response.status_code == 200:
                if "This account doesn’t exist" in response.text or "suspended" in response.text.lower():
                    return True, "Available"
                return False, "Taken"
            if response.status_code == 404:
                return True, "Available"
            return False, f"Error {response.status_code}"
        except HTTPError as e:
            status_code = e.response.status_code if e.response else "Unknown"
            logging.error(f"X HTTP Error for {username}: {e}")
            return False, f"Error {status_code}"
        except RequestException as e:
            if "NameResolutionError" in str(e):
                error_msg = "Error DNS"
            elif "ConnectTimeout" in str(e):
                error_msg = "Error Timeout"
            else:
                error_msg = "Error Network"
            logging.error(f"X Request Exception for {username}: {e}")
            return False, error_msg
        time.sleep(2 ** attempt)
    logging.error(f"X max retries reached for {username}")
    return False, "Error MaxRetries"