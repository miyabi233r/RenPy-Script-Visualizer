# core/__init__.py

"""
核心模块包
包含脚本解析、正则规则、文本校验等核心逻辑
"""

from .patterns import *
from .parser import ScriptParser
from .checker import ScriptChecker
from .analyzer import StoryAnalyzer   # 新增

__all__ = ['ScriptParser', 'ScriptChecker', 'patterns', 'StoryAnalyzer']
