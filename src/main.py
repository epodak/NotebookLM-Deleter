#!/usr/bin/env python3
"""
NotebookLM 笔记本管理器主程序
功能包括：创建、删除、列表查看、文档上传、认证管理
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from .curl_parser import parse_curl_command
from .client import NotebookLMClient  
from .creator import create_notebook_interactive
from .uploader import upload_file_to_notebook_interactive
from .auto_auth import smart_auth_check, auto_auth_workflow, show_auth_status
from .nbs_extractor import extract_notebooks


def delete_notebooks_interactive():
    """
    交互式删除笔记本
    """
    print("正在获取笔记本列表...")
    
    auth_data = parse_curl_command()
    if not auth_data:
        print("❌ 无法解析认证数据")
        return
    
    client = NotebookLMClient(auth_data)
    
    # 获取原始响应文本
    response_text = client.get_all_notebooks()
    if not response_text:
        print("❌ 无法获取笔记本列表")
        return
    
    # 解析笔记本列表
    try:
        notebooks = extract_notebooks(response_text)
    except ValueError as e:
        print(f"❌ 解析笔记本列表失败: {e}")
        return
    
    if not notebooks:
        print("❌ 笔记本列表为空")
        return
    
    print(f"\n📚 找到 {len(notebooks)} 个笔记本:")
    print("-" * 60)
    
    for i, nb in enumerate(notebooks, 1):
        notebook_id = nb.get('id', '未知')  # 使用'id'字段
        title = nb.get('title', '无标题')
        print(f"{i:2d}. [{notebook_id[:8]}...] {title}")
    
    print("-" * 60)
    print("请选择要删除的笔记本 (可多选，用逗号分隔，如: 1,3,5)")
    print("输入 'all' 删除所有笔记本")
    print("输入 'q' 取消操作")
    
    user_input = input("\n请输入选择: ").strip()
    
    if user_input.lower() == 'q':
        print("操作已取消")
        return
    
    selected_notebooks = []
    
    if user_input.lower() == 'all':
        selected_notebooks = notebooks.copy()
    else:
        try:
            indices = [int(x.strip()) for x in user_input.split(',')]
            for idx in indices:
                if 1 <= idx <= len(notebooks):
                    selected_notebooks.append(notebooks[idx-1])
                else:
                    print(f"⚠️  忽略无效索引: {idx}")
        except ValueError:
            print("❌ 输入格式错误")
            return
    
    if not selected_notebooks:
        print("❌ 没有选择任何笔记本")
        return
    
    print(f"\n将要删除 {len(selected_notebooks)} 个笔记本:")
    for nb in selected_notebooks:
        title = nb.get('title', '无标题')
        print(f"  - {title}")
    
    confirm = input(f"\n⚠️  确认删除这些笔记本吗？(输入 'yes' 确认): ").strip()
    
    if confirm.lower() != 'yes':
        print("操作已取消")
        return
    
    print("\n开始删除操作...")
    success_count = 0
    
    for nb in selected_notebooks:
        notebook_id = nb.get('id')  # 使用'id'字段
        title = nb.get('title', '无标题')
        
        success, message = client.delete_notebook(notebook_id)
        if success:
            print(f"✅ 已删除: {title}")
            success_count += 1
        else:
            print(f"❌ 删除失败: {title} - {message}")
    
    print(f"\n删除完成！成功删除 {success_count}/{len(selected_notebooks)} 个笔记本")


def list_notebooks_interactive():
    """
    交互式查看笔记本列表
    """
    print("正在获取笔记本列表...")
    
    auth_data = parse_curl_command()
    if not auth_data:
        print("❌ 无法解析认证数据")
        return
    
    client = NotebookLMClient(auth_data)
    
    # 获取原始响应文本
    response_text = client.get_all_notebooks()
    if not response_text:
        print("❌ 无法获取笔记本列表")
        return
    
    # 解析笔记本列表
    try:
        notebooks = extract_notebooks(response_text)
    except ValueError as e:
        print(f"❌ 解析笔记本列表失败: {e}")
        return
    
    if not notebooks:
        print("❌ 笔记本列表为空")
        return
    
    print(f"\n📚 找到 {len(notebooks)} 个笔记本:")
    print("-" * 80)
    print(f"{'序号':<4} {'笔记本ID':<20} {'标题'}")
    print("-" * 80)
    
    for i, nb in enumerate(notebooks, 1):
        notebook_id = nb.get('id', '未知')  # 使用'id'字段
        title = nb.get('title', '无标题')
        print(f"{i:<4} {notebook_id[:18]:<20} {title}")
    
    print("-" * 80)


def show_menu():
    """
    显示主菜单
    """
    print("\n" + "="*50)
    print("🤖 NotebookLM 笔记本管理器")
    print("="*50)
    print("1. 📋 查看笔记本列表")
    print("2. ➕ 创建新笔记本")
    print("3. 🗑️  删除笔记本")
    print("4. 📄 上传文档到笔记本")
    print("5. 🔐 认证状态检查")
    print("6. 🔄 更新认证信息")
    print("7. ❌ 退出程序")
    print("="*50)


def main():
    """
    主程序入口
    """
    print("🚀 启动 NotebookLM 管理器...")
    
    # 启动时自动检查认证
    print("\n🔍 检查认证状态...")
    if not smart_auth_check():
        print("❌ 认证检查失败，程序可能无法正常工作")
        print("💡 建议选择菜单中的认证管理选项")
    
    while True:
        try:
            show_menu()
            choice = input("\n请选择操作 (1-7): ").strip()
            
            if choice == "1":
                list_notebooks_interactive()
                
            elif choice == "2":
                create_notebook_interactive()
                
            elif choice == "3":
                delete_notebooks_interactive()
                
            elif choice == "4":
                upload_file_to_notebook_interactive()
                
            elif choice == "5":
                show_auth_status()
                
            elif choice == "6":
                auto_auth_workflow()
                
            elif choice == "7":
                print("👋 再见！")
                break
                
            else:
                print("❌ 无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n\n👋 程序被用户中断，再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            print("程序将继续运行...")


if __name__ == "__main__":
    main() 