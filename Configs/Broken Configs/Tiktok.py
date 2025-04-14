import requests
import re
import logging
from requests.exceptions import HTTPError, RequestException

# Headers from the working script to avoid blocks
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US",
    "content-type": "application/json"
}

def validate_username(username):
    """Validate TikTok username: 2-24 chars, letters, numbers, underscores, periods."""
    pattern = r'^[a-zA-Z0-9_.]{2,24}$'
    is_valid = bool(re.match(pattern, username))
    return is_valid, "Invalid: 2-24 letters, numbers, underscores, periods" if not is_valid else ""

def check_availability(username):
    """Check TikTok username availability by searching for 'Couldn't find this account' in response text."""
    url = f"https://www.tiktok.com/@{username}"
    for attempt in range(3):
        try:
            response = requests.get(url, headers=HEADERS, timeout=5, allow_redirects=True)
            text_snippet = response.text[:1000]  # Limit for logging
            logging.debug(f"TikTok response for {username}: status={response.status_code}, url={response.url}, text_snippet={text_snippet}")
            if "Couldn't find this account" in response.text:
                return True, "Available"
            return False, "Taken"
        except HTTPError as e:
            status_code = e.response.status_code if e.response else "Unknown"
            logging.error(f"TikTok HTTP Error for {username}: {e}")
            return False, f"Error {status_code}"
        except RequestException as e:
            if "NameResolutionError" in str(e):
                error_msg = "Error DNS"
            elif "ConnectTimeout" in str(e):
                error_msg = "Error Timeout"
            else:
                error_msg = "Error Network"
            logging.error(f"TikTok Request Exception for {username}: {e}")
            return False, error_msg
        time.sleep(2 ** attempt)
    logging.error(f"TikTok max retries reached for {username}")
    return False, "Error MaxRetries"