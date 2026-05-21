import re
from .patterns import (
    LABEL_PATTERN, JUMP_PATTERN, CALL_PATTERN,
    MENU_OPTION_PATTERN, DIALOGUE_PATTERN
)


class ScriptParser:
    def __init__(self):
        pass

    def run_static_dashboard(self, text: str):
        """返回剧本统计数据"""
        lines = text.splitlines()
        c_label = c_jump = c_menu_option = c_dialogue = 0
        keywords = ("label", "jump", "call", "menu", "scene", "show", "hide", "play", "stop", "$", "return")

        for line in lines:
            clean = line.strip()
            if not clean or clean.startswith("#"):
                continue
            if re.search(LABEL_PATTERN, clean):
                c_label += 1
            if re.search(JUMP_PATTERN, clean):
                c_jump += 1
            if re.search(MENU_OPTION_PATTERN, clean):
                c_menu_option += 1
            if re.search(DIALOGUE_PATTERN, clean):
                if not re.search(MENU_OPTION_PATTERN, clean) and not any(clean.startswith(k) for k in keywords):
                    c_dialogue += 1

        return {
            "nodes": c_label,
            "jumps": c_jump,
            "menus": c_menu_option,
            "dialogues": c_dialogue
        }

    def parse_script(self, text: str):
        """
        深度解析：不仅生成文本日志，还提取网络拓扑流向关系
        返回: (results_text_list, graph_edges_list, all_nodes_set)
        """
        lines = text.splitlines()
        results = ["=== 🗺️ 剧情拓扑流向分析 ==="]

        edges = []  # 存放 (源节点, 目标节点) 的元组，用于绘制流程有向图
        all_labels = set()  # 记录剧本中出现的所有物理 label
        current_label = "start"  # 缺省初始悬挂节点

        for index, line in enumerate(lines):
            clean = line.strip()
            if not clean or clean.startswith("#"):
                continue

            label_match = re.search(LABEL_PATTERN, clean)
            jump_match = re.search(JUMP_PATTERN, clean)
            call_match = re.search(CALL_PATTERN, clean)
            menu_match = re.search(MENU_OPTION_PATTERN, clean)
            dialogue_match = re.search(DIALOGUE_PATTERN, clean)

            if label_match:
                current_label = label_match.group(1)
                all_labels.add(current_label)
                results.append(f"📍 [节点] 第 {index + 1} 行 -> label: {current_label}")

            if jump_match:
                target_node = jump_match.group(1)
                edges.append((current_label, target_node))  # 捕获一条逻辑流向边
                results.append(f"    └── ✈️ [连线] 第 {index + 1} 行 -> jump to: {target_node}")

            if call_match:
                target_node = call_match.group(1)
                edges.append((current_label, f"call_{target_node}"))
                results.append(f"    └── 📞 [子流程] 第 {index + 1} 行 -> call: {target_node}")

            if menu_match:
                results.append(f"    └── 🔀 [Menu选项] 第 {index + 1} 行 -> {menu_match.group(1)}")

            if dialogue_match and not menu_match:
                preview = dialogue_match.group(1)[:25] + "..." if len(
                    dialogue_match.group(1)) > 25 else dialogue_match.group(1)
                results.append(f"💬 [对话] 第 {index + 1} 行 -> {preview}")

        return results, edges, all_labels