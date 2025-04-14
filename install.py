import subprocess
import sys
import importlib
import os

REQUIRED_PACKAGES = [
    "rich",
    "requests",
    "beautifulsoup4",
    "filelock"
]

PYTHON_COMMANDS = ["python", "python3"]

def install_package(package):
    for py_cmd in PYTHON_COMMANDS:
        try:
            subprocess.check_call([py_cmd, "-m", "pip", "install", package])
            return True
        except subprocess.CalledProcessError:
            continue
    print(f"❌ Failed to install {package}")
    return False

def is_installed(pkg):
    try:
        importlib.import_module(pkg)
        return True
    except ImportError:
        return False

def main():
    print("🔍 Checking and installing required packages...\n")
    for pkg in REQUIRED_PACKAGES:
        name = pkg.split("==")[0]
        if not is_installed(name):
            print(f"📦 Installing: {pkg}")
            success = install_package(pkg)
            if not success:
                print(f"❌ Could not install {pkg}. Please install it manually.")
                return
        else:
            print(f"✅ Already installed: {pkg}")

    print("\n🚀 Launching main.py...\n")
    os.system(f"{PYTHON_COMMANDS[0]} main.py")

if __name__ == "__main__":
    main()
