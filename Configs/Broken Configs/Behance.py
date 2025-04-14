import requests
import re
import logging
import time
from requests.exceptions import RequestException

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_username(username):
    """
    Validate Behance username.
    Rules: 2-50 chars, letters, numbers, underscores, hyphens. No spaces, no consecutive _ or -.
    Returns: (is_valid: bool, error_msg: str)
    """
    if not username:
        return False, "Invalid: Username is empty"
    
    # Behance username regex: 2-50 chars, alphanumeric + _-
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9_-]{0,48}[a-zA-Z0-9]$'
    if not re.match(pattern, username):
        return False, "Invalid: Must be 2-50 chars, letters, numbers, underscores, or hyphens"
    
    # Check for consecutive underscores or hyphens
    if re.search(r'[-_]{2,}', username):
        return False, "Invalid: No consecutive underscores or hyphens allowed"
    
    return True, ""

def check_availability(username):
    """
    Check if username is available on Behance via https://www.behance.net/{username}.
    Taken: 200 with '"user"' JSON. Available: 404 or redirect to search.
    Returns: (is_available: bool, details: str)
    """
    logging.info(f"Checking behance for username {username}")
    url = f"https://www.behance.net/{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
            status_code = response.status_code
            
            if status_code == 404 or "search?field" in response.url:
                return True, "Available"
            elif status_code == 200:
                if '"user"' in response.text or '"profile"' in response.text:
                    return False, "Taken"
                return True, "Available"
            elif status_code == 429:
                logging.warning(f"Rate limited checking behance for {username}, attempt {attempt + 1}")
                time.sleep(2 ** attempt)
                continue
            else:
                logging.error(f"Unexpected status {status_code} for behance: {username}")
                return False, f"Error {status_code}"
        
        except RequestException as e:
            logging.error(f"Check error for behance with username {username}: {e}")
            if "Name or service not known" in str(e):
                return False, "Error DNS"
            elif "timeout" in str(e).lower():
                return False, "Error Timeout"
            else:
                return False, "Error Network"
            time.sleep(2 ** attempt)
    
    return False, "Error: Max retries reached"