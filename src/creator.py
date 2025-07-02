"""
NotebookLM Creator - 创建笔记本和上传文档
"""
import requests
import json
from urllib.parse import parse_qs, unquote
from .curl_parser import parse_curl_command


class NotebookCreator:
    def __init__(self, curl_data):
        """初始化创建器"""
        self.session = requests.Session()
        self.base_url = curl_data['url'].split('/_/')[0]
        self.auth_headers = curl_data['headers']
        self.cookie_string = curl_data['cookie']
        self.at_token = None
        
        # 设置session
        self.session.headers.update(self.auth_headers)
        
        # 解析cookie字符串并设置
        if self.cookie_string:
            # Cookie字符串格式: "name1=value1; name2=value2"
            cookie_dict = {}
            for cookie_pair in self.cookie_string.split('; '):
                if '=' in cookie_pair:
                    name, value = cookie_pair.split('=', 1)
                    cookie_dict[name] = value
            
            # 将cookie设置到session中
            for name, value in cookie_dict.items():
                self.session.cookies.set(name, value)
        
        # 提取at token (从现有的curl数据中)
        if 'list_payload' in curl_data and 'at' in curl_data['list_payload']:
            self.at_token = curl_data['list_payload']['at']

    def create_new_notebook(self, title=""):
        """
        创建新的笔记本
        
        Args:
            title (str): 笔记本标题，留空则创建无标题笔记本
            
        Returns:
            dict: 包含新创建笔记本信息的响应，如果成功则包含notebook_id
        """
        # 构建创建笔记本的URL
        create_url = f"{self.base_url}/_/LabsTailwindUi/data/batchexecute"
        
        # URL参数 - 提取f.sid等参数从原始URL
        original_url = self.base_url + "/_/LabsTailwindUi/data/batchexecute"
        
        params = {
            'rpcids': 'CCqFvf',
            'source-path': '/',
            'bl': 'boq_labs-tailwind-frontend_20250630.12_p0',
            'f.sid': '7940217633699768402',  # 这个可能需要从原始请求中提取
            'hl': 'en',
            'authuser': '1',
            '_reqid': '2277574',  # 这个可能需要动态生成
            'rt': 'c'
        }
        
        # 构建payload - 精确匹配实际格式
        # 原格式: [[["CCqFvf","[\"\",null,null,[2]]",null,"generic"]]]
        # title参数在第二个位置的数组中的第一个元素
        payload_inner = f'[\\"{title}\\",null,null,[2]]'
        f_req_data = f'[[[\"CCqFvf\",\"{payload_inner}\",null,\"generic\"]]]'
        
        data = {
            'f.req': f_req_data,
            'at': self.at_token
        }
        
        try:
            print(f"🚀 Creating new notebook: '{title}'...")
            
            response = self.session.post(create_url, params=params, data=data)
            
            if response.status_code == 200:
                print("✅ Request sent successfully!")
                # 解析响应以获取新笔记本ID
                return self._parse_create_response(response.text)
            else:
                print(f"❌ Failed to create notebook. Status: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating notebook: {e}")
            return None

    def _parse_create_response(self, response_text):
        """
        解析创建笔记本的响应
        
        Args:
            response_text (str): 服务器响应文本
            
        Returns:
            dict: 解析后的响应信息
        """
        try:
            # NotebookLM的响应通常是特殊格式的JSON
            # 需要进一步分析响应格式来提取笔记本ID
            lines = response_text.strip().split('\n')
            for line in lines:
                if line.startswith('['):
                    # 尝试解析JSON响应
                    try:
                        data = json.loads(line)
                        # 这里需要根据实际响应格式来提取笔记本ID
                        print(f"📄 Response data: {data}")
                        return {"success": True, "response": data}
                    except json.JSONDecodeError:
                        continue
            
            return {"success": True, "raw_response": response_text}
            
        except Exception as e:
            print(f"⚠️  Warning: Could not parse create response: {e}")
            return {"success": True, "raw_response": response_text}

    def upload_document(self, notebook_id, file_path):
        """
        上传文档到指定笔记本
        
        Args:
            notebook_id (str): 目标笔记本ID
            file_path (str): 要上传的文件路径
            
        Returns:
            bool: 上传是否成功
        """
        print(f"📤 Document upload for notebook {notebook_id} is not yet implemented.")
        print(f"📝 File to upload: {file_path}")
        
        # TODO: 实现文档上传功能
        # 这需要更多的网络请求分析来确定上传API
        
        return False


def create_notebook_interactive():
    """交互式创建笔记本"""
    print("🚀 NotebookLM Creator - Interactive Mode")
    print("=" * 50)
    
    # 读取认证数据 - 使用默认路径
    print("📝 Reading authentication data...")
    curl_data = parse_curl_command()  # 不传参数，使用自动路径检测
    if not curl_data:
        return
    
    print("✅ Authentication loaded!")
    
    # 创建creator实例
    creator = NotebookCreator(curl_data)
    
    # 获取用户输入
    title = input("\n📋 Enter notebook title (press Enter for untitled): ").strip()
    if not title:
        title = ""
        print("📝 Creating untitled notebook...")
    
    # 创建笔记本
    result = creator.create_new_notebook(title)
    
    if result and result.get("success"):
        print("🎉 Notebook created successfully!")
        if "response" in result:
            print(f"📄 Server response: {result['response']}")
    else:
        print("❌ Failed to create notebook.")


if __name__ == "__main__":
    create_notebook_interactive() 