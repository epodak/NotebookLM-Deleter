# NotebookLM 删除工具

一个简单但强大的命令行工具（CLI），帮助您查看和批量删除 `notebooklm.google.com` 上的笔记本。

## 解决的问题

目前，Google NotebookLM 的网页界面只允许一次删除一个笔记本。当您有几十或几百个笔记本需要清理时，这非常不方便。这个工具正是为了解决这个问题而诞生的。

## 功能

- 列出您所有的笔记本并附上序号。
- 友好的命令行界面，用于选择要删除的笔记本。
- 支持选择离散数字（例如：`1, 5, 10`）和范围（例如：`20-30`），甚至是这两种类型的混合。
- 安全地执行批量删除并详细报告结果。
- 只需一次复制粘贴即可轻松更新凭据信息。

---

### ⚠️ 重要警告

- **删除操作是永久性的，无法撤销。**
- 请务必仔细检查将要删除的笔记本列表，然后再确认。
- 作者不对任何数据丢失负责。**请谨慎使用！**
- 工具不要求您输入任何账户密码。

使用 cookies 进行身份验证的机制：
- 尽管这种机制比您直接提供 Google 账户登录密码更安全，但它也带来了不便，即大约每 30 分钟会话将过期，旧的 cookies 将无效。如果您想继续工作，则必须从 dev-tool 重新复制 cURL（按照下面的说明）。
- 尽管这种机制比直接使用密码更安全，但您需要注意，您在 dev-tool 中复制的 cURL 段包含您在 Google 账户上的会话身份验证信息，您**不应通过网络与任何人分享**包含 cookies 的内容。

---

## 安装

该项目使用 Python 3 编写，并在 Linux 上的 Python 3.12 上进行了测试。

1.  **克隆仓库到本地：**
    ```bash
    git clone https://github.com/tuan-karma/NotebookLM-Deleter.git
    cd notebooklm-deleter
    ```

2.  **创建并激活虚拟环境：**
    ```bash
    python -m venv venv
    source venv/bin/activate  # 在 Windows 上使用 `venv\Scripts\activate`
    ```

3.  **安装所需的库：**
    ```bash
    pip install -r requirements.txt
    ```

## 使用指南

该工具通过模拟来自您浏览器的有效请求来工作。因此，您需要为其提供一个临时的"钥匙"来进入。

**步骤 1：获取"钥匙"（cURL 命令）**

这是最重要的一步，每次您想运行工具时（或当旧的"钥匙"过期时）都需要执行。

1.  在 Chrome 浏览器（或基于 Chromium 的浏览器）中打开 `notebooklm.google.com`。
2.  按 **F12** 打开开发者工具。
3.  切换到 **Network** 选项卡。
4.  重新加载页面（按 **Ctrl+R** 或 **Cmd+R**）。
5.  在请求列表中，找到一个名称以 `batchexecute?rpcids=wXbhsf...` 开头的请求。通常它是您重新加载页面后的第二个请求。这是获取笔记本列表的请求。
6.  右键单击该请求，选择 **Copy** -> **Copy as cURL (bash)**。

**步骤 2：为工具提供"钥匙"**

1.  在项目目录中，找到 `secrets/` 目录。
2.  打开 `curl_command.txt` 文件。如果没有，请创建它。
3.  删除所有旧内容（如果有），并**粘贴您刚刚复制的整个 cURL 命令**到该文件中。
4.  保存文件。

**步骤 3：运行工具**

在项目根目录打开终端并运行命令：

```bash
python -m src.main
```

程序将读取 `curl_command.txt` 文件，获取笔记本列表，并在命令行界面上指导您进行后续步骤。

## 项目结构

```
notebooklm-deleter/
├── secrets/
│   └── curl_command.txt   # 包含临时身份验证信息的文件
├── src/
│   ├── main.py            # 主要入口，协调应用程序
│   ├── client.py          # 与 NotebookLM API 通信的客户端类
│   ├── curl_parser.py     # cURL 命令解析模块
│   ├── nbs_extractor.py   # 笔记本数据提取模块
│   └── cli.py             # 命令行界面处理模块
│
└── tests/
    └── ...                # 单元测试文件
```

## 贡献

欢迎任何贡献、问题报告（issue）或功能请求（pull request）。如果您有改进此工具的想法，请不要犹豫，创建一个 issue 让我们一起讨论。

## 未来计划

- [ ] 将测试框架从 `unittest` 转换为 `pytest`，以使测试代码更简洁和强大。
- [ ] 添加 CI/CD 以便在未来扩展项目（如果大家支持的话，呵呵）。

## 许可证

本项目根据 [MIT 许可证](LICENSE) 发布。

---

*如果您觉得这个工具有用，请考虑为项目加一颗星 ⭐！谢谢您。*