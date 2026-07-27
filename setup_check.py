"""
CivicMind AI — Environment Validator & Setup Helper
Run this script before starting the application to verify your environment.

Usage:
    python setup_check.py
"""

import sys
import os
import importlib

# ── ANSI colours ─────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


def ok(msg):  print(f"  [OK]   {msg}")
def fail(msg): print(f"  [FAIL] {msg}")
def warn(msg): print(f"  [WARN] {msg}")
def info(msg): print(f"  [-->]  {msg}")


def check_python():
    print(f"\n{BOLD}Python Version{RESET}")
    major, minor = sys.version_info[:2]
    if (major, minor) >= (3, 10):
        ok(f"Python {major}.{minor} — compatible")
    else:
        fail(f"Python {major}.{minor} — CivicMind AI requires Python 3.10+")
        sys.exit(1)


def check_env():
    print(f"\n{BOLD}Environment Variables{RESET}")
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if api_key and api_key != "your_gemini_api_key_here":
        ok("GEMINI_API_KEY is set")
    else:
        fail("GEMINI_API_KEY is not set — AI features will not work")
        info("Get a free key at https://aistudio.google.com")
        info("Add it to .env: GEMINI_API_KEY=your_key_here")

    for var, default in [("GEMINI_MODEL", "gemini-2.5-flash"), ("LOG_LEVEL", "INFO")]:
        val = os.environ.get(var, default)
        ok(f"{var} = {val}")

    waqi = os.environ.get("WAQI_TOKEN", "demo")
    if waqi == "demo":
        warn("WAQI_TOKEN uses 'demo' — AQI data may be rate-limited")
    else:
        ok("WAQI_TOKEN is set")


def check_packages():
    print(f"\n{BOLD}Required Packages{RESET}")
    required = {
        "streamlit": "streamlit",
        "fastapi": "fastapi",
        "pandas": "pandas",
        "plotly": "plotly",
        "folium": "folium",
        "httpx": "httpx",
        "google.genai": "google-genai",
        "pydantic": "pydantic",
        "dotenv": "python-dotenv",
    }
    all_ok = True
    for import_name, package_name in required.items():
        try:
            importlib.import_module(import_name)
            ok(f"{package_name}")
        except ImportError:
            fail(f"{package_name} — not installed")
            all_ok = False
    if not all_ok:
        info("Run: pip install -r requirements.txt")


def check_datasets():
    print(f"\n{BOLD}Datasets{RESET}")
    datasets_dir = "datasets"
    if os.path.isdir(datasets_dir):
        files = [f for f in os.listdir(datasets_dir) if f.endswith(".csv")]
        if files:
            ok(f"{len(files)} CSV dataset(s) found in datasets/")
        else:
            warn("No CSV datasets found in datasets/ — some features may show fallback data")
    else:
        fail("datasets/ directory not found")


def check_dotenv():
    print(f"\n{BOLD}.env File{RESET}")
    if os.path.isfile(".env"):
        ok(".env file found — loading environment variables")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            ok("Variables loaded from .env")
        except ImportError:
            warn("python-dotenv not installed — .env will not be loaded")
    elif os.path.isfile(".env.example"):
        warn(".env not found — copy .env.example and add your GEMINI_API_KEY")
        info("Run: cp .env.example .env")
    else:
        warn(".env and .env.example not found")


def summary():
    print(f"\n{BOLD}{'-'*55}{RESET}")
    print(f"  {GREEN}{BOLD}Setup check complete.{RESET}")
    print(f"\n  Start the app:")
    print(f"  {CYAN}streamlit run frontend/app.py{RESET}")
    print(f"\n  Or with backend:")
    print(f"  {CYAN}uvicorn backend.main:app --reload  # Terminal 1{RESET}")
    print(f"  {CYAN}streamlit run frontend/app.py       # Terminal 2{RESET}")
    print(f"{BOLD}{'-'*55}{RESET}\n")


if __name__ == "__main__":
    print(f"\n{BOLD}{CYAN}CivicMind AI - Environment Setup Checker{RESET}")
    print("-" * 55)

    # Load .env first so subsequent checks can read variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    check_python()
    check_dotenv()
    check_env()
    check_packages()
    check_datasets()
    summary()
