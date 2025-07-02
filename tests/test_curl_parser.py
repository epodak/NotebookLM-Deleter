# tests/test_curl_parser.py

import unittest
from urllib.parse import urlparse, parse_qs
# Sửa lỗi import ở đây!
from src.curl_parser import parse_curl_command 

class TestCurlParser(unittest.TestCase):
    """
    Bộ kiểm thử cho module curl_parser.
    """
    
    def test_successful_parsing(self):
        """
        Kiểm tra trường hợp phân tích thành công với dữ liệu mẫu.
        """
        # 1. Arrange: Đường dẫn đến file test nằm trong thư mục con 'data'
        test_file_path = "tests/data/test_curl_command.txt"
        
        # 2. Act: Gọi hàm cần kiểm thử
        parsed_data = parse_curl_command(filepath=test_file_path)
        
        # 3. Assert: Khẳng định kết quả đúng như mong đợi
        
        # --- Kiểm tra sự tồn tại và kiểu dữ liệu cơ bản ---
        self.assertIsNotNone(parsed_data, "Hàm parse không nên trả về None với file hợp lệ.")
        self.assertIsInstance(parsed_data, dict, "Kết quả trả về phải là một dictionary.")
        
        # --- Kiểm tra các key chính ---
        assert parsed_data is not None # type narrowing for pylance
        self.assertIn("url", parsed_data)
        self.assertIn("headers", parsed_data)
        self.assertIn("cookie", parsed_data)
        self.assertIn("list_payload", parsed_data)
        
        # --- Kiểm tra kiểu dữ liệu của các giá trị ---
        self.assertIsInstance(parsed_data['url'], str)
        self.assertIsInstance(parsed_data['headers'], dict)
        self.assertIsInstance(parsed_data['cookie'], str)
        self.assertIsInstance(parsed_data['list_payload'], dict)
        
        # --- Kiểm tra nội dung cụ thể ---
        
        # Kiểm tra URL có chứa đúng rpcids không
        parsed_url = urlparse(parsed_data['url'])
        query_params = parse_qs(parsed_url.query)
        self.assertIn('rpcids', query_params, "URL phải chứa tham số 'rpcids'.")
        self.assertEqual(query_params['rpcids'][0], 'wXbhsf', "rpcids phải là 'wXbhsf' cho lệnh lấy danh sách.")
        
        # Kiểm tra cookie có được trích xuất đúng không
        self.assertTrue(parsed_data['cookie'].startswith('SID=g.'))

        # Kiểm tra một header bất kỳ
        self.assertEqual(parsed_data['headers']['user-agent'], 'My Agent')
        
        # Kiểm tra payload đã được phân tích đúng chưa
        payload = parsed_data['list_payload']
        self.assertIn('f.req', payload)
        self.assertIn('at', payload)
        self.assertEqual(payload['at'], 'DEADbeebfCHzvYjqLDRiJgBRg7xU:1231017994689')
        self.assertTrue(payload['f.req'].startswith('[[["wXbhsf"'))

    def test_file_not_found(self):
        """
        Kiểm tra trường hợp file không tồn tại.
        """
        parsed_data = parse_curl_command(filepath="file_khong_ton_tai.txt")
        self.assertIsNone(parsed_data, "Hàm phải trả về None khi file không tồn tại.")

if __name__ == '__main__':
    unittest.main()