# src/main.py
from .client import NotebookLMClient
from .nbs_extractor import extract_notebooks
from .cli import select_nbs_to_delete
from .curl_parser import parse_curl_command

def main():
    """
    The main function of the application.
    Orchestrates the process of fetching, selecting, and deleting notebooks.
    """
    print("🚀 NotebookLM Deleter - Simple & Reliable")
    print("=" * 50)

    # Parse cURL command for authentication
    print("📝 Reading authentication data...")
    curl_data = parse_curl_command("secrets/curl_command.txt")
    if not curl_data:
        return

    try:
        with NotebookLMClient(curl_data) as client:
            # 1. Fetch all notebooks
            response_text = client.get_all_notebooks()
            if not response_text:
                print("❌ Could not retrieve notebooks. Exiting.")
                return

            # 2. Extract notebook data from the response
            all_notebooks = extract_notebooks(response_text)
            if not all_notebooks:
                print("❌ No notebooks found or failed to parse the list. Exiting.")
                return

            # 3. Let the user select which notebooks to delete
            notebooks_to_delete = select_nbs_to_delete(all_notebooks)
            if not notebooks_to_delete:
                print("ℹ️  No notebooks selected for deletion. Exiting.")
                return

            # 4. Execute the deletion
            client.delete_multiple_notebooks(notebooks_to_delete)

    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
