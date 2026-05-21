# core/analyzer.py
import re
from collections import defaultdict


class StoryAnalyzer:
    """剧情复杂度分析器 - 为课程设计增加亮点功能"""

    def __init__(self):
        # 角色显示名称映射（可自行扩展）
        self.character_map = {
            "yan": "颜叙", "han": "韩朔", "st": "旁白",
            "n": "旁白", "player": "玩家", "desk": "旁白",
            # 添加更多角色示例：
            # "lily": "莉莉", "teacher": "老师"
        }

    def analyze(self, text: str):
        """返回完整的复杂度分析结果列表"""
        lines = [line for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]

        report = ["=== 📊 剧情复杂度分析报告 ==="]

        # 1. Ending 数量统计
        endings = self._detect_endings(lines)
        report.append(f"🎯 共检测到 Ending：{sum(endings.values())} 个")
        for etype, count in endings.items():
            report.append(f"   • {etype}：{count} 个")

        # 2. 角色台词占比（最亮眼的功能）
        char_stats = self._analyze_dialogue(lines)
        total_dialogue = sum(char_stats.values())
        report.append(f"\n💬 角色台词占比（共 {total_dialogue} 行对话）：")
        if total_dialogue > 0:
            for char, count in sorted(char_stats.items(), key=lambda x: x[1], reverse=True):
                percent = count / total_dialogue * 100
                report.append(f"   • {char}：{count} 行 ({percent:.1f}%)")
        else:
            report.append("   未检测到有效对话")

        # 3. 其他复杂度指标
        stats = self._get_complexity_stats(lines)
        report.append("\n📈 其他复杂度指标：")
        report.append(f"   • 总 Label 节点数：{stats['labels']}")
        report.append(f"   • 跳转 (jump) 次数：{stats['jumps']}")
        report.append(f"   • 分支 (menu) 数量：{stats['menus']}")
        report.append(f"   • 总有效代码行数：{stats['total_lines']}")
        report.append(f"   • 对话密度：{stats['dialogue_ratio']:.1f}%")
        report.append(f"   • 剧情复杂度评分：{stats['score']}/10 分")

        return report

    def _detect_endings(self, lines):
        endings = defaultdict(int)
        patterns = [
            (r'good|true|happy|perfect', 'Good Ending'),
            (r'bad|fail|over|death', 'Bad Ending'),
            (r'hidden|secret|true_end', 'Hidden/True Ending'),
            (r'normal|common', 'Normal Ending'),
        ]
        for line in lines:
            if re.search(r'^\s*label\s+', line):
                label = re.search(r'^\s*label\s+(\w+)', line)
                if label:
                    name = label.group(1).lower()
                    for pat, etype in patterns:
                        if pat in name:
                            endings[etype] += 1
                            break
                    else:
                        if 'end' in name:
                            endings['普通 Ending'] += 1
        return dict(endings)

    def _analyze_dialogue(self, lines):
        char_count = defaultdict(int)
        for line in lines:
            # 匹配角色说话： yan "台词内容"
            match = re.search(r'^\s*(\w+)\s+["“]', line)
            if match:
                key = match.group(1).lower()
                name = self.character_map.get(key, key.capitalize())
                char_count[name] += 1
            # 纯引号开头的视为旁白
            elif re.search(r'^\s*["“]', line):
                char_count["旁白"] += 1
        return char_count

    def _get_complexity_stats(self, lines):
        labels = jumps = menus = total = dialogue = 0
        for line in lines:
            total += 1
            if re.search(r'^\s*label\s+', line):
                labels += 1
            if re.search(r'^\s*jump\s+', line):
                jumps += 1
            if re.search(r'^\s*menu\s*:', line):
                menus += 1
            if re.search(r'["“]', line):
                dialogue += 1

        ratio = (dialogue / total * 100) if total > 0 else 0
        score = min(10, 4 + (labels > 12) * 2 + (jumps > 25) * 2 + (menus > 6) * 2)

        return {
            "labels": labels,
            "jumps": jumps,
            "menus": menus,
            "total_lines": total,
            "dialogue_ratio": ratio,
            "score": score
        }