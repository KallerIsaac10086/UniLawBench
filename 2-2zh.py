#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert_focus_v2.py
1. 既能处理 JSON 数组文件，也能处理 JSONL。
2. 遇到不合法 JSON 行，会记录到 error_lines.txt 而不中断整体转换。
用法:
    python convert_focus_v2.py input_path output_path
"""

import argparse, json, os, re, sys
from pathlib import Path

FOCUS2LETTER = {
    "诉讼主体": "A", "租金情况": "B", "利息": "C", "本金争议": "D",
    "责任认定": "E", "责任划分": "F", "损失认定及处理": "G",
    "原审判决是否适当": "H", "合同效力": "I", "财产分割": "J",
    "责任承担": "K", "鉴定结论采信问题": "L", "诉讼时效": "M",
    "违约": "N", "合同解除": "O", "肇事逃逸": "P",
}

STANDARD_INSTRUCTION = (
    "判断句子包含的争议焦点类别，每个句子只包含一个争议焦点类别。"
    "类别包括:A、诉讼主体;B、租金情况;C、利息;D、本金争议;E、责任认定;"
    "F、责任划分;G、损失认定及处理;H、原审判决是否适当;I、合同效力;"
    "J、财产分割;K、责任承担;L、鉴定结论采信问题;M、诉讼时效;"
    "N、违约;O、合同解除;P、肇事逃逸。选择正确的答案。"
)

def extract_categories(ans: str):
    """把 answer 文本里的争议焦点提成字母列表"""
    # [争议焦点]责任认定<eoa>
    m = re.search(r"\[争议焦点\]\s*([^\[<]+?)<\s*eoa\s*>", ans, flags=re.I)
    if m:
        cats_str = m.group(1)
    else:
        # 争议焦点类别：责任认定
        m = re.search(r"(?:争议焦点类别|争议焦点)[：:]\s*([^\.;。]+)", ans)
        if m:
            cats_str = m.group(1)
        else:
            # 正确答案：E、F。
            m = re.search(r"正确答案[：:]\s*([A-P](?:[、,，][A-P])*)", ans, flags=re.I)
            if not m:
                raise ValueError("无法解析 answer 字段")
            return [s.strip().upper() for s in re.split(r"[、,，]", m.group(1))]
    # 把中文类别映射到字母
    letters = []
    for c in re.split(r"[、,，;\s]+", cats_str):
        c = c.strip()
        if c:
            letters.append(FOCUS2LETTER[c])
    return letters

def to_choice_obj(rec):
    letters = extract_categories(rec["answer"])
    return {
        "instruction": STANDARD_INSTRUCTION,
        "question": rec["question"],
        "answer": f"正确答案：{'、'.join(letters)}。"
    }

def load_records(path: Path):
    """同时兼容 JSON array 与 JSONL"""
    txt = path.read_text(encoding="utf-8").strip()
    # 如果是以 '[' 开头，就是数组文件
    if txt.startswith("["):
        return json.loads(txt)
    # 否则尝试逐行解析
    records, bad = [], []
    for lineno, line in enumerate(path.open(encoding="utf-8"), 1):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            bad.append((lineno, line))
    return records, bad

def main():
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("output")
    args = p.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 读取
    load_result = load_records(in_path)
    if isinstance(load_result, tuple):
        records, bad_lines = load_result
    else:              # JSON array 情况
        records, bad_lines = load_result, []

    # 转换
    out_f = out_path.open("w", encoding="utf-8")
    for rec in records:
        try:
            out_f.write(json.dumps(to_choice_obj(rec), ensure_ascii=False) + "\n")
        except Exception as e:
            bad_lines.append(("??", rec, str(e)))
    out_f.close()

    # 若有错误行，写到单独文件
    if bad_lines:
        err_file = in_path.with_suffix(".error_lines.txt")
        with err_file.open("w", encoding="utf-8") as f:
            for item in bad_lines:
                f.write(str(item) + "\n")
        print(f"⚠️  有 {len(bad_lines)} 行/条记录解析失败，详情见: {err_file}", file=sys.stderr)
    else:
        print("✅ 全部转换完成")

if __name__ == "__main__":
    main()
