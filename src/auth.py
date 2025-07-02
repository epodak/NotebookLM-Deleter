import json
from pathlib import Path
from playwright.sync_api import sync_playwright
import time

# --- Constants ---
# The script will create and manage its own browser profile in this directory.
# No more manual configuration is needed.
PROFILE_DIR = Path("./script_browser_profile")
AUTH_CONFIG_PATH = Path("auth_config.json")
TARGET_API_URL = "https://notebooklm.google.com/notebook/model"
LOGIN_URL = "https://notebooklm.google.com/"


def get_auth_from_browser() -> dict | None:
    """
    Launches a browser with a dedicated, persistent profile for this script.
    The user only needs to log in once. Subsequent runs will reuse the session.
    """
    with sync_playwright() as p:
        print("Launching dedicated browser for one-time login...")
        
        # We use a persistent context in a local directory.
        # This creates a self-contained browser profile for our script.
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            # Explicitly use chrome_proxy.exe as requested by the user, which can be more stable for automation.
            executable_path="C:/Program Files/Google/Chrome/Application/chrome_proxy.exe",
        )
        page = context.new_page()

        captured_headers = {}

        def handle_request(request):
            """Checks requests for the target API and captures auth headers."""
            if TARGET_API_URL in request.url:
                print(f"✅ Target API call detected: {request.url}")
                headers = request.headers
                
                auth = headers.get('authorization')
                if auth:
                    captured_headers['authorization'] = auth
                    
                    # Also grab the cookie from the full browser context
                    all_cookies = context.cookies()
                    cookie_string = "; ".join([f"{c['name']}={c['value']}" for c in all_cookies])
                    captured_headers['cookie'] = cookie_string

                    print("✅ Successfully captured authentication tokens!")

        page.on("request", handle_request)

        print("\n--- ONE-TIME SETUP: ACTION REQUIRED ---")
        print("A dedicated browser window has opened.")
        print("Please log in to your Google account in THAT browser window.")
        print("Once you have successfully logged into NotebookLM, you can close the browser window.")
        print("This script will wait in the background and save your credentials automatically.")
        
        try:
            page.goto(LOGIN_URL, timeout=30000) # 30s timeout, user can navigate manually anyway

            timeout_ms = 180000  # 3 minutes
            start_time = time.time()
            while not captured_headers:
                page.wait_for_timeout(500)
                if not context.pages:
                    print("Browser closed by user.")
                    break
                if (time.time() - start_time) * 1000 > timeout_ms:
                    print("Timeout reached while waiting for login.")
                    break
        
        except Exception as e:
            print(f"An error occurred during browser automation: {e}")
            return None
        
        finally:
            context.close()

        if captured_headers:
            save_auth_config(captured_headers)
            return captured_headers
        else:
            print("Could not capture credentials. Please ensure you logged in correctly and try again.")
            return None

def save_auth_config(config: dict):
    """Saves the authentication config to a JSON file."""
    print(f"Saving authentication configuration to {AUTH_CONFIG_PATH}...")
    with open(AUTH_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    print("Configuration saved.")

def load_auth_config() -> dict | None:
    """Loads the authentication config from a JSON file."""
    if not AUTH_CONFIG_PATH.exists():
        return None
    try:
        with open(AUTH_CONFIG_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not read or parse {AUTH_CONFIG_PATH}. Error: {e}")
        return None 