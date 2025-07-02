# tests/test_client.py

import unittest
from unittest.mock import patch, MagicMock
from src.client import NotebookLMClient


class TestNotebookLMClient(unittest.TestCase):

    def setUp(self):
        """
        Hàm này chạy trước mỗi bài test.
        Chúng ta tạo một curl_data mẫu để sử dụng.
        """
        self.mock_curl_data = {
            "url": "https://notebooklm.google.com/api?rpcids=wXbhsf&_reqid=101",
            "headers": {"user-agent": "test-agent"},
            "cookie": "SID=test-cookie",
            "list_payload": {
                "f.req": '[[["wXbhsf","[null,1,null,[2]]",null,"generic"]]]',
                "at": "TEST_AT_TOKEN:123456",
            },
        }
        # Khởi tạo client với dữ liệu mẫu
        self.client = NotebookLMClient(self.mock_curl_data)

    @patch("src.client.requests.Session.post")
    def test_get_all_notebooks_success(self, mock_post: MagicMock):
        """
        Kiểm tra trường hợp lấy danh sách notebooks thành công.
        `@patch` sẽ thay thế `requests.Session.post` bằng một "diễn viên đóng thế" (mock_post).
        """
        # 1. Arrange: Cấu hình "diễn viên đóng thế"
        # Giả lập một response thành công từ server
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Response chứa notebook A và B"
        mock_post.return_value = (
            mock_response  # Khi được gọi, mock_post sẽ trả về response này
        )

        # 2. Act: Gọi hàm cần kiểm thử
        response_text = self.client.get_all_notebooks()

        # 3. Assert: Khẳng định kết quả
        # Kiểm tra xem hàm có trả về đúng text không
        self.assertEqual(response_text, "Response chứa notebook A và B")

        # Kiểm tra xem `session.post` có được gọi đúng 1 lần với đúng các tham số không
        mock_post.assert_called_once_with(
            self.mock_curl_data["url"],
            data=self.mock_curl_data["list_payload"],
            timeout=30,
        )

    @patch("src.client.requests.Session.post")
    def test_delete_notebook_failure_400(self, mock_post: MagicMock):
        """
        Kiểm tra trường hợp xóa notebook thất bại với lỗi 400.
        """
        # 1. Arrange: Cấu hình "diễn viên đóng thế"
        # Giả lập một response lỗi 400 từ server
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Error: Invalid f.req parameter"
        mock_post.return_value = mock_response

        # 2. Act: Gọi hàm cần kiểm thử
        notebook_id_to_delete = "test-id-123"
        success, message = self.client.delete_notebook(notebook_id_to_delete)

        # 3. Assert: Khẳng định kết quả
        # Kiểm tra xem hàm có trả về đúng trạng thái thất bại và thông báo lỗi không
        self.assertFalse(success)
        self.assertIn("Status: 400", message)
        self.assertIn("Invalid f.req", message)

        # Kiểm tra xem `session.post` có được gọi với đúng payload xóa không
        expected_delete_url = "https://notebooklm.google.com/api?rpcids=WWINqb&_reqid=102"
        expected_payload = {
            "f.req": r'[[["WWINqb","[[\"test-id-123\"],[2]]",null,"generic"]]]',
            "at": "TEST_AT_TOKEN:123456",
        }
        mock_post.assert_called_once_with(expected_delete_url, data=expected_payload)


if __name__ == "__main__":
    unittest.main()
