#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert_dynamic_choice.py  ·  v1.1
─────────────────────────────────────────────────────────────────────────────
1. 输入：既支持  ❖  JSON 数组   ❖  JSONL（每行一个 JSON 对象）
   - JSON 对象至少包含 instruction / question / answer 三个键

2. 解析 instruction
      ▶ 提取 “标签包括：……。” 这一段
      ▶ 按出现顺序为标签分配字母  A、B、C …

3. 解析 answer
      ▶ 兼容 4 种格式（单选 / 多选 均可）
          ① 「类别:婚姻家庭、劳动纠纷。」
          ② 「[类别]婚姻家庭<eoa>」
          ③ 「正确答案：A、B。」
          ④ 仅写中文标签          ←★ 新增，直接支持
      ▶ 支持多个中文标签用 “、/，/, 空格” 分隔

4. 输出：统一的多项选择 JSONL
      {
        "instruction": "判断句子所属类别……类别包括:A、婚姻家庭;B、劳动纠纷;…",
        "question": "...",
        "answer": "正确答案：A、B。"
      }

用法:
    python convert_dynamic_choice.py   in.jsonl   out.jsonl
"""

import argparse
import json
import re
import sys
from pathlib import Path
from string import ascii_uppercase

# ────────────────────────────── 1. 解析标签 → mapping ──────────────────────────────
def build_mapping(instruction: str):
    """从 instruction 中抓取中文标签列表并映射到字母"""
    m = re.search(r"标签包括：(.+?)。", instruction)
    if not m:
        return None
    labels = [lab.strip() for lab in re.split(r"[、,，;；\s]+", m.group(1)) if lab.strip()]
    if len(labels) > len(ascii_uppercase):
        raise ValueError("❌ 标签超过 26 个，字母不够用了")
    return {lab: ascii_uppercase[i] for i, lab in enumerate(labels)}

# ────────────────────────────── 2. 解析 answer ──────────────────────────────
def get_answer_letters(ans_text: str, zh2letter: dict):
    """
    根据 answer 字段内容，返回字母列表，例如 ['A'] 或 ['A', 'B']
    """
    ans_text = ans_text.strip()

    # ① 「类别: xxx」
    m = re.search(r"类别[:：]\s*([^\.;。]+)", ans_text)
    if m:
        zh_tags = [t.strip() for t in re.split(r"[、,，;\s]+", m.group(1)) if t.strip()]
        return [zh2letter[t] for t in zh_tags]

    # ② 「[类别]xxx<eoa>」
    m = re.search(r"\[类别\]\s*([^\[<]+?)<\s*eoa\s*>", ans_text, flags=re.I)
    if m:
        zh_tags = [t.strip() for t in re.split(r"[、,，;\s]+", m.group(1)) if t.strip()]
        return [zh2letter[t] for t in zh_tags]

    # ③ 「正确答案：A、B。」
    m = re.search(r"正确答案[:：]\s*([A-Z](?:[、,，;][A-Z])*)", ans_text, flags=re.I)
    if m:
        return [s.strip().upper() for s in re.split(r"[、,，;]", m.group(1))]

    # ④ 仅写中文标签（★ 新增 fallback）
    zh_tags = [t.strip() for t in re.split(r"[、,，;\s]+", ans_text) if t.strip()]
    if all(tag in zh2letter for tag in zh_tags):
        return [zh2letter[tag] for tag in zh_tags]

    raise ValueError(f"❌ 无法识别 answer 字段格式: {ans_text}")

# ────────────────────────────── 3. 生成新 instruction ──────────────────────────────
def make_new_instruction(zh2letter: dict):
    parts = [f"{ltr}、{lab}" for lab, ltr in zh2letter.items()]
    return f"判断句子所属类别，可为单选或多选。类别包括:{';'.join(parts)}。选择正确的答案。"

# ────────────────────────────── 4. 转换单条记录 ──────────────────────────────
def convert_record(rec: dict, zh2letter: dict):
    letters = sorted(set(get_answer_letters(rec["answer"], zh2letter)),
                     key=lambda x: ascii_uppercase.index(x))
    return {
        "instruction": make_new_instruction(zh2letter),
        "question": rec["question"],
        "answer": f"正确答案：{'、'.join(letters)}。"
    }

# ────────────────────────────── 5. 读取 JSON / JSONL ──────────────────────────────
def load_any_json(path: Path):
    text = path.read_text(encoding="utf-8").lstrip()
    if text.startswith("["):                       # JSON 数组
        return json.loads(text)

    # 否则按 JSONL 读取
    records = []
    for idx, line in enumerate(path.open(encoding="utf-8"), 1):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise ValueError(f"第 {idx} 行 JSON 解析失败: {e}") from None
    return records

# ────────────────────────────── 6. 主程序 ──────────────────────────────
def main(argv=None):
    ap = argparse.ArgumentParser(description="动态标签 → 标准多选格式 转换器")
    ap.add_argument("input",  help="原始 JSON / JSONL 文件")
    ap.add_argument("output", help="输出 JSONL 文件")
    args = ap.parse_args(argv)

    in_path  = Path(args.input)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    records = load_any_json(in_path)
    if not records:
        print("⚠️  输入为空", file=sys.stderr)
        return

    zh2letter = build_mapping(records[0]["instruction"])
    if zh2letter is None:
        raise RuntimeError("未在 instruction 中找到“标签包括：…”段落，无法获取标签列表")

    with out_path.open("w", encoding="utf-8") as fw:
        for rec in records:
            fw.write(json.dumps(convert_record(rec, zh2letter), ensure_ascii=False) + "\n")

    print(f"✅ 已转换 {len(records)} 条 → {out_path}")

# ────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
