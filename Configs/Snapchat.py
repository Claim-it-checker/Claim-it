import requests
import re
import logging
import time
from requests.exceptions import RequestException

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_username(username):
    """
    Validate Snapchat username.
    Rules: 3-15 chars, letters, numbers, underscores, periods, hyphens. Starts with letter,
    no consecutive special chars, no spaces.
    Returns: (is_valid: bool, error_msg: str)
    """
    if not username:
        return False, "Invalid: Username is empty"
    
    # Snapchat username regex: 3-15 chars, starts with letter, alphanumeric + _.-, no consecutive _.-, no spaces
    pattern = r'^[a-zA-Z][a-zA-Z0-9_.-]{2,14}$'
    if not re.match(pattern, username):
        return False, "Invalid: Must be 3-15 chars, start with a letter, use letters, numbers, underscores, periods, or hyphens"
    
    # Check for consecutive special chars
    if re.search(r'[_.-]{2,}', username):
        return False, "Invalid: No consecutive underscores, periods, or hyphens allowed"
    
    return True, ""

def check_availability(username):
    """
    Check if username is available on Snapchat via https://www.snapchat.com/add/{username}.
    Returns: (is_available: bool, details: str)
    """
    logging.info(f"Checking snapchat for username {username}")
    url = f"https://www.snapchat.com/add/{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=5)
            status_code = response.status_code
            
            if status_code == 404 or "user not found" in response.text.lower():
                return True, "Available"
            elif status_code == 200:
                return False, "Taken"
            elif status_code == 429:
                logging.warning(f"Rate limited checking snapchat for {username}, attempt {attempt + 1}")
                time.sleep(2 ** attempt)
                continue
            else:
                logging.error(f"Unexpected status {status_code} for snapchat: {username}")
                return False, f"Error {status_code}"
        
        except RequestException as e:
            logging.error(f"Check error for snapchat with username {username}: {e}")
            if "Name or service not known" in str(e):
                return False, "Error DNS"
            elif "timeout" in str(e).lower():
                return False, "Error Timeout"
            else:
                return False, "Error Network"
            time.sleep(2 ** attempt)
    
    return False, "Error: Max retries reached"