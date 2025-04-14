import os
import re
import logging
import platform
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
import threading
import webbrowser
import requests
from bs4 import BeautifulSoup
import filelock
import importlib.util

# Open Telegram link
webbrowser.open("https://t.me/Claim_it_checker")

# Custom ASCII art and title
ASCII_ART = """
.---------------------------------------.
|  ____ _       _                 _ _   |
| / ___| | __ _(_)_ __ ___       (_| |_ |
|| |   | |/ _` | | '_ ` _ \ _____| | __||
|| |___| | (_| | | | | | | |_____| | |_ |
| \____|_|\__,_|_|_| |_| |_|     |_|\__||
'---------------------------------------'
Aᴅᴠᴀɴᴄᴇᴅ Mᴜʟᴛɪ Sᴇʀᴠɪᴄᴇ Usᴇʀɴᴀᴍᴇ Vᴀʟɪᴅᴀᴛᴏʀ

Mᴀᴅᴇ ʙʏ @ɴᴇᴡᴍᴇᴘᴇ ғᴏʀ Bʀᴇᴀᴄʜᴇᴅ Aɴᴅ Cʀᴀᴄᴋᴇᴅ Nɪɢɢᴇʀs (Fᴜᴄᴋ ᴘᴀᴛᴄʜᴇᴅ)

Lᴏᴏᴋɪɴɢ ғᴏʀ ᴍᴏʀᴇ ᴍᴏᴅᴜʟᴇs? Jᴏɪɴ t.me/Claim_it_checker
‎         
            ᴛʜɪs ɪs ᴍʏ ғɪʀsᴛ ᴛᴏᴏʟ ɪᴍ ʀᴇʟᴇᴀsɪɴɢ,
                   sᴏ ɪᴛs ɴᴏᴛ ᴛʜᴇ ʙᴇsᴛ,
                   ᴛʜᴇʀᴇ ᴡɪʟʟ ʙᴇ ᴇʀʀᴏʀs. 
"""

# Set up logging to file only
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('log.txt', mode='a')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger = logging.getLogger()
logger.handlers = [file_handler]

# Initialize Rich console
console = Console()

# Clear console based on OS
def clear_console():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# Create results directories
os.makedirs("results/Service", exist_ok=True)
os.makedirs("results/Account Name", exist_ok=True)

