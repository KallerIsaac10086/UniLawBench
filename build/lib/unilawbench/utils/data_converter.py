import json
import csv
import re
from pathlib import Path
from typing import Dict, List, OrderedDict

FOCUS2LETTER = {
    "诉讼主体": "A", "租金情况": "B", "利息": "C", "本金争议": "D",
    "责任认定": "E", "责任划分": "F", "损失认定及处理": "G",
    "原审判决是否适当": "H", "合同效力": "I", "财产分割": "J",
    "责任承担": "K", "鉴定结论采信问题": "L", "诉讼时效": "M",
    "违约": "N", "合同解除": "O", "肇事逃逸": "P",
}

# 通用转换函数
def convert_format(input_path: Path, output_path: Path, convert_type: str):
    if convert_type == 'focus':
        convert_focus(input_path, output_path)
    elif convert_type == 'mcq':
        convert_mcq(input_path, output_path)
    elif convert_type == 'qa':
        convert_qa(input_path, output_path)

# 纠纷焦点转换逻辑
def convert_focus(input_path: Path, output_path: Path):
    records, bad_lines = load_records(input_path)
    with output_path.open('w', encoding='utf-8') as f:
        for rec in records:
            f.write(json.dumps({
                "instruction": "判断句子包含的争议焦点类别，每个句子只包含一个争议焦点类别。",
                "question": rec["question"],
                "answer": f"正确答案：{'、'.join(extract_categories(rec['answer']))}。"
            }) + '\n')

# 选择题转换逻辑
def convert_mcq(input_path: Path, output_path: Path):
    cats = extract_categories_from_first_line(input_path)
    rows = [parse_item(obj, cats) for obj in load_jsonl(input_path)]
    
    with output_path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'question'] + list(cats.values()) + ['answer'])
        for idx, r in enumerate(rows, 1):
            writer.writerow([idx, r['question']] + [cats[l] for l in cats] + [r['answer']])

# 问答题转换逻辑（示例）
def convert_qa(input_path: Path, output_path: Path):
    with input_path.open(encoding='utf-8') as fin, output_path.open('w', encoding='utf-8') as fout:
        for line in fin:
            data = json.loads(line)
            fout.write(json.dumps({
                "instruction": data.get("instruction", ""),
                "question": data["question"],
                "answer": data["answer"]
            }) + '\n')

# 以下为从原有脚本提取的公共函数
# [原有工具函数保持不变...]