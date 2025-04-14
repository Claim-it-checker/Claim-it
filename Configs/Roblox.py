import requests
import re
import logging
from requests.exceptions import HTTPError, RequestException
import json
import time

def validate_username(username):
    """Validate Roblox username: 3-20 chars, letters, numbers, underscores."""
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    is_valid = bool(re.match(pattern, username))
    return is_valid, "Invalid: 3-20 letters, numbers, underscores" if not is_valid else ""

def check_availability(username):
    """Check Roblox username availability via API."""
    url = "https://users.roblox.com/v1/usernames/users"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    payload = {
        "usernames": [username],
        "excludeBannedUsers": True
    }
    
    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=5)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Roblox response for {username}: status={response.status_code}, data={data}")
            if len(data.get("data", [])) == 0:
                return True, "Available"
            return False, "Taken"
        except HTTPError as e:
            status_code = e.response.status_code if e.response else "Unknown"
            logging.error(f"Roblox HTTP Error for {username}: {e}")
            if status_code == 429:
                return False, "Rate Limited"
            return False, f"Error {status_code}"
        except RequestException as e:
            error_msg = (
                "Error DNS" if "NameResolutionError" in str(e) else
                "Error Timeout" if "ConnectTimeout" in str(e) else
                "Error Network"
            )
            logging.error(f"Roblox Request Exception for {username}: {e}")
            return False, error_msg
        time.sleep(2 ** attempt)
    logging.error(f"Roblox max retries reached for {username}")
    return False, "Error MaxRetries"