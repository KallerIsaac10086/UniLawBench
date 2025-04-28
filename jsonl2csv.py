#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, json, csv, re, sys
from pathlib import Path
from typing import Dict, List, OrderedDict, Optional, Union, Any
from collections import defaultdict

# ================= 可配置 =================
WRITE_OPTIONS = True           # False → 只输出 id,question,answer
CSV_ENCODING  = "utf-8-sig"    # 带 BOM，Excel 直接识别 UTF-8
SUPPORT_EVALSCOPE = True       # 支持EvalScope格式的数据
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
    # 去掉可能的 "句子:" 前缀与首尾空格
    q = obj.get("question", "").lstrip("句子:").strip()
    
    # 处理EvalScope格式的答案
    if SUPPORT_EVALSCOPE and "choices" in obj and "answer_index" in obj:
        # EvalScope格式处理
        answer_indices = obj["answer_index"]
        if isinstance(answer_indices, int):
            answer_indices = [answer_indices]  # 转换单选为列表
        
        # 将索引转换为字母（A, B, C...）
        letters = [chr(65 + idx) for idx in answer_indices if 0 <= idx < len(obj["choices"])]
    else:
        # 传统格式处理：抓取所有大写字母并去重保持顺序
        letters: List[str] = []
        for ltr in ANS_RE.findall(obj.get("answer", "")):
            if ltr not in letters:
                letters.append(ltr)
    
    if not letters:
        raise ValueError(f"answer 无法解析: {obj.get('answer')}")

    return {"question": q, "answer": "、".join(letters)}

def load_jsonl(fp: Path) -> List[Dict]:
    """加载JSONL文件，支持标准JSONL和EvalScope格式"""
    try:
        with fp.open(encoding="utf-8") as f:
            data = [json.loads(line) for line in f if line.strip()]
            
        # 检测是否为EvalScope格式
        if SUPPORT_EVALSCOPE and data and all("choices" in item and "answer_index" in item for item in data):
            print(f"检测到EvalScope格式数据: {fp}")
            
        return data
    except Exception as e:
        print(f"加载文件失败 {fp}: {e}", file=sys.stderr)
        return []

def main() -> None:
    parser = argparse.ArgumentParser(description="jsonl → csv (多类别题)")
    parser.add_argument("input",  help="单个 .jsonl 文件或包含 .jsonl 的文件夹")
    parser.add_argument("output", help="输出 CSV 路径")
    parser.add_argument("--no-options", action="store_true", help="只输出id,question,answer，不包含选项")
    parser.add_argument("--encoding", default=CSV_ENCODING, help=f"CSV编码，默认: {CSV_ENCODING}")
    parser.add_argument("--evalscope", action="store_true", help="强制使用EvalScope格式处理")
    args = parser.parse_args()
    
    # 根据命令行参数覆盖全局设置
    global WRITE_OPTIONS, CSV_ENCODING, SUPPORT_EVALSCOPE
    if args.no_options:
        WRITE_OPTIONS = False
    if args.encoding:
        CSV_ENCODING = args.encoding
    if args.evalscope:
        SUPPORT_EVALSCOPE = True

    in_path = Path(args.input)
    files   = sorted(in_path.glob("*.jsonl")) if in_path.is_dir() else [in_path]

    # --------------- 解析类别映射 ---------------
    try:
        first_obj = json.loads(open(files[0], encoding="utf-8").readline())
        
        # 处理EvalScope格式
        if SUPPORT_EVALSCOPE and "choices" in first_obj:
            # 从choices构建类别映射
            categories = OrderedDict()
            for i, choice in enumerate(first_obj["choices"]):
                letter = chr(65 + i)  # A, B, C...
                categories[letter] = choice.strip()
        else:
            # 传统格式
            categories = extract_categories(first_obj["instruction"])
            
        letters = list(categories.keys())
    except Exception as e:
        print(f"解析类别映射失败: {e}", file=sys.stderr)
        sys.exit(1)

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
