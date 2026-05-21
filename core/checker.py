# core/checker.py
import re
from .patterns import LABEL_PATTERN, JUMP_PATTERN, CALL_PATTERN, DIALOGUE_PATTERN

class ScriptChecker:
    def check_text(self, text: str, cfg_dead_link=True, cfg_quotes=True, cfg_punc=True):
        """返回校验结果列表和错误数量"""
        lines = text.splitlines()
        results = ["=== 🔍 多模态规范与逻辑审计日志 ==="]
        error_count = 0

        # 收集所有 label
        valid_labels = set()
        for line in lines:
            m = re.search(LABEL_PATTERN, line)
            if m:
                valid_labels.add(m.group(1))

        # 孤立节点检测
        if cfg_dead_link:
            targeted = set()
            for line in lines:
                for pat in (JUMP_PATTERN, CALL_PATTERN):
                    m = re.search(pat, line)
                    if m:
                        targeted.add(m.group(1))
            isolated = valid_labels - targeted - {"start", "chapter_1"}
            for node in isolated:
                results.append(f"⚠️ [逻辑孤立点] 节点 '{node}' 未被任何跳转指向（可能为废弃内容）")
                error_count += 1

        # 逐行检测
        keywords = ("label", "jump", "call", "menu", "scene", "show", "hide", "play", "stop", "$")

        for index, line in enumerate(lines):
            curr = index + 1
            clean = line.strip()
            if not clean or clean.startswith("#"):
                continue

            # 死链检测
            if cfg_dead_link:
                m = re.search(JUMP_PATTERN, clean)
                if m and m.group(1) not in valid_labels:
                    results.append(f"❌ [逻辑死链] 第 {curr} 行 -> jump 指向不存在的节点 '{m.group(1)}'")
                    error_count += 1

            # 控制语句中文冒号
            if any(clean.startswith(k) for k in keywords):
                if "：" in clean and ":" not in clean:
                    results.append(f"⚠️ [语法错误] 第 {curr} 行 -> 控制语句中使用了中文冒号 '：'")
                    error_count += 1
                continue

            # 引号检测
            if cfg_quotes:
                quotes = re.findall(r'["“”]', clean)
                if quotes:
                    if len(quotes) % 2 != 0:
                        results.append(f"❌ [引号残缺] 第 {curr} 行 -> 引号未成对闭合")
                        error_count += 1
                    elif clean.startswith("“") and clean.endswith('"'):
                        results.append(f"❌ [引号规范] 第 {curr} 行 -> 中英引号混用（“ 与 \"）")
                        error_count += 1

            # 标点检测
            if cfg_punc:
                dialogues = re.findall(DIALOGUE_PATTERN, clean)
                for d in dialogues:
                    pure = re.sub(r'\{[^}]+\}', '', d)
                    if not pure.strip():
                        continue
                    if re.search(r'[\u4e00-\u9fff]', pure):   # 中文
                        if ',' in pure:
                            results.append(f"❌ [标点问题] 第 {curr} 行 -> 中文对话中使用英文逗号 ','")
                            error_count += 1
                        if '.' in pure and not pure.endswith('...'):
                            results.append(f"❌ [标点问题] 第 {curr} 行 -> 中文对话中使用英文句号 '.'")
                            error_count += 1

        results.append("------")
        results.append(f"审计完成：共发现 {error_count} 个问题")
        return results, error_count