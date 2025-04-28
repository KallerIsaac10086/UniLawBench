#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EvalScope集成模块 - UniLawBench

此模块提供了EvalScope与UniLawBench的集成功能，允许用户：
1. 将UniLawBench数据转换为EvalScope格式
2. 使用EvalScope评估模型在UniLawBench上的表现
3. 可视化评估结果

用法:
    python evalscope_integration.py convert <input_file> <output_file>
    python evalscope_integration.py evaluate <model_name> <dataset_path>
    python evalscope_integration.py visualize <results_file>
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

try:
    import evalscope
    from evalscope.data import DatasetFormatError
    from evalscope.evaluation import evaluate_model
    from evalscope.visualization import visualize_results
except ImportError:
    print("错误: 未安装evalscope包，请先安装: pip install evalscope[all]")
    sys.exit(1)

# ================= 常量定义 =================
SUPPORTED_MODELS = ["gpt-3.5-turbo", "gpt-4", "qwen", "baichuan", "llama"]
DEFAULT_OUTPUT_DIR = "evalscope_results"

# ================= 数据转换函数 =================
def convert_to_evalscope_format(input_file: str, output_file: str) -> None:
    """将UniLawBench数据转换为EvalScope格式"""
    input_path = Path(input_file)
    output_path = Path(output_file)
    
    if not input_path.exists():
        print(f"错误: 输入文件 {input_file} 不存在")
        return
    
    # 创建输出目录
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 根据文件扩展名确定处理方式
    if input_path.suffix.lower() == ".jsonl":
        _convert_jsonl_to_evalscope(input_path, output_path)
    elif input_path.suffix.lower() == ".csv":
        _convert_csv_to_evalscope(input_path, output_path)
    else:
        print(f"错误: 不支持的文件格式 {input_path.suffix}")
        return
    
    print(f"✅ 已将 {input_file} 转换为EvalScope格式: {output_file}")

def _convert_jsonl_to_evalscope(input_path: Path, output_path: Path) -> None:
    """将JSONL格式转换为EvalScope格式"""
    evalscope_data = []
    
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            
            try:
                item = json.loads(line)
                
                # 检查是否已经是EvalScope格式
                if "choices" in item and "answer_index" in item:
                    evalscope_data.append(item)
                    continue
                
                # 从instruction中提取选项
                instruction = item.get("instruction", "")
                question = item.get("question", "")
                answer = item.get("answer", "")
                
                # 解析选项和答案
                choices, answer_indices = _parse_options_and_answer(instruction, answer)
                
                # 创建EvalScope格式的数据项
                evalscope_item = {
                    "question": question,
                    "choices": choices,
                    "answer_index": answer_indices,
                    "metadata": {
                        "original_instruction": instruction,
                        "original_answer": answer
                    }
                }
                
                evalscope_data.append(evalscope_item)
                
            except json.JSONDecodeError:
                print(f"警告: 跳过无效的JSON行: {line[:50]}...")
            except Exception as e:
                print(f"警告: 处理行时出错: {str(e)}")
    
    # 写入输出文件
    with open(output_path, "w", encoding="utf-8") as f:
        for item in evalscope_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

