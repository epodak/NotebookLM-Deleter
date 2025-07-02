"""
Command Line Interface utilities for NotebookLM Deleter
"""


def display_welcome():
    """显示欢迎信息"""
    print("🚀 NotebookLM Manager - Create & Delete")
    print("=" * 50)


def select_nbs_to_delete(notebooks: list[dict[str, str]]) -> list[dict[str, str]]:
    """
    Interacts with the user via the command line to select notebooks for deletion.
    Takes a list of notebooks and returns a list of notebooks to be deleted.
    """
    if not notebooks:
        print("No notebooks found.")
        return []
        
    print("\n--- AVAILABLE NOTEBOOKS ---")
    for i, nb in enumerate(notebooks):
        print(f"{i+1:2d}: {nb['title']} (ID: {nb['id']})")

    print("\nEnter the numbers of the notebooks you want to delete (e.g., 1, 3, 5-8):")

    try:
        user_input = input("> ")
        if not user_input:
            print("No notebooks selected. Exiting.")
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
            print("Invalid selection. Exiting.")
            return []

        print("\nTHE FOLLOWING NOTEBOOKS WILL BE PERMANENTLY DELETED:")
        for nb in notebooks_to_delete:
            print(f"  - {nb['title']}")

        confirm = input("Are you sure? (type 'y' to confirm): ")
        if confirm.lower() != "y":
            print("Action cancelled.")
            return []
        
        return notebooks_to_delete

    except (ValueError, IndexError):
        print("Error: Invalid input. Please enter numbers in the correct format.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
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