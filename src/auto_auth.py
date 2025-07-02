#!/usr/bin/env python3
"""
NotebookLM 自动化认证辅助工具
提供多种方案简化认证过程，避免手动复制cURL的繁琐操作
"""

import os
import json
import time
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any
from .curl_parser import get_secrets_path
from .nbs_extractor import extract_notebooks


def check_auth_validity() -> bool:
    """
    检查当前认证是否有效
    
    Returns:
        bool: 认证是否有效
    """
    from .curl_parser import parse_curl_command
    from .client import NotebookLMClient
    
    try:
        auth_data = parse_curl_command()
        if not auth_data:
            return False
            
        client = NotebookLMClient(auth_data)
        response_text = client.get_all_notebooks()
        if not response_text:
            return False
            
        # 尝试解析笔记本列表来验证认证
        notebooks = extract_notebooks(response_text)
        return len(notebooks) >= 0  # 只要能解析就说明认证有效
    except:
        return False


def get_auth_age() -> Optional[int]:
    """
    获取认证文件的年龄（分钟）
    
    Returns:
        int: 文件年龄（分钟），如果文件不存在返回None
    """
    secrets_path = get_secrets_path()
    curl_file = secrets_path / "curl_command.txt"
    
    if not curl_file.exists():
        return None
        
    file_time = curl_file.stat().st_mtime
    current_time = time.time()
    age_seconds = current_time - file_time
    return int(age_seconds / 60)


def show_auth_status():
    """
    显示当前认证状态
    """
    print("🔐 认证状态检查")
    print("=" * 40)
    
    age = get_auth_age()
    if age is None:
        print("❌ 未找到认证文件")
        return False
        
    print(f"📅 认证文件年龄: {age} 分钟")
    
    if age > 35:  # 接近40分钟限制
        print("⚠️  认证即将过期 (>35分钟)")
    elif age > 40:
        print("❌ 认证已过期 (>40分钟)")
    else:
        print("✅ 认证文件较新")
        
    is_valid = check_auth_validity()
    if is_valid:
        print("✅ 认证有效，可以正常使用")
        return True
    else:
        print("❌ 认证无效，需要更新")
        return False


def open_notebooklm_for_auth():
    """
    自动打开NotebookLM页面，方便用户获取新的认证
    """
    url = "https://notebooklm.google.com/"
    print(f"🌐 正在打开 NotebookLM 页面...")
    print(f"📋 请在页面中：")
    print(f"   1. 确认已登录")
    print(f"   2. 打开开发者工具 (F12)")
    print(f"   3. 切换到 Network 选项卡")
    print(f"   4. 刷新页面或进行任何操作")
    print(f"   5. 找到 batchexecute 请求")
    print(f"   6. 右键选择 'Copy as cURL'")
    print(f"   7. 将内容保存到 secrets/curl_command.txt")
    
    webbrowser.open(url)


def create_auth_helper_script():
    """
    创建一个便捷的认证更新脚本
    """
    secrets_path = get_secrets_path()
    script_content = '''@echo off
echo ======================================
echo   NotebookLM 认证更新助手
echo ======================================
echo.
echo 请将从浏览器复制的 cURL 命令粘贴到下面，
echo 输入完成后按两次 Enter 键结束输入：
echo.

setlocal enabledelayedexpansion
set "content="
:input_loop
set /p "line="
if "!line!"=="" (
    if defined content (
        goto :save_content
    )
) else (
    if defined content (
        set "content=!content!!line! "
    ) else (
        set "content=!line! "
    )
)
goto :input_loop

:save_content
echo !content! > "%~dp0curl_command.txt"
echo.
echo ✅ 认证信息已保存到 curl_command.txt
echo.
pause
'''
    
    script_path = secrets_path / "update_auth.bat"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ 创建认证更新脚本: {script_path}")
    print(f"💡 您可以双击运行此脚本来快速更新认证")
    
    return script_path


def auto_auth_workflow():
    """
    自动化认证工作流程
    """
    print("🤖 自动化认证助手")
    print("=" * 50)
    
    # 1. 检查当前认证状态
    is_valid = show_auth_status()
    
    if is_valid:
        print("\n✅ 当前认证有效，无需更新")
        return True
        
    print("\n🔄 需要更新认证，启动辅助流程...")
    
    # 2. 提供多种更新方案
    print("\n📋 选择认证更新方式:")
    print("1. 🌐 自动打开NotebookLM页面（推荐）")
    print("2. 📄 创建便捷更新脚本")
    print("3. 📝 手动输入新的cURL命令")
    print("4. ❌ 跳过认证更新")
    
    choice = input("\n请选择 (1-4): ").strip()
    
    if choice == "1":
        open_notebooklm_for_auth()
        print("\n⏳ 请按照上述步骤获取新的cURL命令...")
        input("完成后按 Enter 键继续...")
        
        # 重新检查认证
        if check_auth_validity():
            print("✅ 认证更新成功！")
            return True
        else:
            print("❌ 认证仍然无效，请检查cURL命令是否正确")
            return False
            
    elif choice == "2":
        script_path = create_auth_helper_script()
        print(f"\n💡 请运行脚本: {script_path}")
        return False
        
    elif choice == "3":
        return manual_curl_input()
        
    else:
        print("⏭️  跳过认证更新")
        return False


def manual_curl_input() -> bool:
    """
    手动输入cURL命令
    """
    print("\n📝 手动输入cURL命令")
    print("请粘贴完整的cURL命令 (输入END结束):")
    
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    
    curl_command = " ".join(lines)
    
    if not curl_command.strip():
        print("❌ 未输入任何内容")
        return False
    
    # 保存到文件
    secrets_path = get_secrets_path()
    curl_file = secrets_path / "curl_command.txt"
    
    try:
        with open(curl_file, 'w', encoding='utf-8') as f:
            f.write(curl_command)
        
        print("✅ cURL命令已保存")
        
        # 验证认证
        if check_auth_validity():
            print("✅ 认证验证成功！")
            return True
        else:
            print("❌ 认证验证失败，请检查cURL命令格式")
            return False
            
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False


def smart_auth_check():
    """
    智能认证检查 - 在程序启动时自动检查和提示
    """
    age = get_auth_age()
    
    # 如果文件不存在或太旧，主动提示更新
    if age is None or age > 35:
        print("⚠️  检测到认证问题，建议更新认证信息")
        
        update = input("是否现在更新认证？(y/N): ").lower().strip()
        if update in ['y', 'yes']:
            return auto_auth_workflow()
        else:
            print("💡 提示：如果遇到认证错误，请运行认证更新流程")
            return age is not None  # 如果文件存在就继续，即使可能过期
    
    # 认证文件较新，进行有效性检查
    if not check_auth_validity():
        print("❌ 认证文件存在但无效，建议更新")
        return auto_auth_workflow()
    
    return True


if __name__ == "__main__":
    auto_auth_workflow() 