# 面向视觉小说的轻量级剧本逻辑可视化与文本校验系统

![Version](https://img.shields.io/badge/Version-2.5-blue)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-brightgreen)

一个专为 **Ren'Py** 视觉小说（VN）开发者设计的轻量级辅助工具，帮助解决剧本逻辑混乱和中英文符号混用两大核心痛点。

---

## 📖 项目简介

本系统针对 Ren'Py 剧本开发中的实际问题，实现了**剧本逻辑可视化**与**文本规范智能校验**功能。系统能够自动解析 `.rpy` 脚本，生成剧情拓扑流向图，并智能检测常见的符号错误、逻辑死链等问题。

**选题背景**：Ren'Py 剧本以纯文本形式编写，分支复杂时极易迷失，且中英文标点混用问题频繁发生。本工具有效提升了开发效率和脚本规范性。

---

## ✨ 核心功能

### 已实现功能
- **脚本导入与编辑**：支持 `.rpy` 文件快速导入，带行号的代码编辑器
- **剧情结构解析**：自动识别 `label`、`jump`、`call`、`menu` 等结构
- **图形化可视化**：生成剧情非线性流向有向拓扑图（节点+连线）
- **多模态文本校验**：
  - 逻辑死链检测（jump 到不存在的 label）
  - 引号残缺与中英混用检测
  - 中英文标点规范检测
  - 孤立节点（不可达剧情）检测
- **剧情复杂度分析**（亮点功能）：
  - Ending 类型与数量统计
  - 角色台词占比分析（支持中文显示）
  - 对话密度、剧情复杂度评分等指标

---

## 🛠 技术栈

- **语言**：Python 3.9+
- **GUI 框架**：PyQt5
- **图形可视化**：NetworkX + Matplotlib
- **文本解析**：正则表达式（re）

---

##  安装与运行

### 1. 环境准备
```bash
# 克隆项目（或直接解压）
git clone <仓库地址>
cd VN_Script_Tool
```
### 2. 安装依赖
pip install -r requirements.txt
### 3. 运行
python main.py
```
VN_Script_Tool/
├── main.py                 # 程序入口
├── requirements.txt        # 依赖列表
├── README.md
├── core/                   # 核心逻辑模块
│   ├── __init__.py
│   ├── patterns.py         # 正则规则
│   ├── parser.py           # 脚本解析
│   ├── checker.py          # 文本校验
│   └── analyzer.py         # 剧情复杂度分析
└── ui/
    ├── __init__.py
    └── main_window.py      # 主界面
```