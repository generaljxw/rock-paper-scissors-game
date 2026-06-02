# 🎮 猜拳小游戏 - 本地开发环境配置指南

**项目**: 儿童猜拳小游戏
**版本**: v1.0.0
**日期**: 2026-06-01
**状态**: 基线版本
**作者**: Planner架构师
**审批人**: 待确认

---

## 📋 版本控制记录

| 版本号 | 修订日期 | 修订人 | 修订内容摘要 | 审批状态 |
|--------|----------|--------|--------------|----------|
| v1.0.0 | 2026-06-01 | Planner架构师 | 初始版本，编写开发环境配置指南 | 已审批 |

---

## 📋 环境要求

### 必需环境

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| Python | 3.11.x | 推荐 3.11.9 |
| pip | 最新版 | Python包管理器 |
| Git | 任意版本 | 代码版本控制 |

### 可选工具

| 工具 | 说明 |
|------|------|
| PyCharm / VS Code | IDE推荐 |
| GitHub Desktop | Git图形化客户端 |

---

## 🚀 快速开始（Windows）

### 第一步：安装Python 3.11

1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.11.9
3. 运行安装程序
4. **重要**：勾选 "Add Python to PATH"
5. 点击 "Install Now"

### 第二步：验证Python安装

打开命令提示符（CMD），输入：

```cmd
python --version
```

应显示：`Python 3.11.9`

### 第三步：克隆项目

```cmd
git clone <项目仓库地址>
cd RockPaperScissors
```

### 第四步：运行初始化脚本

```cmd
setup.bat
```

脚本将自动：
- 创建虚拟环境（venv）
- 激活虚拟环境
- 安装所有依赖

### 第五步：启动游戏

```cmd
venv\Scripts\activate.bat
python src\main.py
```

---

## 🚀 快速开始（Linux/macOS）

### 第一步：安装Python 3.11

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

**macOS (Homebrew):**
```bash
brew install python@3.11
```

### 第二步：验证Python安装

```bash
python3 --version
```

### 第三步：克隆并初始化项目

```bash
git clone <项目仓库地址>
cd RockPaperScissors
chmod +x setup.sh
./setup.sh
```

### 第四步：启动游戏

```bash
source venv/bin/activate
python src/main.py
```

---

## 📦 依赖说明

### 核心依赖

| 依赖包 | 版本 | 用途 |
|--------|------|------|
| PyQt6 | 6.7.0 | GUI图形界面框架 |
| pytest | 8.1.1 | 单元测试框架 |
| pytest-qt | 4.4.0 | PyQt测试插件 |

### 开发依赖

| 依赖包 | 用途 |
|--------|------|
| black | 代码格式化 |
| flake8 | 代码检查 |
| pylint | 代码质量分析 |
| mypy | 类型检查 |

### 打包依赖

| 依赖包 | 用途 |
|--------|------|
| pyinstaller | 生成免安装exe |

---

## 🧪 测试

### 运行所有测试

```bash
pytest
```

### 运行特定测试

```bash
pytest tests/test_game.py
```

### 生成覆盖率报告

```bash
pytest --cov=src --cov-report=html
```

---

## 🔨 打包发布

### Windows打包

```bash
pyinstaller --onefile --windowed --name="猜拳游戏" src/main.py
```

打包后的exe位于 `dist/` 目录

### GitHub Actions 自动构建

项目已配置 `.github/workflows/build.yml`，每次发布自动构建Windows/macOS/Linux版本。

---

## 🐛 常见问题

### Q: pip install 失败？

```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: PyQt6 安装失败？

PyQt6需要编译工具，确保已安装：

**Windows:** Visual Studio Build Tools
**Ubuntu:** `sudo apt install build-essential`
**macOS:** Xcode Command Line Tools

### Q: 虚拟环境激活失败？

**Windows PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### Q: 打包后exe无法运行？

检查是否有缺失的动态库：
```bash
pyinstaller --onefile --windowed --debug src/main.py
```

---

## 📁 项目结构

```
RockPaperScissors/
├── src/                    # 源代码
│   ├── main.py            # 程序入口
│   ├── ui/                # UI界面
│   ├── game/              # 游戏逻辑
│   └── data/              # 数据层
├── tests/                 # 测试文件
├── dist/                  # 打包输出
├── requirements.txt       # 依赖清单
├── setup.bat             # Windows初始化
├── setup.sh              # Linux/macOS初始化
└── README.md             # 项目说明
```

---

## 📮 技术支持

如遇环境配置问题，请联系项目团队。

---

## 评审签字

| 角色 | 姓名 | 日期 | 签字 |
|------|------|------|------|
| 项目负责人 |  |  |  |
| Planner架构师 | Planner | 2026-06-01 | ✅ |
| Coder开发工程师 |  |  |  |
| Tester测试工程师 |  |  |  |
| Reviewer代码审查 |  |  |  |

---

**文档状态**: ✅ 已审批为基线版本
**基线版本号**: v1.0.0
**基线创建日期**: 2026-06-01
**基线保存位置**: DEVELOPMENT_GUIDE.md (当前版本即为基线)
