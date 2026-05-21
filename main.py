import sys
import os

# --- 绝对路径硬核修复代码 ---
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = r"C:\Users\26779\.conda\envs\PyQt-py39\Library\plugins"
# ----------------------------

import re
import networkx as nx
import matplotlib

matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QFileDialog, QListWidget,
    QLabel, QGroupBox, QCheckBox, QSplitter, QTabWidget, QGraphicsView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QTextFormat, QPainter

# 🌟 完美引入所有的后端类，包括我们手写的交互画布
from core.editor_canvas import NodeEditorScene, NodeItem
from core.parser import ScriptParser
from core.checker import ScriptChecker
from core.analyzer import StoryAnalyzer


class ScriptTool(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("面向视觉小说叙事结构的轻量级静态分析与可视化编辑系统 v3.0")
        self.resize(1650, 900)

        # 实例化所有的后端类
        self.parser = ScriptParser()
        self.checker = ScriptChecker()
        self.analyzer = StoryAnalyzer()

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # =============================================================
        # 左侧面板：脚本控制、规则配置与编辑器（你原有的所有核心功能按钮）
        # =============================================================
        left_panel = QVBoxLayout()

        self.load_btn = QPushButton("📂 导入 Ren'Py 脚本 (.rpy)")
        self.load_btn.setStyleSheet("font-weight: bold; padding: 6px;")
        self.load_btn.clicked.connect(self.load_script)

        self.parse_btn = QPushButton("🗺️ 运行结构解析与图形可视化")
        self.parse_btn.setStyleSheet("background-color: #CFE2F3; font-weight: bold;")
        self.parse_btn.clicked.connect(self.parse_and_visualize)

        self.check_btn = QPushButton("🔍 执行多模态文本校验")
        self.check_btn.setStyleSheet("background-color: #D9EAD3; font-weight: bold;")
        self.check_btn.clicked.connect(self.run_text_audit)

        self.analyze_btn = QPushButton("📊 运行剧本复杂度深度分析")
        self.analyze_btn.setStyleSheet("background-color: #FCE5CD; font-weight: bold; color: #B45F06;")
        self.analyze_btn.clicked.connect(self.run_complexity_analysis)

        # 🚀 节点工厂快速控制（为右侧连线画布提供支持）
        factory_box = QGroupBox("🛠️ 可视化拓扑节点工厂（高级编辑模式使用）")
        factory_layout = QHBoxLayout()
        self.btn_add_label = QPushButton("📍 新增 Label 节点")
        self.btn_add_label.setStyleSheet("background-color: #526D82; color: white; font-weight: bold;")
        self.btn_add_label.clicked.connect(lambda: self.create_node_on_canvas("label"))
        self.btn_add_menu = QPushButton("🔀 新增 Menu 节点")
        self.btn_add_menu.setStyleSheet("background-color: #D35400; color: white; font-weight: bold;")
        self.btn_add_menu.clicked.connect(lambda: self.create_node_on_canvas("menu"))
        factory_layout.addWidget(self.btn_add_label)
        factory_layout.addWidget(self.btn_add_menu)
        factory_box.setLayout(factory_layout)

        # 审计规则库
        config_box = QGroupBox("⚙️ 审计规则库动态配置")
        config_layout = QVBoxLayout()
        self.cfg_dead_link = QCheckBox("启用逻辑死链与孤立节点检测")
        self.cfg_dead_link.setChecked(True)
        config_layout.addWidget(self.cfg_dead_link)
        config_box.setLayout(config_layout)

        # 编辑器联动
        editor_layout = QHBoxLayout()
        self.line_number_bar = QTextEdit()
        self.line_number_bar.setReadOnly(True)
        self.line_number_bar.setFixedWidth(45)
        self.line_number_bar.setStyleSheet("background-color: #f5f5f5; color: #999999; font-family: Consolas;")

        self.editor = QTextEdit()
        self.editor.setStyleSheet("font-family: Consolas; font-size: 14px;")
        editor_layout.addWidget(self.line_number_bar)
        editor_layout.addWidget(self.editor)

        # 反向生成代码按钮
        self.btn_compile = QPushButton("⚡ 从实体编辑器拓扑图反向更新剧本代码")
        self.btn_compile.setStyleSheet("background-color: #27AE60; color: white; font-weight: bold; padding: 6px;")
        self.btn_compile.clicked.connect(self.generate_code_from_graph)

        # 按顺序组装左侧
        left_panel.addWidget(self.load_btn)
        left_panel.addWidget(self.parse_btn)
        left_panel.addWidget(self.check_btn)
        left_panel.addWidget(self.analyze_btn)
        left_panel.addWidget(factory_box)
        left_panel.addWidget(config_box)
        left_panel.addWidget(QLabel("📝 剧本源码编辑器"))
        left_panel.addLayout(editor_layout)
        left_panel.addWidget(self.btn_compile)

        # =============================================================
        # 右侧面板：原功能与新拖拽连线画布的完美整合区
        # =============================================================
        right_panel = QVBoxLayout()

        # 1. 顶部定量分析看板保持原样
        self.dashboard_box = QGroupBox("📊 剧本静态拓扑定量分析看板")
        dash_layout = QHBoxLayout()
        self.lbl_nodes = QLabel("剧情节点: 0")
        self.lbl_jumps = QLabel("跳转连线: 0")
        dash_layout.addWidget(self.lbl_nodes)
        dash_layout.addWidget(self.lbl_jumps)
        self.dashboard_box.setLayout(dash_layout)
        right_panel.addWidget(self.dashboard_box)

        # 2. 核心大改造：使用分页标签卡 QTabWidget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabBar::tab { font-weight: bold; padding: 8px 16px; }")

        # ---- 标签页 1：你原来的老功能（日志列表 + Matplotlib 只读静态图）----
        tab1_widget = QWidget()
        tab1_layout = QVBoxLayout(tab1_widget)

        splitter = QSplitter(Qt.Vertical)
        self.result_list = QListWidget()  # 存放你多模态和复杂度的分析文本
        splitter.addWidget(self.result_list)

        self.graph_box = QGroupBox("🌐 剧本非线性流向有向拓扑图 (静态分析)")
        graph_layout = QVBoxLayout()
        self.figure, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        graph_layout.addWidget(self.canvas)
        self.graph_box.setLayout(graph_layout)
        splitter.addWidget(self.graph_box)

        tab1_layout.addWidget(splitter)
        self.tab_widget.addTab(tab1_widget, "📊 静态审计与只读图谱")

        # ---- 标签页 2：全新的可视化拖拽节点编辑器 ----
        tab2_widget = QWidget()
        tab2_layout = QVBoxLayout(tab2_widget)

        self.scene = NodeEditorScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.view.setStyleSheet("background-color: #FDFEFE;")

        # 预先在画布上丢几个默认引导节点
        start_node = NodeItem("start", "label")
        start_node.setPos(100, 150)
        self.scene.addItem(start_node)

        tab2_layout.addWidget(self.view)
        self.tab_widget.addTab(tab2_widget, "🕹️ 交互式有向节点编辑器 (高级模式)")

        right_panel.addWidget(self.tab_widget)

        # 组装主架构布局
        main_layout.addLayout(left_panel, 4)
        main_layout.addLayout(right_panel, 5)
        self.setLayout(main_layout)

    # =============================================================
    # 后端算法驱动与核心槽函数（原封不动保留，并无缝融合新功能）
    # =============================================================
    def load_script(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "打开 Ren'Py 脚本", "", "Ren'Py Script (*.rpy)")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.editor.setPlainText(content)
            stats = self.parser.run_static_dashboard(content)
            self.lbl_nodes.setText(f"剧情节点: {stats['nodes']}")
            self.lbl_jumps.setText(f"跳转连线: {stats['jumps']}")

    def run_text_audit(self):
        """调用 core/checker.py 驱动多模态文本校验 pipeline"""
        self.tab_widget.setCurrentIndex(0)  # 自动切回第一个标签卡查看日志
        text = self.editor.toPlainText()
        if not text.strip():
            self.result_list.clear()
            self.result_list.addItem("❌ 错误：当前编辑器内没有检测到剧本源码。")
            return
        self.result_list.clear()
        is_dead_link_enabled = self.cfg_dead_link.isChecked()
        results, error_count = self.checker.check_text(text, is_dead_link_enabled, True, True)
        for log_entry in results:
            self.result_list.addItem(log_entry)

    def run_complexity_analysis(self):
        """调用 core/analyzer.py 对编辑器内容进行复杂度计算并呈现在右侧"""
        self.tab_widget.setCurrentIndex(0)  # 自动切回第一个标签卡查看日志
        text = self.editor.toPlainText()
        if not text.strip():
            self.result_list.clear()
            self.result_list.addItem("❌ 错误：当前编辑器内没有检测到剧本源码。")
            return
        self.result_list.clear()
        report_logs = self.analyzer.analyze(text)
        for line in report_logs:
            self.result_list.addItem(line)

    def parse_and_visualize(self):
        """执行脚本拓扑解析，并同步调用图论引擎渲染有向拓扑分支图"""
        self.tab_widget.setCurrentIndex(0)  # 自动切回第一个标签卡查看画面
        text = self.editor.toPlainText()
        if not text.strip():
            return
        self.result_list.clear()
        results, edges, all_labels = self.parser.parse_script(text)
        for item in results:
            self.result_list.addItem(item)

        self.ax.clear()
        if not edges and not all_labels:
            self.canvas.draw()
            return

        G = nx.DiGraph()
        for node in all_labels: G.add_node(node)
        for u, v in edges: G.add_edge(u, v)

        pos = nx.spring_layout(G, seed=42, k=0.3)
        node_colors = []
        for node in G.nodes:
            if node.startswith("call_"):
                node_colors.append("#FFE599")
            elif node not in all_labels and node != "goodend":
                node_colors.append("#F4CCCC")
            else:
                node_colors.append("#C9DAF8")

        nx.draw_networkx_nodes(G, pos, ax=self.ax, node_color=node_colors, node_size=1200, edgecolors="#666666")
        nx.draw_networkx_edges(G, pos, ax=self.ax, edgelist=edges, arrowstyle="->", arrowsize=15, edge_color="#888888",
                               width=1.5)
        nx.draw_networkx_labels(G, pos, ax=self.ax, font_size=9, font_family="sans-serif", font_weight="bold")
        self.ax.set_title("Ren'Py Storyline Topology Flow", fontsize=10, color="#333333", weight="bold")
        self.ax.axis("off")
        self.figure.tight_layout()
        self.canvas.draw()

    # ---- 交互式画布专属驱动槽函数 ----
    def create_node_on_canvas(self, node_type):
        self.tab_widget.setCurrentIndex(1)  # 自动切换到画布模式
        from PyQt5.QtWidgets import QInputDialog
        title, ok = QInputDialog.getText(self, "生成节点", f"请输入该 {node_type} 的逻辑标示符名称:")
        if ok and title.strip():
            node = NodeItem(title.strip(), node_type)
            node.setPos(200, 200)
            self.scene.addItem(node)

    def generate_code_from_graph(self):
        """图论反向静态重构：精确提取图形节点与多分支连线，反向编译出标准的 Ren'Py 语法代码"""
        generated_code = []

        # 分离提取场景中所有的 label 节点与 menu 节点
        all_items = self.scene.items()
        labels_nodes = [item for item in all_items if isinstance(item, NodeItem) and item.node_type == "label"]
        menu_nodes = [item for item in all_items if isinstance(item, NodeItem) and item.node_type == "menu"]

        # 1. 优先编排所有的静态 label 块
        for item in labels_nodes:
            generated_code.append(f"label {item.title}:")

            # 检查这个 label 后面有没有拉出去的连线
            if item.output_port.edges:
                for edge in item.output_port.edges:
                    if edge.sink_port and edge.sink_port.parent_node:
                        target = edge.sink_port.parent_node
                        # 高级联动：如果直接连到了一个 menu 节点，说明接下来要触发分支选择
                        if target.node_type == "menu":
                            generated_code.append(f"    jump menu_{target.title}")
                        else:
                            generated_code.append(f"    jump {target.title}")
            else:
                generated_code.append("    pass\n")
            generated_code.append("")  # 空行格开

        # 2. 核心补齐：优雅编译 menu 分支树，彻底杜绝闪退
        for item in menu_nodes:
            generated_code.append(f"label menu_{item.title}:")
            generated_code.append("    menu:")

            # 遍历 menu 节点的多个物理输出端口（选项 A / 选项 B）
            for port in item.output_ports:
                opt_label = getattr(port, "option_text", "未知分支")
                generated_code.append(f'        "{opt_label}":')

                # 检查该选项是否牵出了逻辑纽带（连线）
                if port.edges:
                    for edge in port.edges:
                        if edge.sink_port and edge.sink_port.parent_node:
                            dest_title = edge.sink_port.parent_node.title
                            generated_code.append(f"            jump {dest_title}")
                else:
                    generated_code.append("            pass")
            generated_code.append("")  # 空行隔开

        # 更新到左侧编辑器镜像中
        self.editor.setPlainText("\n".join(generated_code))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScriptTool()
    window.show()
    sys.exit(app.exec_())