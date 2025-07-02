def select_nbs_to_delete(notebooks: list[dict[str, str]]) -> list[dict[str, str]]:
    """
    Giao tiếp với người dùng qua dòng lệnh CLI.
    Từ danh sách các notebooks hiện có dạng [{title: title, id: id}, ...].
    Trả về danh sách các nb cần xóa (tập hợp con của danh sách vào) [{title: title, id:id}, ...]
    """
    print("\n--- DANH SÁCH NOTEBOOKS HIỆN CÓ ---")
    for i, nb in enumerate(notebooks):
        print(f"{i+1:2d}: {nb['title']} (ID: {nb['id']})")

    print("\nNhập số thứ tự của các notebooks bạn muốn xóa (ví dụ: 1, 3, 5-8):")

    try:
        user_input = input("> ")
        if not user_input:
            print("Không chọn notebook nào. Kết thúc.")
            return []

        selected_indices = set()
        parts = user_input.split(",")
        for part in parts:
            part = part.strip()
            if "-" in part:
                start, end = map(int, part.split("-"))
                selected_indices.update(range(start - 1, end))
            else:
                selected_indices.add(int(part) - 1)

        notebooks_to_delete = [
            notebooks[i]
            for i in sorted(list(selected_indices))
            if 0 <= i < len(notebooks)
        ]

        if not notebooks_to_delete:
            print("Lựa chọn không hợp lệ. Kết thúc.")
            return []

        print("\nBẠN SẼ XÓA VĨNH VIỄN CÁC NOTEBOOKS SAU:")
        for nb in notebooks_to_delete:
            print(f"  - {nb['title']}")

        confirm = input("Bạn có chắc chắn không? (nhập 'y' để xác nhận): ")
        if confirm.lower() != "y":
            print("Hành động đã được hủy.")
            return[]
        
        return notebooks_to_delete

    except (ValueError, IndexError):
        print("Lỗi: Input không hợp lệ. Vui lòng chỉ nhập số và theo đúng định dạng.")
        return []
    except Exception as e:
        print(f"Đã xảy ra lỗi không mong muốn: {e}")
        return []
    
if __name__ == "__main__":
    """For manual tests"""
    from pprint import pprint
    notebooks = [
        {"title": "title 1", "id": "id1"},
        {"title": "title 2", "id": "id2"},
        {"title": "title 3", "id": "id3"},
        {"title": "title 4", "id": "id4"},
        {"title": "title 5", "id": "id5"},
        {"title": "title 6", "id": "id6"},
    ]
    pprint(select_nbs_to_delete(notebooks))