# Multi-Agent 开发团队系统

基于 LangChain Agents 的多代理协作开发框架，支持与多个AI Agent进行并行对话和任务协作。

## 🎯 功能特性

- **4个专业Agent**: Planner（架构师）、Coder（工程师）、Tester（测试师）、Reviewer（审查员）
- **Agent间通信**: 支持消息传递和广播机制
- **任务管理**: 内置任务创建、分配和状态跟踪
- **对话历史**: 自动记录所有Agent对话
- **完整迭代**: 支持一键运行完整的开发迭代

## 📁 项目结构

```
multi_agents/
├── agents/                 # Agent定义
│   ├── __init__.py
│   ├── planner_agent.py    # 架构师Agent
│   ├── coder_agent.py      # 工程师Agent
│   ├── tester_agent.py     # 测试师Agent
│   └── reviewer_agent.py   # 审查员Agent
├── prompts/                # Agent角色定义
│   ├── planner.md
│   ├── coder.md
│   ├── tester.md
│   └── reviewer.md
├── tools/                  # 工具函数
├── __init__.py
├── coordinator.py          # Agent协调器
└── main.py                 # 程序入口
```

## 🚀 快速开始

### 1. 环境配置

```bash
cd c:\Code\TRAE\RockPaperScissors\multi_agents
pip install -r requirements.txt
```

### 2. 配置API Key

复制 `.env.example` 为 `.env`，并填入你的 OpenAI API Key：

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4
```

### 3. 运行程序

```bash
python main.py
```

## 📝 使用方式

### 交互模式

运行后可以看到主菜单：

```
请选择要交互的Agent或输入问题：
  [planner] - 与架构师讨论需求
  [coder]   - 与工程师讨论实现
  [tester]  - 与测试师讨论测试
  [reviewer]- 与审查员讨论代码
  [team]    - 启动完整迭代
```

### 与特定Agent对话

**与Planner讨论需求：**
```
请输入选项或直接描述问题: planner
已连接 [PLANNER]
请输入您的问题: 我想添加一个难度选择功能，应该如何设计？
```

**与Coder讨论实现：**
```
请输入选项或直接描述问题: coder
已连接 [CODER]
请输入您的问题: 如何实现难度选择中的AI策略？
```

**与Tester讨论测试：**
```
请输入选项或直接描述问题: tester
已连接 [TESTER]
请输入您的问题: 难度选择功能应该测试哪些场景？
```

**与Reviewer讨论代码质量：**
```
请输入选项或直接描述问题: reviewer
已连接 [REVIEWER]
请输入您的问题: 这段代码有什么安全问题？
```

### 启动完整迭代

输入 `team` 可以启动完整的开发迭代流程：

```
请输入选项或直接描述问题: team
请输入项目需求描述: 开发一个带有难度选择的猜拳游戏
```

系统会自动：
1. Planner 分析需求并设计架构
2. Coder 实现功能
3. Tester 编写测试用例
4. Reviewer 审查代码

## 🔧 API使用示例

```python
from multi_agents import AgentCoordinator, AgentType

coordinator = AgentCoordinator()

# 与Planner讨论需求
response = coordinator.discuss_feature_with_planner(
    "添加一个玩家历史排行榜功能"
)

# 与Coder讨论实现方案
response = coordinator.discuss_with_coder(
    "如何实现排行榜的排序？",
    "使用JavaScript实现"
)

# 与Tester讨论测试策略
response = coordinator.discuss_with_tester(
    "排行榜测试用例设计",
    "需要测试排序、重复分数等场景"
)

# 与Reviewer讨论代码质量
response = coordinator.discuss_with_reviewer(
    "这段代码的性能如何？",
    "代码片段..."
)

# 导出对话历史
coordinator.export_conversation("conversation.json")
```

## 📋 Agent职责说明

| Agent | 职责 | 核心能力 |
|-------|------|----------|
| **Planner** | 需求分析、架构设计 | 需求澄清、技术选型、任务分解 |
| **Coder** | 代码实现 | 前端/后端开发、性能优化 |
| **Tester** | 测试验证 | 测试用例设计、缺陷报告 |
| **Reviewer** | 代码审查 | 安全检查、质量评估、重构建议 |

## ⚙️ 配置选项

环境变量配置文件 `.env`：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `OPENAI_API_KEY` | OpenAI API Key | 必填 |
| `OPENAI_MODEL` | 使用的模型 | gpt-4 |
| `OPENAI_TEMPERATURE` | 生成温度 | 0.7 |
| `AGENT_VERBOSE` | 详细输出 | true |
| `PROJECT_ROOT` | 项目根目录 | 当前目录 |

## 🔄 典型工作流程

```
1. 需求提出
   ↓
2. Planner 分析需求 → 输出技术规范
   ↓
3. Coder 实现功能 ←→ Tester 编写测试
   ↓
4. Reviewer 审查代码
   ↓
5. 根据审查意见修复 → 重新审查
   ↓
6. 完成迭代 → 进入下一轮迭代
```

## 🐛 故障排除

**问题：ImportError**
```bash
pip install -r requirements.txt
```

**问题：API Key错误**
检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确

**问题：模型响应慢**
可以尝试切换到 `gpt-3.5-turbo` 模型

## 📄 许可证

MIT License
