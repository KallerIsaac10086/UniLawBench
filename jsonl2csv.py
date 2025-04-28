#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, json, csv, re
from pathlib import Path
from typing import Dict, List, OrderedDict

# ================= 可配置 =================
WRITE_OPTIONS = True           # False → 只输出 id,question,answer
CSV_ENCODING  = "utf-8-sig"    # 带 BOM，Excel 直接识别 UTF-8
# ========================================

# A、类别
CAT_RE = re.compile(r"([A-Z])、([^;；]+)")
# 全部答案字母
ANS_RE = re.compile(r"[A-Z]")

def extract_categories(instr: str) -> "OrderedDict[str,str]":
    """从 instruction 里生成 {字母: 中文类别}（保持顺序）"""
    cats: "OrderedDict[str,str]" = OrderedDict()
    for m in CAT_RE.finditer(instr):
        letter, text = m.groups()
        cats[letter] = text.strip()
    if not cats:
        raise ValueError("instruction 中未找到 'A、类别' 描述")
    return cats

def parse_item(obj: Dict, cats: Dict[str, str]) -> Dict:
    """取 question && answer（answer 可能多选）"""
    # 去掉可能的 “句子:” 前缀与首尾空格
    q = obj.get("question", "").lstrip("句子:").strip()

    # 抓取所有大写字母并去重保持顺序
    letters: List[str] = []
    for ltr in ANS_RE.findall(obj.get("answer", "")):
        if ltr not in letters:
            letters.append(ltr)
    if not letters:
        raise ValueError(f"answer 无合法字母: {obj.get('answer')}")

    return {"question": q, "answer": "、".join(letters)}

def load_jsonl(fp: Path) -> List[Dict]:
    with fp.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def main() -> None:
    parser = argparse.ArgumentParser(description="jsonl → csv (多类别题)")
    parser.add_argument("input",  help="单个 .jsonl 文件或包含 .jsonl 的文件夹")
    parser.add_argument("output", help="输出 CSV 路径")
    args = parser.parse_args()

    in_path = Path(args.input)
    files   = sorted(in_path.glob("*.jsonl")) if in_path.is_dir() else [in_path]

    # --------------- 解析类别映射 ---------------
    first_obj = json.loads(open(files[0], encoding="utf-8").readline())
    categories = extract_categories(first_obj["instruction"])
    letters = list(categories.keys())

    # --------------- 读取全部数据 ---------------
    rows = []
    for fp in files:
        rows.extend(parse_item(obj, categories) for obj in load_jsonl(fp))

    # --------------- 写 CSV --------------------
    header = ["id", "question"] + (letters if WRITE_OPTIONS else []) + ["answer"]
    with Path(args.output).open("w", newline="", encoding=CSV_ENCODING) as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for idx, r in enumerate(rows, 1):
            row = [idx, r["question"]]
            if WRITE_OPTIONS:
                row.extend(categories[l] for l in letters)
            row.append(r["answer"])
            writer.writerow(row)

    print(f"✅ 已转换 {len(rows)} 条 → {args.output}")

if __name__ == "__main__":
    main()
