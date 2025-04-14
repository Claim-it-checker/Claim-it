import requests
import re
import logging
import time
from requests.exceptions import RequestException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_username(username):
    if not username:
        return False, "Invalid: Username is empty"
    pattern = r'^[a-zA-Z0-9_-]{4,20}$'
    if not re.match(pattern, username):
        return False, "Invalid: Must be 4-20 chars, letters, numbers, underscores, or hyphens"
    return True, ""

def check_availability(username):
    logging.info(f"Checking etsy for username {username}")
    url = f"https://www.etsy.com/shop/{username}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
            if response.status_code == 404 or "etsy.com/search" in response.url:
                return True, "Available"
            elif response.status_code == 200 and '"shop_name"' in response.text:
                return False, "Taken"
            elif response.status_code == 429:
                logging.warning(f"Rate limited checking etsy for {username}, attempt {attempt + 1}")
                time.sleep(2 ** attempt)
                continue
            else:
                logging.error(f"Unexpected status {response.status_code} for etsy: {username}")
                return False, f"Error {response.status_code}"
        except RequestException as e:
            logging.error(f"Check error for etsy with username {username}: {e}")
            if "Name or service not known" in str(e):
                return False, "Error DNS"
            elif "timeout" in str(e).lower():
                return False, "Error Timeout"
            else:
                return False, "Error Network"
            time.sleep(2 ** attempt)
    return False, "Error: Max retries reached"