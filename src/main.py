#!/usr/bin/env python3
"""
NotebookLM Deleter & Creator - 批量管理NotebookLM笔记本
"""

from .curl_parser import parse_curl_command
from .client import NotebookLMClient
from .cli import display_welcome, select_nbs_to_delete
from .creator import create_notebook_interactive
from .nbs_extractor import extract_notebooks


def main():
    """主程序入口"""
    display_welcome()
    
    # 显示操作选项
    print("🎯 Choose an operation:")
    print("1. 📝 Create new notebook")
    print("2. 🗑️  Delete existing notebooks")
    print("3. ❌ Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        # 创建新笔记本
        create_notebook_interactive()
        return
    elif choice == "2":
        # 删除笔记本（原有功能）
        delete_notebooks()
        return
    elif choice == "3":
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice. Please enter 1, 2, or 3.")
        return


def delete_notebooks():
    """删除笔记本的功能"""
    # Parse cURL command for authentication - 使用自动路径检测
    print("📝 Reading authentication data...")
    curl_data = parse_curl_command()  # 不传参数，使用自动路径检测
    if not curl_data:
        return

    print("✅ Successfully parsed cURL command!")

    # Initialize client
    client = NotebookLMClient(curl_data)

    # Get all notebooks - 注意这里返回的是原始响应文本
    print("Fetching notebooks from the server...")
    response_text = client.get_all_notebooks()
    if not response_text:
        return

    print("✅ Successfully fetched notebook list.")

    # 解析响应文本以提取笔记本信息
    try:
        notebooks = extract_notebooks(response_text)
    except ValueError as e:
        print(f"❌ Failed to parse notebook list: {e}")
        return

    if not notebooks:
        print("ℹ️  No notebooks found.")
        return

    # Display and select notebooks
    selected_notebooks = select_nbs_to_delete(notebooks)
    if not selected_notebooks:
        print("ℹ️  No notebooks selected for deletion. Exiting.")
        return

    # Confirm deletion
    print(f"\n⚠️  You are about to delete {len(selected_notebooks)} notebook(s):")
    for notebook in selected_notebooks:
        print(f"   • {notebook['title']} (ID: {notebook['id']})")

    confirm = input("\n❓ Are you sure you want to delete these notebooks? (yes/no): ").lower().strip()
    if confirm not in ['yes', 'y']:
        print("ℹ️  Deletion cancelled. Exiting.")
        return

    # Delete notebooks
    print(f"\n🗑️  Deleting {len(selected_notebooks)} notebook(s)...")
    success_count = 0
    for notebook in selected_notebooks:
        success, message = client.delete_notebook(notebook['id'])
        if success:
            success_count += 1
            print(f"✅ Deleted: {notebook['title']}")
        else:
            print(f"❌ Failed to delete: {notebook['title']} - {message}")

    # Summary
    print(f"\n🎯 Deletion Summary:")
    print(f"   ✅ Successfully deleted: {success_count}")
    print(f"   ❌ Failed to delete: {len(selected_notebooks) - success_count}")
    print(f"   📊 Total processed: {len(selected_notebooks)}")

    if success_count == len(selected_notebooks):
        print("\n🎉 All notebooks deleted successfully!")
    elif success_count > 0:
        print("\n⚠️  Some notebooks could not be deleted. Please check the error messages above.")
    else:
        print("\n❌ No notebooks were deleted. Please check your authentication and try again.")


if __name__ == "__main__":
    main()
