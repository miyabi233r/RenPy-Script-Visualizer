# core/patterns.py
import re

# ==================== 正则规则集中管理 ====================
LABEL_PATTERN = r'^\s*label\s+(\w+)\s*:'
JUMP_PATTERN = r'^\s*jump\s+(\w+)'
CALL_PATTERN = r'^\s*call\s+(\w+)'
MENU_PATTERN = r'^\s*menu\s*:'

# Menu 选项（"选项内容": 或 "选项内容" if ...）
MENU_OPTION_PATTERN = r'^\s*["“](.+?)["”]\s*(?:if|:)'

# 对话文本提取
DIALOGUE_PATTERN = r'["“](.+?)["”]'

__all__ = [
    'LABEL_PATTERN', 'JUMP_PATTERN', 'CALL_PATTERN', 'MENU_PATTERN',
    'MENU_OPTION_PATTERN', 'DIALOGUE_PATTERN'
]