# curl_parser.py - Simplified and user-friendly version
import re
import os
from urllib.parse import parse_qs, unquote

def parse_curl_command(filepath=None) -> dict | None:
    """
    Reads and parses a cURL command to extract authentication components.
    """
    if filepath is None:
        # 使用相对于当前脚本文件的路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        secrets_dir = os.path.join(script_dir, "..", "secrets")
        filepath = os.path.join(secrets_dir, "curl_command.txt")
        filepath = os.path.normpath(filepath)  # 规范化路径
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            curl_string = f.read().replace('\\\n', ' ').strip()
    except FileNotFoundError:
        print(f"\n❌ Error: Could not find '{filepath}'.")
        print("\n📋 QUICK SETUP REQUIRED:")
        print("1. Open NotebookLM in your browser and log in")
        print("2. Press F12 to open Developer Tools")
        print("3. Go to the 'Network' tab")
        print("4. Reload the page (Ctrl+R)")
        print("5. Look for a request to 'notebook/model'")
        print("6. Right-click it → Copy → Copy as cURL")
        print("7. Create a file called 'dev/secrets/curl_command.txt' and paste the command there")
        print(f"8. Run this script again")
        return None

    # Extract URL
    url_match = re.search(r"curl ['\"]([^'\"]+)['\"]", curl_string)
    if not url_match:
        print("❌ Error: Could not find URL in cURL command.")
        return None
    url = url_match.group(1)

    # Extract Headers
    headers_matches = re.findall(r"-H ['\"]([^'\"]+)['\"]", curl_string)
    headers = {}
    for h in headers_matches:
        if ':' in h:
            key, value = h.split(':', 1)
            headers[key.strip()] = value.strip()

    # Extract Cookie
    cookie_match = re.search(r"--cookie ['\"]([^'\"]+)['\"]", curl_string) or re.search(r"-b ['\"]([^'\"]+)['\"]", curl_string)
    cookie = cookie_match.group(1) if cookie_match else ""
    
    # Extract Data and parse payload
    data_raw_match = re.search(r"--data-raw ['\"]([^'\"]+)['\"]", curl_string)
    if not data_raw_match:
        print("❌ Error: Could not find payload (--data-raw) in cURL command.")
        print("💡 Make sure you copied the request that contains notebook data.")
        return None
    
    data_raw_string = data_raw_match.group(1)
    parsed_payload = parse_qs(data_raw_string)
    
    f_req = unquote(parsed_payload.get('f.req', [''])[0])
    at_token = unquote(parsed_payload.get('at', [''])[0])

    if not all([url, headers, cookie, f_req, at_token]):
        print("❌ Error: Could not extract sufficient information from cURL command.")
        print("💡 Please ensure you copied the correct network request.")
        return None

    print("✅ Successfully parsed cURL command!")
    return {
        "url": url,
        "headers": headers,
        "cookie": cookie,
        "list_payload": {
            'f.req': f_req,
            'at': at_token
        }
    } 