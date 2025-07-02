# src/main.py (Phiên bản sử dụng Context Manager)

from src.curl_parser import parse_curl_command
from src.nbs_extractor import extract_notebooks
from src.cli import select_nbs_to_delete
from src.client import NotebookLMClient


def run_app(client: NotebookLMClient):
    """
    Hàm chứa logic chính của ứng dụng, nhận vào một client đã được khởi tạo.
    """
    # 1. Fetch & Extract
    response_text = client.get_all_notebooks()
    if response_text == None:
        return
    if '"e",4,null,null,143' in response_text:
        print("Có lỗi khi lấy danh sách từ server")
        print("at token đã hết hạn, làm ơn cập nhật lại curl_command.txt")
        print(f"response_text: {response_text}")
        return

    notebooks = extract_notebooks(response_text)
    if not notebooks:
        print("Không có notebook nào để xóa!")
        return

    # 2. Interact (CLI)
    notebooks_to_delete = select_nbs_to_delete(notebooks)
    if not notebooks_to_delete:
        print("Không có notebook nào được chọn. Kết thúc chương trình.")
        return

    # 3. Execute
    client.delete_multiple_notebooks(notebooks_to_delete)


def main():
    """Hàm chính: chỉ chịu trách nhiệm thiết lập và dọn dẹp."""

    print("Đang đọc và phân tích file 'curl_command.txt'...")
    curl_data = parse_curl_command(filepath="secrets/curl_command.txt")
    if not curl_data:
        return

    # Sử dụng `with` để tự động quản lý vòng đời của client
    # try:
    with NotebookLMClient(curl_data) as client:
        run_app(client)
    # except Exception as e:
    # print(f"\nĐã xảy ra lỗi không mong muốn trong quá trình chạy: {e}")


if __name__ == "__main__":
    main()
