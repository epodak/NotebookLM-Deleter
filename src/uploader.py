#!/usr/bin/env python3
"""
NotebookLM 文档上传器
支持向指定笔记本上传文档内容
"""

import json
import requests
import re
from typing import Optional, Dict, Any, List
from .curl_parser import parse_curl_command
from .client import NotebookLMClient
from .nbs_extractor import extract_notebooks


def select_target_notebook() -> Optional[str]:
    """
    让用户从现有笔记本中选择上传目标
    
    Returns:
        str: 选择的笔记本ID，如果取消则返回None
    """
    print("📋 获取笔记本列表...")
    
    # 获取认证数据
    auth_data = parse_curl_command()
    if not auth_data:
        print("❌ 无法解析认证数据")
        return None
    
    # 获取笔记本列表
    client = NotebookLMClient(auth_data)
    response_text = client.get_all_notebooks()
    if not response_text:
        print("❌ 无法获取笔记本列表")
        return None
    
    try:
        notebooks = extract_notebooks(response_text)
    except ValueError as e:
        print(f"❌ 解析笔记本列表失败: {e}")
        return None
    
    if not notebooks:
        print("ℹ️  未找到任何笔记本")
        return None
    
    # 显示笔记本列表
    print(f"\n📚 找到 {len(notebooks)} 个笔记本:")
    print("-" * 80)
    for i, nb in enumerate(notebooks, 1):
        print(f"{i:2}. {nb['title']} (ID: {nb['id']})")
    print("-" * 80)
    
    # 用户选择
    while True:
        try:
            choice = input(f"请选择目标笔记本 (1-{len(notebooks)}) 或输入 0 取消: ").strip()
            if choice == "0":
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(notebooks):
                selected = notebooks[index]
                print(f"✅ 已选择: {selected['title']}")
                return selected['id']
            else:
                print(f"❌ 请输入 1-{len(notebooks)} 之间的数字")
        except ValueError:
            print("❌ 请输入有效数字")


def upload_document_to_notebook(notebook_id: str, content: str, title: str = "上传的文档") -> bool:
    """
    上传文档到指定的NotebookLM笔记本
    
    Args:
        notebook_id: 目标笔记本ID
        content: 文档内容
        title: 文档标题
        
    Returns:
        bool: 上传是否成功
    """
    # 解析cURL认证数据
    auth_data = parse_curl_command()
    if not auth_data:
        print("❌ 无法解析认证数据，请更新 secrets/curl_command.txt")
        return False
    
    try:
        # 1. 首先获取上传会话
        upload_session = _initiate_upload_session(auth_data, notebook_id)
        if not upload_session:
            print("❌ 无法创建上传会话")
            return False
            
        # 2. 上传文档内容
        success = _upload_content(upload_session, content, auth_data)
        if success:
            print(f"✅ 文档 '{title}' 上传成功！")
            return True
        else:
            print("❌ 文档上传失败")
            return False
            
    except Exception as e:
        print(f"❌ 上传过程出现错误: {e}")
        return False


def _initiate_upload_session(auth_data: Dict[str, Any], notebook_id: str) -> Optional[Dict[str, str]]:
    """
    初始化上传会话，获取upload_id
    """
    # 临时方案：从upload.txt中提取已有的upload_id作为模板
    upload_url = "https://notebooklm.google.com/upload/_/"
    
    # 从现有的upload.txt URL中提取upload_id格式
    # 实际实现中需要调用相应API获取新的upload_id
    upload_id = "ABgVH89KdApCCUEFm6IzNBvLyI-a_8CATq32T-MMg4Bp3kVALogN8xa5qg4pMPkocpbJ4uNv2wRDBY9QasY2nh8zhuOpKIYon-k4D1s3X-2Iag"
    
    return {
        "upload_url": f"{upload_url}?authuser=0&upload_id={upload_id}&upload_protocol=resumable",
        "upload_id": upload_id
    }


def _upload_content(upload_session: Dict[str, str], content: str, auth_data: Dict[str, Any]) -> bool:
    """
    执行实际的文档内容上传
    """
    try:
        # 构建请求
        url = upload_session["upload_url"]
        
        # 使用认证数据中的headers，并修复cookies字段名问题
        headers = auth_data["headers"].copy()
        headers.update({
            'content-type': 'application/x-www-form-urlencoded;charset=utf-8',
            'x-goog-upload-command': 'upload, finalize',
            'x-goog-upload-offset': '0'
        })
        
        # 修复cookies字段 - 检查auth_data中实际的cookie字段名
        cookies_data = None
        if "cookies" in auth_data:
            cookies_data = auth_data["cookies"]
        elif "cookie" in auth_data:
            cookies_data = auth_data["cookie"]
        else:
            print("❌ 认证数据中未找到cookies信息")
            return False
        
        print(f"📡 正在上传到: {url}")
        print(f"📄 文档大小: {len(content.encode('utf-8'))} 字节")
        
        # 发送上传请求
        response = requests.post(
            url,
            headers=headers,
            cookies=cookies_data if isinstance(cookies_data, dict) else None,
            data=content.encode('utf-8'),
            timeout=30
        )
        
        print(f"📡 上传响应状态: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 上传请求成功")
            return True
        else:
            print(f"❌ 上传失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ 上传请求失败: {e}")
        return False


def upload_file_to_notebook_interactive():
    """
    交互式文档上传功能
    """
    print("📁 NotebookLM 文档上传器")
    print("=" * 40)
    
    # 1. 选择目标笔记本
    notebook_id = select_target_notebook()
    if not notebook_id:
        print("❌ 未选择笔记本，取消上传")
        return
    
    # 2. 获取文档内容方式
    print("\n📝 选择文档内容来源:")
    print("1. 直接输入文本")
    print("2. 从文件读取")
    
    choice = input("请选择 (1-2): ").strip()
    
    content = ""
    title = "上传的文档"
    
    if choice == "1":
        print("\n请输入文档内容 (输入END结束):")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        content = "\n".join(lines)
        title = input("请输入文档标题: ").strip() or "手动输入的文档"
        
    elif choice == "2":
        file_path = input("请输入文件路径: ").strip()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            title = input("请输入文档标题: ").strip() or f"从{file_path}上传的文档"
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return
    else:
        print("❌ 无效选择")
        return
    
    if not content.strip():
        print("❌ 文档内容不能为空")
        return
    
    print(f"\n📤 开始上传文档...")
    success = upload_document_to_notebook(notebook_id, content, title)
    
    if success:
        print("🎉 文档上传完成！")
    else:
        print("💔 文档上传失败，请检查网络连接和认证信息")


if __name__ == "__main__":
    upload_file_to_notebook_interactive() 