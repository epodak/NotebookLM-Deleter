# src/client.py

import requests
import time
import re
from urllib.parse import urlparse, urlunparse, urlencode
from requests_toolbelt.utils import dump  # Optional, để in ra cURL


class NotebookLMClient:
    """
    Một client để tương tác với API ẩn của Google NotebookLM.
    """

    def __init__(self, curl_data: dict):
        self.curl_data = curl_data
        self.session = self._create_session()
        self._reqid = self._extract_reqid()

    # --- Context Manager Methods ---
    def __enter__(self):
        """Được gọi khi vào khối `with`."""
        return self  # Trả về chính đối tượng client để sử dụng bên trong khối `with`

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Được gọi khi thoát khỏi khối `with`, dù thành công hay có lỗi.
        Đây là nơi để dọn dẹp tài nguyên.
        """
        self.session.close()

    # -----------------------------
    def _extract_reqid(self) -> int | None:
        pattern = r"_reqid=(\d+)"
        match = re.search(pattern, self.curl_data["url"])
        if match:
            return int(match.group(1))
        else:
            print("curl_data không hợp lệ: Không tìm thấy _reqid trong url")
            return None

    def _create_session(self) -> requests.Session:
        """Tạo và cấu hình một session requests."""
        session = requests.Session()
        session.headers.update(self.curl_data["headers"])
        session.headers.update({"cookie": self.curl_data["cookie"]})
        return session

    def _build_delete_url(self) -> str:
        """
        Xây dựng URL cho lệnh xóa một notebook:
        - giữ lại tất cả các thông số khác của curl_data['url']
        - thay thế rpcids bằng "WWINqb"
        - tăng _reqid lên một mỗi lần gọi delete để tránh trùng lặp
        - (có lẽ google dùng _reqid để chống tấn công trùng lặp: hiện giờ trùng lặp không sao)
        """
        DEL_RPCID = "WWINqb"
        assert self._reqid is not None
        self._reqid += 1

        rpcids_pattern = r"rpcids=[^&]*"
        reqid_pattern = pattern = r"_reqid=\d+"
        delete_url = re.sub(
            rpcids_pattern, f"rpcids={DEL_RPCID}", self.curl_data["url"]
        )
        delete_url = re.sub(reqid_pattern, f"_reqid={self._reqid}", delete_url)
        return delete_url

    def get_all_notebooks(self) -> str | None:
        """Gửi request để lấy response text chứa danh sách notebooks."""
        print("Đang lấy danh sách notebooks từ server...")
        try:
            response = self.session.post(
                self.curl_data["url"], data=self.curl_data["list_payload"], timeout=30
            )
            if response.status_code == 200:
                return response.text
            else:
                print(
                    f"Lỗi! Không thể lấy danh sách. Status code: {response.status_code}"
                )
                print("Phản hồi từ server:", response.text)
                return None
        except requests.exceptions.RequestException as e:
            print(f"Lỗi mạng: {e}")
            return None

    def delete_notebook(self, notebook_id: str) -> tuple[bool, str]:
        """Gửi request để xóa một notebook cụ thể."""
        delete_freq_template = (
            '[[["WWINqb","[[\\"{notebook_id}\\"],[2]]",null,"generic"]]]'
        )
        payload_dict = {
            "f.req": delete_freq_template.format(notebook_id=notebook_id),
            "at": self.curl_data["list_payload"]["at"],
        }

        try:
            response = self.session.post(self._build_delete_url(), data=payload_dict)
            if response.status_code == 200:
                return True, "Thành công"
            else:
                return (
                    False,
                    f"Status: {response.status_code}, Response: {response.text[:100]}",
                )
        except requests.exceptions.RequestException as e:
            return False, f"Lỗi mạng: {e}"

    def delete_multiple_notebooks(self, notebooks_to_delete: list[dict]):
        """Lặp và xóa nhiều notebooks, báo cáo tiến trình."""
        print("\n--- BẮT ĐẦU QUÁ TRÌNH XÓA ---")
        success_count = 0
        fail_count = 0
        for nb in notebooks_to_delete:
            print(f"Đang xóa '{nb['title']}'...", end="", flush=True)
            status, message = self.delete_notebook(nb["id"])
            if status:
                print(" ✅ Thành công!")
                success_count += 1
            else:
                print(f" ❌ Thất bại! Lý do: {message}")
                fail_count += 1
            time.sleep(0.5)

        print(
            f"\n--- KẾT QUẢ ---\nĐã xóa thành công: {success_count}\nThất bại: {fail_count}"
        )
