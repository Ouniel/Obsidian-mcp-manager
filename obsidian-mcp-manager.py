import os
import shutil
from mcp.server.fastmcp import FastMCP

# 初始化 MCP 服务
mcp = FastMCP("Obsidian-Optimizer")

# ==========================================
# 1. 内置 Prompt
# ==========================================

@mcp.prompt("obsidian_tagging_expert")
def obsidian_tagging_expert_prompt() -> str:
    """
    [单文件优化] 获取 Obsidian 全文优化与标签生成的专家提示词。
    """
    return """你是一名 Obsidian 笔记软件知识库构建高手，精通 Markdown 格式美化及知识分类。

你的任务是对指定的笔记进行【全量优化】，请严格遵循以下工作流程：

**Step 1: 读取文件**
调用 `read_note_content` 获取目标笔记的原始内容。

**Step 2: 内容美化与标签生成 (由你在内存中处理)**
你不仅要添加标签，还要基于原始内容进行格式优化（**注意：严禁删除原始内容中的任何文本或图片链接**）：
1. **格式美化**：
   - 自动识别文档结构，规范一级标题 (#)、二级标题 (##) 等。
   - 检查并优化段落间距。
   - 为原本属于代码或命令的内容添加 Markdown 代码块 (```)。
2. **增加标签**：
   - 根据笔记内容，在文件头部增加或合并 YAML Frontmatter。
   - 标签规则如下（选取3-4个关键标签，必须带行内注释）：
     ```yaml
     tags:
     - 类型/****
     - 工具链/****
     - 关键特征/****
     - 工具/****
     - 结果/****
     ```

**Step 3: 写入文件**
将经过【格式美化】+【标签添加】后的**完整内容**，调用 `update_note_content` 覆盖写入原文件。
"""

@mcp.prompt("obsidian_folder_architect")
def obsidian_folder_architect_prompt() -> str:
    """
    [目录重构] 获取 Obsidian 文件夹架构重构的专家提示词。
    """
    return """你是一名 Obsidian 知识库架构师，精通信息组织与分类（如 PARA 方法、杜威十进制分类法等）。

你的任务是重构用户的笔记文件夹结构，使其更加清晰、逻辑性更强。

请遵循以下工作流程：

**Step 1: 审计现状**
调用 `list_directory_structure` 获取当前文件夹下的所有文件列表。
仔细分析文件名和当前的目录结构，识别混乱的区域。

**Step 2: 架构设计 (思维链)**
根据文件列表，在脑海中设计一个新的、更合理的文件夹架构。
设计原则：
1. 扁平化与层级化的平衡。
2. 按照领域、项目或状态进行分类。
3. 确保类目互斥且穷尽 (MECE原则)。
4. *如果用户有特定的分类偏好，优先遵循用户的指示。*

**Step 3: 执行重构**
根据你设计的新架构，循环调用 `move_file` 工具将文件移动到新的位置。
注意：
- 如果目标文件夹不存在，`move_file` 工具会自动创建，无需额外操作。
- 确保文件名保持不变，仅修改路径。
- 遇到命名极其模糊的文件，可以暂时跳过或放入 "Inbox/ToSort" 文件夹。
- 每次移动后，简要告知用户进度。
"""

# ==========================================
# 2. 工具定义
# ==========================================

@mcp.tool()
def read_note_content(file_path: str) -> str:
    """
    读取 Obsidian 笔记的内容。
    """
    if not os.path.exists(file_path):
        return f"Error: 文件不存在: {file_path}"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error: 读取文件失败: {str(e)}"

@mcp.tool()
def update_note_content(file_path: str, full_content: str) -> str:
    """
    [危险操作] 将优化后的完整内容（包含 Frontmatter 和正文）覆盖写入文件。
    
    调用此工具前，AI 必须确保：
    1. 已经完整读取了原文件。
    2. 新内容完整包含了原文件的所有正文信息（未丢失图片、文字）。
    3. 已经完成了 Markdown 格式美化（标题、代码块）和 YAML 标签的添加。
    """
    if not os.path.exists(file_path):
        return f"Error: 文件不存在: {file_path}"

    try:
        # 写入全量内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        return f"Success: 已更新文件 {os.path.basename(file_path)} 的全部内容 (格式美化 + 标签)。"
    except Exception as e:
        return f"Error: 写入文件失败: {str(e)}"

@mcp.tool()
def list_directory_structure(root_path: str) -> str:
    """
    递归列出指定目录下的所有文件结构。
    会自动忽略 .git, .obsidian 等隐藏文件夹，只展示笔记和资源文件。
    
    Args:
        root_path: 你的 Obsidian 仓库根目录路径。
    """
    if not os.path.exists(root_path):
        return f"Error: 路径不存在: {root_path}"
    
    structure_lines = []
    # 遍历目录
    for root, dirs, files in os.walk(root_path):
        # 过滤掉隐藏目录 (如 .git, .obsidian)
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        # 计算缩进层级
        rel_path = os.path.relpath(root, root_path)
        if rel_path == '.':
            level = 0
            display_path = os.path.basename(root_path) + "/"
        else:
            level = rel_path.count(os.sep) + 1
            display_path = os.path.basename(root) + "/"
            
        indent = '    ' * level
        structure_lines.append(f"{indent}{display_path}")
        
        sub_indent = '    ' * (level + 1)
        for f in files:
            if not f.startswith('.'):
                structure_lines.append(f"{sub_indent}{f}")
                
    return "\n".join(structure_lines)

@mcp.tool()
def move_file(source_path: str, destination_path: str) -> str:
    """
    将文件从源路径移动到目标路径（支持重构文件夹结构）。
    
    Args:
        source_path: 文件的当前绝对路径。
        destination_path: 文件希望移动到的新绝对路径（包含文件名）。
    
    注意：
    - 如果 destination_path 中的文件夹不存在，会自动创建。
    - 这是一个物理移动操作。
    """
    if not os.path.exists(source_path):
        return f"Error: 源文件不存在: {source_path}"
    
    if os.path.exists(destination_path):
        return f"Error: 目标位置已存在同名文件，跳过移动: {destination_path}"
        
    try:
        # 确保目标文件夹存在
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        # 移动文件
        shutil.move(source_path, destination_path)
        return f"Success: 已移动 {os.path.basename(source_path)} -> {destination_path}"
    except Exception as e:
        return f"Error: 移动文件失败: {str(e)}"

if __name__ == "__main__":
    print("启动 Obsidian Optimizer MCP Server...")
    mcp.run(transport="sse")
