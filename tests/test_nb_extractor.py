import unittest

from src.nbs_extractor import extract_notebooks
from pathlib import Path


class TestNotebookExtractor(unittest.TestCase):
    def setUp(self):
        """Preparing data for tests"""
        CURRENT_DIR = Path(__file__).parent
        file_path = CURRENT_DIR / "data/list_nb_response.txt"
        try:
            with open(file_path, "r") as f:
                sample_response_text = f.read().strip()
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file '{file_path}'.")
            print("Vui lòng tạo file này và dán lệnh reponse text vào đó.")
            return None

        self.response_text = sample_response_text

    def test_successful_extraction(self):
        nb_list = extract_notebooks(self.response_text)

        self.assertIsInstance(nb_list, list)
        # self.assertEqual(len(nb_list), 3, "Must found exact 3 notebooks")

        # Check the first notebook
        self.assertEqual(
            nb_list[0]["title"], "Notebook Name 1"
        )
        self.assertEqual(nb_list[0]["id"], "1bf5f3d9-7a14-4b97-8af8-7e9c7c1101b9")

        # Check the second notebook
        self.assertEqual(nb_list[1]["title"], "Notebook Name 2")
        self.assertEqual(nb_list[1]["id"], "029d0fa0-7db8-4ada-a1a2-d96890800e60")

        # Check the third notebook
        self.assertEqual(
            nb_list[2]["title"], "Notebook Name 3"
        )
        self.assertEqual(nb_list[2]["id"], "03663619-8bec-475e-b401-635999254980")


if __name__ == "__main__":
    unittest.main()
