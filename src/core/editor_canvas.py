import sys
from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsItem,
    QGraphicsPathItem, QInputDialog
)
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QPen, QBrush, QTransform


class PortItem(QGraphicsItem):
    """节点连接端口（左边蓝色为输入，右边橙色为输出）"""

    def __init__(self, is_output=True, parent=None):
        super().__init__(parent)
        self.is_output = is_output
        self.parent_node = parent
        self.edges = []
        self.radius = 6
        self.option_text = None
        self.setAcceptHoverEvents(True)

    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, self.radius * 2, self.radius * 2)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        # 出口用橙色，入口用蓝色
        color = QColor("#E67E22") if self.is_output else QColor("#3498DB")
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor("#FFFFFF"), 1.5))
        painter.drawEllipse(-self.radius, -self.radius, self.radius * 2, self.radius * 2)


class EdgeItem(QGraphicsPathItem):
    """有向连线（带箭头贝塞尔曲线）"""

    def __init__(self, source_port, sink_port=None):
        super().__init__()
        self.source_port = source_port
        self.sink_port = sink_port
        self.setPen(QPen(QColor("#7F8C8D"), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.setZValue(-1)

    def update_path(self, target_pos=None):
        try:
            path = QPainterPath()
            p1 = self.source_port.scenePos()
            p2 = self.sink_port.scenePos() if self.sink_port else target_pos

            if not p2:
                return

            dx = abs(p2.x() - p1.x()) * 0.5
            cp1 = QPointF(p1.x() + dx, p1.y())
            cp2 = QPointF(p2.x() - dx, p2.y())

            path.moveTo(p1)
            path.cubicTo(cp1, cp2, p2)

            if self.sink_port:
                path.addEllipse(p2, 3, 3)

            self.setPath(path)
        except Exception as e:
            pass


class NodeItem(QGraphicsItem):
    """实体剧本流节点（Label / Menu）"""

    def __init__(self, title="Label", node_type="label"):
        super().__init__()
        self.title = title
        self.node_type = node_type
        self.width = 180
        self.height = 110 if node_type == "menu" else 80

        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

        # 1. 剧情流入口（左侧蓝色）
        self.input_port = PortItem(is_output=False, parent=self)
        self.input_port.setPos(0, 40)

        # 2. 动态构建出口（右侧橙色）
        self.output_ports = []
        if self.node_type == "menu":
            opt1_port = PortItem(is_output=True, parent=self)
            opt1_port.setPos(self.width, 55)
            opt1_port.option_text = "选项 A"

            opt2_port = PortItem(is_output=True, parent=self)
            opt2_port.setPos(self.width, 85)
            opt2_port.option_text = "选项 B"

            self.output_ports.extend([opt1_port, opt2_port])
        else:
            standard_port = PortItem(is_output=True, parent=self)
            standard_port.setPos(self.width, 40)
            standard_port.option_text = None
            self.output_ports.append(standard_port)

        self.output_port = self.output_ports[0]

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        if self.node_type == "label":
            base_color = QColor("#DDE6ED")
            header_color = QColor("#526D82")
        elif self.node_type == "menu":
            base_color = QColor("#FCF0E4")
            header_color = QColor("#D35400")
        else:
            base_color = QColor("#EAF2F8")
            header_color = QColor("#2980B9")

        painter.setBrush(QBrush(base_color))
        painter.setPen(
            QPen(QColor("#B2BABB") if not self.isSelected() else QColor("#E74C3C"), 2 if self.isSelected() else 1))
        painter.drawRoundedRect(0, 0, self.width, self.height, 8, 8)

        painter.setBrush(QBrush(header_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(QRectF(0, 0, self.width, 24), 8, 8)
        painter.drawRect(0, 16, self.width, 8)

        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(10, 16, f"📍 {self.node_type.upper()}")

        painter.setPen(QColor("#2C3E50"))
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(10, 42, self.title)

        if self.node_type == "menu":
            font.setBold(False)
            font.setPointSize(9)
            painter.setFont(font)
            painter.setPen(QColor("#7F8C8D"))
            txt_a = self.output_ports[0].option_text if len(self.output_ports) > 0 else "选项 A"
            txt_b = self.output_ports[1].option_text if len(self.output_ports) > 1 else "选项 B"
            painter.drawText(15, 60, f"⌥ {txt_a} ->")
            painter.drawText(15, 90, f"⌥ {txt_b} ->")

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.input_port.edges:
            for edge in self.input_port.edges: edge.update_path()
        for port in self.output_ports:
            if port.edges:
                for edge in port.edges: edge.update_path()

    def mouseDoubleClickEvent(self, event):
        new_title, ok = QInputDialog.getText(None, "修改节点属性", "请输入新的节点逻辑标识符:", text=self.title)
        if ok and new_title.strip():
            self.title = new_title.strip()
            if self.node_type == "menu":
                opt_a, ok1 = QInputDialog.getText(None, "修改分支 A", "修改选项 A 的对话文本:",
                                                  text=self.output_ports[0].option_text)
                if ok1 and opt_a.strip(): self.output_ports[0].option_text = opt_a.strip()
                opt_b, ok2 = QInputDialog.getText(None, "修改分支 B", "修改选项 B 的对话文本:",
                                                  text=self.output_ports[1].option_text)
                if ok2 and opt_b.strip(): self.output_ports[1].option_text = opt_b.strip()
            self.update()


class NodeEditorScene(QGraphicsScene):
    """节点编辑器画布场景"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 3000, 3000)
        self.current_edge = None

    def drawBackground(self, painter, rect):
        painter.setPen(QPen(QColor("#EAEAEA"), 1))
        left = int(rect.left()) - (int(rect.left()) % 20)
        top = int(rect.top()) - (int(rect.top()) % 20)
        for x in range(left, int(rect.right()), 20):
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
        for y in range(top, int(rect.bottom()), 20):
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)

    def mousePressEvent(self, event):
        """🎯 核心重写：精准捕获右侧橙色输出圆点"""
        try:
            # 拿到鼠标点击位置下的所有图形项
            click_items = self.items(event.scenePos())
            selected_port = None

            # 遍历检查是否点中了橙色（is_output=True）的连接点
            for item in click_items:
                if isinstance(item, PortItem) and item.is_output:
                    selected_port = item
                    break

            # 如果成功点中输出点，激活拉线模式
            if selected_port:
                self.current_edge = EdgeItem(selected_port)
                self.addItem(self.current_edge)
                self.current_edge.update_path(event.scenePos())
                event.accept()
            else:
                # 否则执行默认事件（比如拖动方块或多选框）
                super().mousePressEvent(event)
        except Exception as e:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        try:
            if self.current_edge:
                self.current_edge.update_path(event.scenePos())
                event.accept()
            else:
                super().mouseMoveEvent(event)
        except Exception as e:
            pass

    def mouseReleaseEvent(self, event):
        """鼠标松开，完成吸附连线"""
        try:
            if self.current_edge:
                release_items = self.items(event.scenePos())
                target_port = None

                # 寻找鼠标松开位置有没有合法的左侧蓝色输入圆点（is_output=False）
                for item in release_items:
                    if isinstance(item, PortItem) and not item.is_output:
                        target_port = item
                        break

                if target_port and target_port.parent_node != self.current_edge.source_port.parent_node:
                    self.current_edge.sink_port = target_port
                    self.current_edge.update_path()

                    if self.current_edge not in self.current_edge.source_port.edges:
                        self.current_edge.source_port.edges.append(self.current_edge)
                    if self.current_edge not in target_port.edges:
                        target_port.edges.append(self.current_edge)
                else:
                    self.removeItem(self.current_edge)

                self.current_edge = None
                event.accept()
            else:
                super().mouseReleaseEvent(event)
        except Exception as e:
            if self.current_edge:
                self.removeItem(self.current_edge)
                self.current_edge = None
            event.accept()