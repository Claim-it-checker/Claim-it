import requests
import re
import logging
import time
from requests.exceptions import RequestException

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_username(username):
    """
    Validate Pinterest username.
    Rules: 3-30 chars, letters, numbers, underscores. No spaces or other symbols.
    Returns: (is_valid: bool, error_msg: str)
    """
    if not username:
        return False, "Invalid: Username is empty"
    
    # Pinterest username regex: 3-30 chars, alphanumeric + _ only
    pattern = r'^[a-zA-Z0-9_]{3,30}$'
    if not re.match(pattern, username):
        return False, "Invalid: Must be 3-30 chars, letters, numbers, or underscores only"
    
    return True, ""

def check_availability(username):
    """
    Check if username is available on Pinterest via https://www.pinterest.com/{username}/.
    Invalid usernames redirect to https://[region].pinterest.com/?show_error=true#featured-boards.
    Returns: (is_available: bool, details: str)
    """
    logging.info(f"Checking pinterest for username {username}")
    url = f"https://www.pinterest.com/{username}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
            status_code = response.status_code
            
            # Check for redirect to error page (Available)
            if "show_error=true" in response.url:
                return True, "Available"
            
            # Check response content
            if status_code == 200:
                # Profile exists if user-specific content is present
                if '"pins"' in response.text or '"display_name"' in response.text:
                    return False, "Taken"
                return True, "Available"
            elif status_code == 404:
                return True, "Available"
            elif status_code == 429:
                logging.warning(f"Rate limited checking pinterest for {username}, attempt {attempt + 1}")
                time.sleep(2 ** attempt)
                continue
            else:
                logging.error(f"Unexpected status {status_code} for pinterest: {username}")
                return False, f"Error {status_code}"
        
        except RequestException as e:
            logging.error(f"Check error for pinterest with username {username}: {e}")
            if "Name or service not known" in str(e):
                return False, "Error DNS"
            elif "timeout" in str(e).lower():
                return False, "Error Timeout"
            else:
                return False, "Error Network"
            time.sleep(2 ** attempt)
    
    return False, "Error: Max retries reached"