# Load errors.txt
def load_errors():
    errors = {}
    errors_file = "errors.txt"
    if os.path.exists(errors_file):
        with open(errors_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if ':' in line:
                    code, info = [part.strip() for part in line.split(':', 1)]
                    try:
                        errors[int(code)] = info
                    except ValueError:
                        logging.error(f"Invalid error code in {errors_file}: {code}")
    return errors

# Save error to errors.txt
def save_error(code, info):
    errors_file = "errors.txt"
    errors = load_errors()
    if code != 200:
        errors[int(code)] = info
        with filelock.FileLock(f"{errors_file}.lock"):
            with open(errors_file, 'w', encoding='utf-8') as f:
                for code, info in sorted(errors.items()):
                    f.write(f"{code}:{info}\n")

# Parse .claim file
def parse_claim_file(file_path):
    checker = {
        'title': '',
        'url': '',
        'url_user': '',
        'results': {}
    }
    current_result = None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if ':' not in line:
                    logging.warning(f"Skipping invalid line {line_number} in {file_path}: Missing colon")
                    continue
                
                key, value = [part.strip() for part in line.split(':', 1)]
                key = key.lower()
                
                if key == 'checker title':
                    checker['title'] = value
                elif key == 'url':
                    checker['url'] = value
                elif key == 'url_user':
                    checker['url_user'] = value
                elif key == 'result.name':
                    current_result = value
                    checker['results'][current_result] = {
                        'must_have': [],
                        'if_have': [],
                        'cant_have': [],
                        'if_redirects': None,
                        'codes': []
                    }
                elif current_result:
                    if key == 'must_have':
                        checker['results'][current_result]['must_have'].append(value)
                    elif key == 'if_have':
                        checker['results'][current_result]['if_have'].append(value)
                    elif key == 'cant_have':
                        checker['results'][current_result]['cant_have'].append(value)
                    elif key == 'if_redirects':
                        checker['results'][current_result]['if_redirects'] = value.lower() == 'true'
                    elif key == 'code':
                        try:
                            checker['results'][current_result]['codes'].append(int(value))
                        except ValueError:
                            logging.error(f"Invalid code at line {line_number} in {file_path}: {value}")
        if not checker['url_user']:
            logging.error(f"Invalid checker {file_path}: Missing url_user")
            return None
        return checker
    except Exception as e:
        logging.error(f"Error parsing {file_path} at line {line_number}: {e}")
        return None

# Load checkers from Configs/
def load_checkers():
    checkers = {}
    configs_dir = "Configs"
    if not os.path.exists(configs_dir):
        logging.error(f"Configs directory not found: {configs_dir}")
        return checkers
    
    logging.info(f"Scanning {configs_dir} for checkers")
    for filename in os.listdir(configs_dir):
        service_name = filename.rsplit('.', 1)[0].lower()
        file_path = os.path.join(configs_dir, filename)
        
        if filename.endswith(".claim"):
            if service_name in checkers:
                logging.warning(f"Skipping {filename}, {service_name} already loaded")
                continue
            checker = parse_claim_file(file_path)
            if checker:
                checkers[service_name] = {'type': 'claim', 'config': checker}
                logging.info(f"Loaded checker: {service_name}")
            else:
                logging.warning(f"Skipping invalid checker: {file_path}")
                continue
        
        elif filename.endswith(".py") and filename != "__init__.py":
            if service_name in checkers:
                logging.warning(f"Skipping {filename}, {service_name} already loaded")
                continue
            try:
                spec = importlib.util.spec_from_file_location(service_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, 'validate_username') and hasattr(module, 'check_availability'):
                    checkers[service_name] = {
                        'type': 'py',
                        'validate': module.validate_username,
                        'check': module.check_availability
                    }
                    logging.info(f"Loaded checker: {service_name}")
                else:
                    logging.error(f"Checker {service_name} missing validate_username or check_availability")
            except Exception as e:
                logging.error(f"Failed to load checker {service_name}: {e}")
    
    return checkers

def update_service_file(service, username, result_name, details, error_code=None):
    service_dir = f"results/Service/{service}"
    os.makedirs(service_dir, exist_ok=True)
    service_file = f"{service_dir}/{service}.txt"
    errors = load_errors()
    
    # Create username entry
    if result_name == "Error" and error_code is not None:
        if error_code in errors:
            username_entry = f"{username} ({error_code}:{errors[error_code]})"
        else:
            username_entry = f"{username} ({error_code})"
    else:
        username_entry = f"{username} ({details})"
    
    # Thread-safe append to file
    with filelock.FileLock(f"{service_file}.lock"):
        sections = {}
        if os.path.exists(service_file):
            with open(service_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                current_section = None
                for line in lines:
                    line = line.strip()
                    if line.endswith(":"):
                        current_section = line[:-1]
                        sections[current_section] = []
                    elif line and current_section:
                        sections[current_section].append(line)
        
        section_key = f"{service} {result_name}"
        if section_key not in sections:
            sections[section_key] = []
        
        # Remove existing entry for this username
        for key in sections:
            sections[key] = [entry for entry in sections[key] if not entry.startswith(f"{username} (")]
        
        # Add new entry
        sections[section_key].append(username_entry)
        logging.info(f"Added {username_entry} to {section_key}")
        
        # Write updated sections
        with open(service_file, 'w', encoding='utf-8') as f:
            for key in sorted(sections.keys()):
                if sections[key]:
                    f.write(f"{key}:\n")
                    for uname in sorted(sections[key]):
                        f.write(f"{uname}\n")
                    f.write("\n")
    
    logging.info(f"Updated {service_file} for {username}")

def update_account_file(username, service, result_name, details, error_code=None):
    account_dir = "results/Account Name"
    os.makedirs(account_dir, exist_ok=True)
    account_file = f"{account_dir}/{username}.txt"
    errors = load_errors()
    
    # Create entry
    if result_name == "Error" and error_code is not None:
        if error_code in errors:
            entry = f"{service} ({error_code}:{errors[error_code]})"
        else:
            entry = f"{service} ({error_code})"
    else:
        entry = f"{service} ({details})"
    
    # Thread-safe update
    with filelock.FileLock(f"{account_file}.lock"):
        sections = {}
        if os.path.exists(account_file):
            with open(account_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                current_section = None
                for line in lines:
                    line = line.strip()
                    if line.endswith(':') and not line.startswith('username:'):
                        current_section = line[:-1]
                        sections[current_section] = []
                    elif line and current_section and not line.startswith('username:'):
                        sections[current_section].append(line)
        
        # Initialize section if not present
        if result_name not in sections:
            sections[result_name] = []
        
        # Remove existing entry for this service
        sections[result_name] = [e for e in sections[result_name] if not e.startswith(f"{service} (")]
        
        # Add new entry
        sections[result_name].append(entry)
        logging.info(f"Added {entry} to {account_file}")
        
        # Write updated file
        with open(account_file, 'w', encoding='utf-8') as f:
            f.write(f"username: {username}\n\n")
            for key in sorted(sections.keys()):
                if sections[key]:
                    f.write(f"{key}:\n")
                    for service_entry in sorted(sections[key]):
                        f.write(f"{service_entry}\n")
                    f.write("\n")

def load_usernames():
    default_file = "usernames.txt"
    if os.path.exists(default_file):
        with open(default_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    
    console.print("[red]usernames.txt not found.[/red]")
    file_path = console.input("[bold green]Enter path to username file (or press Enter to exit): [/bold green]").strip()
    if not file_path:
        return []
    if not os.path.exists(file_path):
        console.print("[red]File not found.[/red]")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def check_username(username, checkers, progress, task_id, stats):
    results = {}
    invalid_services = []
    valid_services = []
    errors = load_errors()

    logging.info(f"Validating username {username} for {len(checkers)} services")
    # Validate username for checkers
    for service, checker in checkers.items():
        logging.info(f"Checking validation for {service}")
        if checker['type'] == 'py':
            try:
                is_valid, error_msg = checker['validate'](username)
                if not is_valid:
                    invalid_services.append((service, error_msg))
                    logging.info(f"Invalid username {username} for {service}: {error_msg}")
                else:
                    valid_services.append(service)
                    logging.info(f"Valid username {username} for {service}")
            except Exception as e:
                invalid_services.append((service, f"Validation error: {e}"))
                logging.error(f"Validation error for {service} with username {username}: {e}")
        else:
            # For .claim checkers, validate URL compatibility
            try:
                checker['config']['url_user'].format(USERNAME=username)
                valid_services.append(service)
                logging.info(f"Valid username {username} for {service} (URL format OK)")
            except Exception as e:
                invalid_services.append((service, f"Invalid URL format: {e}"))
                logging.error(f"Validation error for {service} with username {username}: {e}")

    total_services = len(valid_services)
    logging.info(f"Valid services for {username}: {valid_services}")
    if not valid_services:
        logging.warning(f"No valid services for {username}, skipping checks")
        with stats['lock']:
            stats['results'][username] = (results, invalid_services)
        progress.update(task_id, completed=total_services)
        progress.remove_task(task_id)
        return

    # Check each service
    for i, service in enumerate(valid_services):
        progress.update(task_id, description=f"Checking {username} On {service.capitalize()}")
        checker = checkers[service]
        logging.info(f"Checking {service} for username {username}")
        try:
            if checker['type'] == 'py':
                # Handle .py checker
                available, details = checker['check'](username)
                result_name = "Available" if available else "Taken" if details.startswith("Taken") else "Error"
                if details == "Rate Limited":
                    result_name = "Rate_Limit"
                error_code = None
                matched_conditions = [f"Details: {details}"]
                if result_name == "Error":
                    # Extract error code if possible
                    match = re.search(r'Error (\d+)', details)
                    if match:
                        error_code = int(match.group(1))
                        if error_code not in errors and error_code != 200:
                            save_error(error_code, "Unknown")
            else:
                # Handle .claim checker
                url = checker['config']['url_user'].format(USERNAME=username)
                response = requests.get(url, timeout=10, allow_redirects=True)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                redirected = response.url != url
                
                result_name = "Error"
                details = "No matching conditions"
                error_code = None
                matched_conditions = []
                failure_reasons = []
                
                for name, rules in checker['config']['results'].items():
                    matches = True
                    current_failures = []
                    
                    if rules['codes']:
                        if response.status_code not in rules['codes']:
                            matches = False
                            current_failures.append(f"Code {response.status_code} not in {rules['codes']}")
                        else:
                            matched_conditions.append(f"Code: {response.status_code}")
                    
                    for text in rules['must_have']:
                        if not soup.find(lambda tag: tag.name == 'div' and text.lower() in tag.text.lower()):
                            matches = False
                            current_failures.append(f"Must Have missing: {text}")
                        else:
                            matched_conditions.append(f"Must Have: {text}")
                    
                    for text in rules['if_have']:
                        if text.lower() not in response.text.lower():
                            matches = False
                            current_failures.append(f"If Have missing: {text}")
                        else:
                            matched_conditions.append(f"If Have: {text}")
                    
                    for text in rules['cant_have']:
                        if text.lower() in response.text.lower():
                            matches = False
                            current_failures.append(f"Cant Have present: {text}")
                        else:
                            matched_conditions.append(f"Cant Have (absent): {text}")
                    
                    if rules['if_redirects'] is not None:
                        if rules['if_redirects'] != redirected:
                            matches = False
                            current_failures.append(f"Redirect {redirected} does not match {rules['if_redirects']}")
                        else:
                            matched_conditions.append(f"Redirect: {redirected}")
                    
                    if matches:
                        result_name = name
                        details = name
                        if name == "Error":
                            error_code = response.status_code
                        break
                    else:
                        failure_reasons.append(f"Failed {name}: {', '.join(current_failures)}")
                
                if result_name == "Error" and error_code is None:
                    error_code = response.status_code
                    if error_code in errors:
                        details = f"{error_code}:{errors[error_code]}"
                        matched_conditions.append(f"Error Code: {error_code} ({errors[error_code]})")
                    else:
                        details = f"{error_code}"
                        matched_conditions.append(f"Error Code: {error_code}")
                    
                    if error_code not in errors and error_code != 200:
                        save_error(error_code, "Unknown")
                
                # Log conditions and failures
                if matched_conditions:
                    logging.info(f"Username {username} on {service}: Matched {result_name}: {'; '.join(matched_conditions)}")
                if failure_reasons:
                    logging.info(f"Username {username} on {service}: {'; '.join(failure_reasons)}")
            
            # Store and write result
            results[service] = (result_name, details, error_code, matched_conditions)
            with stats['lock']:
                if result_name.lower() not in stats['counts']:
                    stats['counts'][result_name.lower()] = {}
                stats['counts'][result_name.lower()][username] = stats['counts'][result_name.lower()].get(username, 0) + 1
            
            update_service_file(service, username, result_name, details, error_code)
            update_account_file(username, service, result_name, details, error_code)
        
        except Exception as e:
            result_name = "Error"
            details = f"Exception: {str(e)}"
            error_code = None
            matched_conditions = [f"Exception: {str(e)}"]
            results[service] = (result_name, details, error_code, matched_conditions)
            with stats['lock']:
                if 'error' not in stats['counts']:
                    stats['counts']['error'] = {}
                stats['counts']['error'][username] = stats['counts']['error'].get(username, 0) + 1
            logging.error(f"Check error for {service} with username {username}: {e}")
            
            update_service_file(service, username, result_name, details, error_code)
            update_account_file(username, service, result_name, details, error_code)
        
        progress.update(
            task_id,
            advance=1,
            **{k.lower(): stats['counts'].get(k.lower(), {}).get(username, 0) for k in checker['config']['results'].keys()} if checker['type'] == 'claim' else {
                'available': stats['counts'].get('available', {}).get(username, 0),
                'taken': stats['counts'].get('taken', {}).get(username, 0),
                'error': stats['counts'].get('error', {}).get(username, 0),
                'rate_limit': stats['counts'].get('rate_limit', {}).get(username, 0)
            }
        )
        time.sleep(2)

    with stats['lock']:
        stats['results'][username] = (results, invalid_services)
    progress.update(task_id, completed=total_services)
    progress.remove_task(task_id)

def main():
    # Load checkers
    checkers = load_checkers()
    
    if not checkers:
        clear_console()
        console.print("[red]No checkers loaded. Add files to Configs/ directory.[/red]")
        console.input("[yellow]Press Enter to exit...[/yellow]")
        return

    while True:
        clear_console()
        console.print("[cyan]{}[/cyan]".format(ASCII_ART.strip()))
        console.print("[green]Modules:[/green]")
        for service in sorted(checkers.keys()):
            console.print(f"[white]{service.capitalize()}[/white]")
        console.print()

        # Prompt for threads
        thread_input = console.input("[bold green]Enter number of threads (1-100, default 1): [/bold green]").strip()
        try:
            max_threads = int(thread_input) if thread_input else 1
            max_threads = min(max(1, max_threads), 100)
        except ValueError:
            max_threads = 1
            console.print("[yellow]Invalid input, using 1 thread.[/yellow]")

        # Load usernames
        usernames = load_usernames()
        if not usernames:
            console.print("[yellow]No usernames to check. Exiting.[/yellow]")
            console.input("[yellow]Press Enter to continue...[/yellow]")
            continue

        # Initialize stats with dynamic counts
        stats = {
            'results': {},
            'lock': threading.Lock(),
            'counts': {}
        }

        # Set up Rich progress with dynamic fields
        all_result_names = set()
        for checker in checkers.values():
            if checker['type'] == 'claim':
                all_result_names.update(checker['config']['results'].keys())
            else:
                all_result_names.update(['Available', 'Taken', 'Error', 'Rate_Limit'])
        
        progress_fields = {name.lower(): 0 for name in all_result_names}
        progress_columns = [
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("--")
        ]
        for name in sorted(all_result_names):
            color = {
                'Available': 'green',
                'Taken': 'red',
                'Error': 'purple',
                'Rate_Limit': 'yellow'
            }.get(name, 'cyan')
            progress_columns.append(TextColumn(f"[{color}]{name} {{task.fields[{name.lower()}]}}[/{color}]"))
        
        with Progress(*progress_columns, console=console) as progress:
            # Process usernames in batches
            for i in range(0, len(usernames), max_threads):
                batch = usernames[i:i + max_threads]
                tasks = {}
                for username in batch:
                    tasks[username] = progress.add_task(
                        f"Checking {username} On Initializing",
                        total=0,
                        **progress_fields
                    )

                # Check batch concurrently
                with ThreadPoolExecutor(max_workers=max_threads) as executor:
                    futures = []
                    for username in batch:
                        valid_services = []
                        for service, checker in checkers.items():
                            if checker['type'] == 'py':
                                try:
                                    is_valid, _ = checker['validate'](username)
                                    if is_valid:
                                        valid_services.append(service)
                                except Exception as e:
                                    logging.error(f"Exception in .py validation for {service}, {username}: {e}")
                            else:
                                try:
                                    checker['config']['url_user'].format(USERNAME=username)
                                    valid_services.append(service)
                                except Exception as e:
                                    logging.error(f"Exception in .claim validation for {service}, {username}: {e}")
                        progress.update(tasks[username], total=len(valid_services))
                        futures.append(
                            executor.submit(check_username, username, checkers, progress, tasks[username], stats)
                        )
                    for future in futures:
                        try:
                            future.result(timeout=60)
                        except Exception as e:
                            logging.error(f"Thread error: {e}")

        # Display results
        clear_console()
        console.print("[cyan]{}[/cyan]".format(ASCII_ART.strip()))
        console.print("[bold white]Final Results[/bold white]")
        console.print()
        errors = load_errors()

        for username in usernames:
            results, invalid_services = stats['results'].get(username, ({}, []))
            console.print(f"[bold white]Username: {username}[/bold white]")

            if invalid_services:
                console.print("[red]Invalid username for the following services:[/red]")
                invalid_table = Table()
                invalid_table.add_column("Service", style="cyan")
                invalid_table.add_column("Reason", style="red")
                for service, reason in invalid_services:
                    invalid_table.add_row(service, reason)
                console.print(invalid_table)
                console.print()

            table = Table(title="Availability Results")
            table.add_column("Service", style="white")
            table.add_column("Status", style="white")
            table.add_column("Details", style="white")
            if results:
                for service in sorted(results.keys()):
                    result_name, details, error_code, _ = results[service]
                    color = {
                        "Available": "green",
                        "Taken": "red",
                        "Error": "purple",
                        "Rate_Limit": "yellow",
                        "Suspended": "magenta"
                    }.get(result_name, "cyan")
                    service_style = "green" if result_name == "Available" else "red"
                    
                    table.add_row(
                        service,
                        f"[{color}]{result_name}[/{color}]",
                        f"[{color}]{details}[/{color}]",
                        style=f"{service_style} on black"
                    )
            else:
                table.add_row("None", "[purple]No results[/purple]", "[purple]No services checked[/purple]")
            console.print(table)
            console.print()

        console.input("[yellow]Press Enter to continue...[/yellow]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("[yellow]Stopped by user[/yellow]")