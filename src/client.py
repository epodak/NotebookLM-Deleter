# src/client.py

import requests
import time

class NotebookLMClient:
    """
    A client to interact with Google NotebookLM's internal API using cURL-extracted credentials.
    """

    def __init__(self, curl_data: dict):
        self.curl_data = curl_data
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Creates and configures a requests session with auth headers."""
        session = requests.Session()
        session.headers.update(self.curl_data["headers"])
        session.headers.update({"cookie": self.curl_data["cookie"]})
        return session

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def get_all_notebooks(self) -> str | None:
        """Sends a request to get the response text containing the notebook list."""
        print("Fetching notebooks from the server...")
        try:
            response = self.session.post(
                self.curl_data["url"], 
                data=self.curl_data["list_payload"], 
                timeout=30
            )
            if response.status_code == 200:
                print("✅ Successfully fetched notebook list.")
                return response.text
            else:
                print(f"❌ Error fetching list. Status code: {response.status_code}")
                if response.status_code in [401, 403]:
                    print("💡 Your authentication may have expired. Please get a fresh cURL command.")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return None

    def delete_notebook(self, notebook_id: str) -> tuple[bool, str]:
        """Sends a request to delete a specific notebook."""
        # Build the delete URL by modifying the original URL
        import re
        delete_url = re.sub(r'rpcids=[^&]*', 'rpcids=WWINqb', self.curl_data["url"])
        
        delete_f_req = f'[[["WWINqb","[[\\"{notebook_id}\\"],[2]]",null,"generic"]]]'
        payload = {
            "f.req": delete_f_req,
            "at": self.curl_data["list_payload"]["at"],
        }

        try:
            response = self.session.post(delete_url, data=payload)
            if response.status_code == 200:
                return True, "Success"
            else:
                return False, f"Status: {response.status_code}, Response: {response.text[:100]}"
        except requests.exceptions.RequestException as e:
            return False, f"Network error: {e}"

    def delete_multiple_notebooks(self, notebooks_to_delete: list[dict]):
        """Loops through and deletes multiple notebooks, reporting progress."""
        print("\n--- STARTING DELETION PROCESS ---")
        if not notebooks_to_delete:
            print("No notebooks selected for deletion.")
            return

        success_count = 0
        fail_count = 0
        
        for nb in notebooks_to_delete:
            print(f"Deleting '{nb['title']}'...", end="", flush=True)
            status, message = self.delete_notebook(nb["id"])
            if status:
                print(" ✅ Success!")
                success_count += 1
            else:
                print(f" ❌ Failed! Reason: {message}")
                fail_count += 1
            time.sleep(0.5)

        print(
            f"\n--- RESULTS ---\nSuccessfully deleted: {success_count}\nFailed: {fail_count}"
        )
