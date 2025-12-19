# 🧠 Obsidian-mcp-manager

<p align="center">

<img alt="Python版本" src="https://img.shields.io/badge/Python-3.10%252B-blue">

<img alt="MCP协议" src="https://img.shields.io/badge/MCP-Standard-purple">

<img alt="多平台支持" src="https://img.shields.io/badge/%E5%B9%B3%E5%8F%B0-Windows%252FLinux%252FmacOS-green">

<img alt="开源协议" src="https://img.shields.io/badge/许可-Apache2.0-orange">

</p>

> 基于 Model Context Protocol (MCP) 的智能知识库管家，赋予 AI 直接管理、优化和重构 Obsidian 笔记的能力

Obsidian-mcp-manager 是一个专为 Obsidian 用户设计的 MCP 服务端工具。它打通了本地文件系统与 LLM（如 Claude）之间的通道，让 AI 不仅能“读”懂你的笔记，还能像资深编辑一样自动优化格式、生成元数据标签，甚至像架构师一样重构整个文件夹目录。

## ✨ 核心功能

- **🏷️ 智能打标**：深度分析笔记内容，自动生成符合知识体系的 YAML Frontmatter (Tags/分类)
- **🎨 格式美化**：自动规范 Markdown 标题层级、修复段落间距、补全代码块标记
- **📂 架构重构**：全局审计文件夹结构，基于语义理解自动归类和移动文件 (支持 PARA 等方法)
- **🔒 安全写入**：全量更新机制，确保在优化格式时绝对保留原始图片链接和正文内容
- **🔌 无缝集成**：基于标准 MCP 协议，完美适配 Claude Desktop 等支持 MCP 的客户端
- **⚡ 实时响应**：使用 SSE (Server-Sent Events) 流式传输，操作反馈即时可见

## 🚀 快速开始

### 安装步骤

```
# 1. 克隆仓库
git clone https://github.com/Ouniel/Obsidian-mcp-manager.git

# 2. 进入项目目录
cd Obsidian-mcp-manager

# 3. 安装依赖 (建议使用 uv 或 pip)
pip install mcp

# 4. 验证运行 (测试启动)
python obsidian_mcp.py
# 输出: 启动 Obsidian Optimizer MCP Server... (监听 SSE)
```

### 客户端配置 (Claude Desktop)

要让 Claude 使用此工具，请修改配置文件：

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```
{
  "mcpServers": {
    "obsidian-manager": {
      "command": "python",
      "args": [
        "绝对路径/path/to/Obsidian-mcp-manager/obsidian_mcp.py"
      ]
    }
  }
}
```

## 🛠️ 内置指令 (Prompts)

项目内置了经过调优的 System Prompts，连接后可直接调用，无需手动输入复杂指令。

### 1. 单文件优化专家

| **指令名称** | **obsidian_tagging_expert**                                  |
| ------------ | ------------------------------------------------------------ |
| **功能**     | 读取指定笔记 -> 内存中进行格式清洗与标签生成 -> 覆盖写入     |
| **适用场景** | 处理杂乱的 Markdown 笔记，补充缺失的 Metadata                |
| **调用示例** | *"请使用 obsidian_tagging_expert 优化这篇笔记：C:\MyVault\CTF\Writeup.md"* |

### 2. 文件夹架构师

| **指令名称** | **obsidian_folder_architect**                                |
| ------------ | ------------------------------------------------------------ |
| **功能**     | 扫描目录树 -> 审计混乱结构 -> 设计新架构 -> 自动移动文件     |
| **适用场景** | 整理 Inbox 文件夹，或重构整个知识库的目录分类                |
| **调用示例** | *"请使用 obsidian_folder_architect 帮我重构 'Inbox' 目录，按 PARA 方法分类"* |

## 🔧 技术特性

### MCP 协议实现

- **FastMCP**: 基于 `mcp.server.fastmcp` 构建，轻量高效
- **SSE Transport**: 使用 Server-Sent Events 进行流式通信
- **Prompt Resource**: 利用 `@mcp.prompt` 装饰器将业务逻辑固化在代码中

### 文件操作安全

- **原子化读取**: 使用 UTF-8 编码安全读取文件内容
- **全量写入验证**: `update_note_content` 强制要求覆盖全量内容，防止截断
- **智能移动**: `move_file` 自动处理目标文件夹不存在的情况，使用 `shutil` 确保移动原子性

## 📊 使用示例

### 场景一：整理一篇杂乱的 CTF 笔记

**用户输入：**

> "这篇 `misc_writeup.md` 格式太乱了，帮我整理一下。"

**AI 执行流：**

1. 读取笔记内容。
2. **思考**：识别出这是关于 "隐写术" 的内容，且标题层级混乱。
3. **优化**：调整 `#` 标题，添加代码块，生成 Tags: `['隐写术', 'CTF', 'Python']`。
4. **写入**：调用 `update_note_content` 更新文件。

### 场景二：重构知识库目录

**用户输入：**

> "我的 `Unsorted` 文件夹里堆了100个文件，帮我按领域分类整理。"

**AI 执行流：**

1. 调用 `list_directory_structure` 扫描文件列表。
2. **思考**：发现有 Python 脚本、Docker 配置和 读书笔记。
3. **规划**：设计目录结构 `Dev/Python`, `Dev/Ops`, `Reading/Notes`。
4. **执行**：循环调用 `move_file` 将文件移动到新目录。

## 📌 注意事项

### 数据安全

- **备份建议**：虽然工具包含防丢失逻辑，但涉及批量文件移动和重写时，**强烈建议先对 Obsidian 仓库进行 Git 提交或备份**。
- **冲突处理**：如果目标路径已存在同名文件，移动操作会自动失败并报错，以保护现有文件。

### 运行环境

- **Python环境**：建议使用虚拟环境运行，避免依赖冲突。
- **路径格式**：在 Windows 上建议使用双反斜杠 `\\` 或正斜杠 `/` 来指定路径。

## ⚠️ 免责声明

**使用本工具前请务必阅读并同意以下条款：**

1. **数据备份**：本工具会对本地文件进行物理修改（写入/移动），作者不承担因操作失误导致的数据丢失责任。
2. **隐私安全**：工具仅在本地运行，通过 MCP 协议与你授权的 AI 客户端交互，不会私自上传文件内容。
3. **使用范围**：请仅在你有权操作的文件目录下使用本工具。

## 🤝 项目结构

```
Obsidian-mcp-manager/
├── obsidian_mcp.py        # 核心 MCP 服务端代码
├── requirements.txt       # 项目依赖
└── README.md              # 项目说明文档
```

**让知识库管理自动化** - 释放你的第二大脑 🧠
