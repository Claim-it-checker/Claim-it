import requests
import re
import logging
from requests.exceptions import HTTPError, RequestException
import random
import time

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
]

def validate_username(username):
    """Validate Fortnite username: 3-16 chars, letters, numbers, underscores, periods."""
    pattern = r'^[a-zA-Z0-9_.]{3,16}$'
    is_valid = bool(re.match(pattern, username))
    return is_valid, "Invalid: 3-16 letters, numbers, underscores, periods" if not is_valid else ""

def check_availability(username):
    """Check Fortnite username availability via Epic Games store profile using API."""
    url = f"[invalid url, do not cite]
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://fortniteapi.com/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
            logging.debug(f"Fortnite response for {username}: status={response.status_code}, url={response.url}")
            
            if response.status_code == 404 or "not found" in response.text.lower():
                return True, "Available"
            if response.status_code == 200 and '"displayName"' in response.text and username.lower() in response.text.lower():
                return False, "Taken"
            return False, f"Error {response.status_code}"
        except HTTPError as e:
            status_code = e.response.status_code if e.response else "Unknown"
            logging.error(f"Fortnite HTTP Error for {username}: {e}")
            return False, f"Error {status_code}"
        except RequestException as e:
            if "NameResolutionError" in str(e):
                error_msg = "Error DNS"
            elif "ConnectTimeout" in str(e):
                error_msg = "Error Timeout"
            else:
                error_msg = "Error Network"
            logging.error(f"Fortnite Request Exception for {username}: {e}")
            return False, error_msg
        time.sleep(2 ** attempt)
    
    logging.error(f"Fortnite max retries reached for {username}")
    return False, "Error MaxRetries"