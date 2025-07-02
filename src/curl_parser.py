# curl_parser.py
import re
from urllib.parse import parse_qs, unquote

def parse_curl_command(filepath="curl_command.txt") -> dict | None:
    """
    Đọc và phân tích một lệnh cURL từ file để trích xuất các thành phần.
    """
    try:
        with open(filepath, 'r') as f:
            curl_string = f.read().replace('\\\n', ' ').strip()
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file '{filepath}'.")
        print("Vui lòng tạo file này và dán lệnh cURL vào đó.")
        return None

    # Trích xuất URL
    url_match = re.search(r"curl '(.*?)'", curl_string)
    if not url_match:
        print("Lỗi: Không thể tìm thấy URL trong lệnh cURL.")
        return None
    url = url_match.group(1)

    # Trích xuất Headers
    headers_matches = re.findall(r"-H '(.*?)'", curl_string)
    headers = {key.strip(): value.strip() for key, value in (h.split(':', 1) for h in headers_matches)}

    # Trích xuất Cookie
    cookie_match = re.search(r"--cookie '(.*?)'", curl_string) or re.search(r"-b '(.*?)'", curl_string)
    cookie = cookie_match.group(1) if cookie_match else ""
    
    # Trích xuất Data Raw và phân tích nó
    data_raw_match = re.search(r"--data-raw '(.*?)'", curl_string)
    if not data_raw_match:
        print("Lỗi: Không thể tìm thấy payload (--data-raw) trong lệnh cURL.")
        return None
    
    data_raw_string = data_raw_match.group(1)
    # Phân tích chuỗi query của payload để lấy ra 'f.req' và 'at'
    parsed_payload = parse_qs(data_raw_string)
    
    # Lấy giá trị, unquote nếu cần, và lấy phần tử đầu tiên vì parse_qs trả về list
    f_req = unquote(parsed_payload.get('f.req', [''])[0])
    at_token = unquote(parsed_payload.get('at', [''])[0])

    if not all([url, headers, cookie, f_req, at_token]):
        print("Lỗi: Không thể trích xuất đủ thông tin từ lệnh cURL.")
        return None

    return {
        "url": url,
        "headers": headers,
        "cookie": cookie,
        "list_payload": {
            'f.req': f_req,
            'at': at_token
        }
    }