def _convert_csv_to_evalscope(input_path: Path, output_path: Path) -> None:
    """将CSV格式转换为EvalScope格式"""
    import csv
    
    evalscope_data = []
    
    with open(input_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        
        if not headers or "question" not in headers or "answer" not in headers:
            print("错误: CSV文件格式不正确，必须包含'question'和'answer'列")
            return
        
        # 确定选项列
        option_columns = [h for h in headers if h not in ["id", "question", "answer"]]
        
        for row in reader:
            question = row.get("question", "")
            answer = row.get("answer", "")
            
            # 提取选项
            choices = [row.get(col, "") for col in option_columns if row.get(col)]
            
            # 解析答案（格式如"A、B"）
            answer_letters = [letter.strip() for letter in answer.split("、") if letter.strip()]
            answer_indices = [ord(letter) - ord("A") for letter in answer_letters if "A" <= letter <= "Z"]
            
            evalscope_item = {
                "question": question,
                "choices": choices,
                "answer_index": answer_indices,
                "metadata": {
                    "original_answer": answer
                }
            }
            
            evalscope_data.append(evalscope_item)
    
    # 写入输出文件
    with open(output_path, "w", encoding="utf-8") as f:
        for item in evalscope_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

def _parse_options_and_answer(instruction: str, answer: str) -> tuple:
    """从instruction和answer中解析选项和答案"""
    import re
    
    # 从instruction中提取选项
    options_pattern = r"([A-Z])、([^;；]+)"
    options_matches = re.findall(options_pattern, instruction)
    
    if not options_matches:
        raise ValueError("无法从instruction中提取选项")
    
    # 构建选项列表
    choices = [text.strip() for _, text in options_matches]
    
    # 从answer中提取答案字母
    answer_pattern = r"[A-Z]"
    answer_letters = re.findall(answer_pattern, answer)
    
    if not answer_letters:
        raise ValueError(f"无法从answer中提取答案字母: {answer}")
    
    # 将答案字母转换为索引
    answer_indices = [ord(letter) - ord("A") for letter in answer_letters]
    
    return choices, answer_indices

# ================= 评估函数 =================
def evaluate_with_evalscope(model_name: str, dataset_path: str, 
                           output_dir: Optional[str] = None) -> str:
    """使用EvalScope评估模型在UniLawBench上的表现"""
    if model_name not in SUPPORTED_MODELS:
        print(f"警告: 模型 {model_name} 可能不受支持。支持的模型: {', '.join(SUPPORTED_MODELS)}")
    
    dataset_path = Path(dataset_path)
    if not dataset_path.exists():
        print(f"错误: 数据集文件 {dataset_path} 不存在")
        return ""
    
    # 设置输出目录
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成结果文件路径
    result_file = Path(output_dir) / f"{model_name}_results.json"
    
    try:
        # 调用EvalScope进行评估
        print(f"开始使用 {model_name} 评估数据集 {dataset_path}...")
        results = evaluate_model(
            model_name=model_name,
            dataset_path=str(dataset_path),
            output_file=str(result_file)
        )
        
        print(f"✅ 评估完成，结果已保存至: {result_file}")
        return str(result_file)
        
    except DatasetFormatError as e:
        print(f"错误: 数据集格式不正确: {e}")
    except Exception as e:
        print(f"错误: 评估过程中出错: {e}")
    
    return ""

# ================= 可视化函数 =================
def visualize_evalscope_results(results_file: str, output_dir: Optional[str] = None) -> None:
    """可视化EvalScope评估结果"""
    results_path = Path(results_file)
    if not results_path.exists():
        print(f"错误: 结果文件 {results_file} 不存在")
        return
    
    # 设置输出目录
    if output_dir is None:
        output_dir = results_path.parent / "visualizations"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 调用EvalScope进行可视化
        print(f"开始可视化结果文件 {results_file}...")
        visualize_results(
            results_file=str(results_path),
            output_dir=str(output_dir)
        )
        
        print(f"✅ 可视化完成，结果已保存至: {output_dir}")
        
    except Exception as e:
        print(f"错误: 可视化过程中出错: {e}")

# ================= 命令行接口 =================
def main():
    parser = argparse.ArgumentParser(description="EvalScope集成工具 - UniLawBench")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # 转换命令
    convert_parser = subparsers.add_parser("convert", help="将UniLawBench数据转换为EvalScope格式")
    convert_parser.add_argument("input", help="输入文件路径（.jsonl或.csv）")
    convert_parser.add_argument("output", help="输出文件路径（.jsonl）")
    
    # 评估命令
    evaluate_parser = subparsers.add_parser("evaluate", help="使用EvalScope评估模型")
    evaluate_parser.add_argument("model", help=f"模型名称，支持: {', '.join(SUPPORTED_MODELS)}")
    evaluate_parser.add_argument("dataset", help="数据集文件路径（EvalScope格式）")
    evaluate_parser.add_argument("--output-dir", help="结果输出目录")
    
    # 可视化命令
    visualize_parser = subparsers.add_parser("visualize", help="可视化评估结果")
    visualize_parser.add_argument("results", help="评估结果文件路径")
    visualize_parser.add_argument("--output-dir", help="可视化结果输出目录")
    
    args = parser.parse_args()
    
    if args.command == "convert":
        convert_to_evalscope_format(args.input, args.output)
    elif args.command == "evaluate":
        evaluate_with_evalscope(args.model, args.dataset, args.output_dir)
    elif args.command == "visualize":
        visualize_evalscope_results(args.results, args.output_dir)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()