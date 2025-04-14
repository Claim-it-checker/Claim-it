import requests
import re
import logging
from requests.exceptions import HTTPError, RequestException
import time

def validate_username(username):
    """Validate Twitch username: 4-25 chars, letters, numbers, underscores."""
    pattern = r'^[a-zA-Z0-9_]{4,25}$'
    is_valid = bool(re.match(pattern, username))
    return is_valid, "Invalid: 4-25 letters, numbers, underscores" if not is_valid else ""

def check_availability(username):
    """Check Twitch username availability via API."""
    url = f"https://api.twitch.tv/helix/users?login={username}"
    headers = {
        "Client-ID": "gp762nuuoqcoxypju8c9io9qdn4p1ar",  # Public client ID
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Twitch response for {username}: status={response.status_code}, data={data}")
            if len(data.get("data", [])) == 0:
                return True, "Available"
            return False, "Taken"
        except HTTPError as e:
            status_code = e.response.status_code if e.response else "Unknown"
            logging.error(f"Twitch HTTP Error for {username}: {e}")
            if status_code == 429:
                return False, "Rate Limited"
            return False, f"Error {status_code}"
        except RequestException as e:
            error_msg = (
                "Error DNS" if "NameResolutionError" in str(e) else
                "Error Timeout" if "ConnectTimeout" in str(e) else
                "Error Network"
            )
            logging.error(f"Twitch Request Exception for {username}: {e}")
            return False, error_msg
        time.sleep(2 ** attempt)
    logging.error(f"Twitch max retries reached for {username}")
    return False, "Error MaxRetries"