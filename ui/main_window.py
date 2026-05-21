# ui/main_window.py
import re
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTextEdit,
    QFileDialog, QListWidget, QLabel, QGroupBox, QCheckBox, QMessageBox
)
from PyQt5.QtGui import QColor, QTextFormat

from core.parser import ScriptParser
from core.checker import ScriptChecker


class ScriptTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("面向视觉小说的轻量级剧本逻辑可视化与文本校验系统 v2.0")
        self.resize(1350, 820)

        self.parser = ScriptParser()
        self.checker = ScriptChecker()

        self.init_ui()  # 必须调用！

    def init_ui(self):
        main_layout = QHBoxLayout()

        # ==================== 左侧面板 ====================
        left_panel = QVBoxLayout()

        self.load_btn = QPushButton("📂 导入 Ren'Py 脚本 (.rpy)")
        self.load_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        self.load_btn.clicked.connect(self.load_script)

        self.parse_btn = QPushButton("🗺️ 解析剧情拓扑流向")
        self.parse_btn.clicked.connect(self.parse_script)

        self.check_btn = QPushButton("🔍 执行多模态文本校验")
        self.check_btn.setStyleSheet("background-color: #D9EAD3; font-weight: bold; padding: 8px;")
        self.check_btn.clicked.connect(self.check_text)

        # ==================== 新增：剧情复杂度分析按钮 ====================
        self.analyze_btn = QPushButton("📊 剧情复杂度分析")
        self.analyze_btn.setStyleSheet("background-color: #E3F2FD; font-weight: bold; padding: 8px;")
        self.analyze_btn.clicked.connect(self.analyze_story)
        left_panel.addWidget(self.analyze_btn)

        # 规则配置
        config_box = QGroupBox("⚙️ 审计规则配置")
        cfg_layout = QVBoxLayout()
        self.cfg_dead_link = QCheckBox("启用逻辑死链与孤立节点检测")
        self.cfg_quotes = QCheckBox("启用引号规范检测")
        self.cfg_punc = QCheckBox("启用中英文标点混用检测")

        for cb in (self.cfg_dead_link, self.cfg_quotes, self.cfg_punc):
            cb.setChecked(True)
            cfg_layout.addWidget(cb)

        config_box.setLayout(cfg_layout)

        # 编辑器 + 行号
        editor_layout = QHBoxLayout()
        self.line_number_bar = QTextEdit()
        self.line_number_bar.setReadOnly(True)
        self.line_number_bar.setFixedWidth(50)
        self.line_number_bar.setStyleSheet(
            "background-color: #f5f5f5; color: #666666; font-family: Consolas; border: none;")

        self.editor = QTextEdit()
        self.editor.setStyleSheet("font-family: Consolas; font-size: 14px;")

        self.editor.textChanged.connect(self.update_line_numbers)
        self.editor.verticalScrollBar().valueChanged.connect(
            self.line_number_bar.verticalScrollBar().setValue)

        editor_layout.addWidget(self.line_number_bar)
        editor_layout.addWidget(self.editor)

        # 组装左侧
        left_panel.addWidget(self.load_btn)
        left_panel.addWidget(self.parse_btn)
        left_panel.addWidget(self.check_btn)
        left_panel.addWidget(config_box)
        left_panel.addWidget(QLabel("📝 剧本源码编辑器"))
        left_panel.addLayout(editor_layout)

        # ==================== 右侧面板 ====================
        right_panel = QVBoxLayout()

        # 统计看板
        self.dashboard_box = QGroupBox("📊 剧本拓扑统计看板")
        dash_layout = QHBoxLayout()
        self.lbl_nodes = QLabel("节点: 0")
        self.lbl_jumps = QLabel("跳转: 0")
        self.lbl_menus = QLabel("Menu: 0")
        self.lbl_dialogues = QLabel("对话: 0")

        for lbl in (self.lbl_nodes, self.lbl_jumps, self.lbl_menus, self.lbl_dialogues):
            dash_layout.addWidget(lbl)
        self.dashboard_box.setLayout(dash_layout)

        self.result_list = QListWidget()
        self.result_list.itemDoubleClicked.connect(self.jump_to_line)

        right_panel.addWidget(self.dashboard_box)
        right_panel.addWidget(QLabel("📋 分析与审计结果（双击可跳转定位）"))
        right_panel.addWidget(self.result_list)

        # ==================== 主布局 ====================
        main_layout.addLayout(left_panel, 5)
        main_layout.addLayout(right_panel, 4)

        self.setLayout(main_layout)

    # ====================== 其他方法 ======================
    def update_line_numbers(self):
        text = self.editor.toPlainText()
        lines = text.splitlines() or [""]
        numbers = "\n".join(str(i) for i in range(1, len(lines) + 1))
        self.line_number_bar.setPlainText(numbers)

    def load_script(self):
        path, _ = QFileDialog.getOpenFileName(self, "打开 Ren'Py 脚本", "", "Ren'Py Script (*.rpy)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.editor.setPlainText(f.read())

    def parse_script(self):
        text = self.editor.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "提示", "请先导入脚本文件")
            return

        stats = self.parser.run_static_dashboard(text)
        self.lbl_nodes.setText(f"节点: {stats['nodes']}")
        self.lbl_jumps.setText(f"跳转: {stats['jumps']}")
        self.lbl_menus.setText(f"Menu: {stats['menus']}")
        self.lbl_dialogues.setText(f"对话: {stats['dialogues']}")

        results = self.parser.parse_script(text)
        self.result_list.clear()
        self.result_list.addItems(results)

    def check_text(self):
        text = self.editor.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "提示", "请先导入脚本文件")
            return

        results, count = self.checker.check_text(
            text,
            self.cfg_dead_link.isChecked(),
            self.cfg_quotes.isChecked(),
            self.cfg_punc.isChecked()
        )
        self.result_list.clear()
        self.result_list.addItems(results)

        if count == 0:
            QMessageBox.information(self, "校验完成", "🎉 未发现规范或逻辑问题！")

    def analyze_story(self):
        """剧情复杂度分析"""
        text = self.editor.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "提示", "请先导入 Ren'Py 脚本")
            return

        from core.analyzer import StoryAnalyzer
        analyzer = StoryAnalyzer()
        results = analyzer.analyze(text)

        self.result_list.clear()  # 假设你有 result_list
        self.result_list.addItems(results)

        QMessageBox.information(self, "分析完成", "剧情复杂度分析报告已生成！")

    def jump_to_line(self, item):
        if not item:
            return
        item_text = item.text()
        match = re.search(r'第\s*(\d+)\s*行', item_text)
        if match:
            try:
                line_num = int(match.group(1)) - 1
                self.execute_ui_jump(line_num)
            except:
                pass

    def execute_ui_jump(self, line_num: int):
        doc = self.editor.document()
        if line_num < 0 or line_num >= doc.blockCount():
            return

        target_block = doc.findBlockByLineNumber(line_num)
        cursor = self.editor.textCursor()
        cursor.setPosition(target_block.position())
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

        # 高亮
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(QColor("#FFF2CC"))
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = cursor

        self.editor.setExtraSelections([selection])
        self.editor.ensureCursorVisible()