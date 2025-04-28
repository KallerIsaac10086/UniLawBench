import argparse
import sys
import os
import json
import re
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, OrderedDict
from collections import defaultdict



# 常量定义
SUPPORTED_MODELS = ["gpt-3.5-turbo", "gpt-4", "qwen", "baichuan", "llama"]
DEFAULT_OUTPUT_DIR = "evalscope_results"

def main():
    parser = argparse.ArgumentParser(description='UniLawBench 法律评估工具')
    
    # 支持两种使用方式：子命令模式和参数模式
    # 1. 子命令模式（兼容旧版本）
    subparsers = parser.add_subparsers(dest='command')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='显示当前版本号')
    version_parser.set_defaults(func=handle_version)

    # GUI命令
    gui_parser = subparsers.add_parser('gui', help='启动图形界面')
    gui_parser.set_defaults(func=handle_gui)
    
    # 评估命令
    eval_parser = subparsers.add_parser('eval', help='启动评估任务')
    eval_parser.add_argument('-set', nargs='+', help='指定评估数据集ID，例如1-1 2-3')
    eval_parser.add_argument('-form', choices=['qa', 'mcq'], required=True, 
                           help='评估形式: qa-问答题 mcq-选择题')
    eval_parser.add_argument('-model', type=Path, required=True,
                           help='本地模型路径（包含模型文件和配置文件）')
    eval_parser.add_argument('--run-all', action='store_true',
                           help='自动运行当前form类型的所有数据集')
    eval_parser.set_defaults(func=handle_eval)

    # 数据转换命令
    convert_parser = subparsers.add_parser('convert', help='数据格式转换工具')
    convert_parser.add_argument('--type', choices=['mcq', 'qa', 'focus', 'dynamic-choice', 'evalscope'], required=True,
                              help='转换类型: mcq-选择题 qa-问答题 focus-纠纷焦点 dynamic-choice-动态选择题 evalscope-EvalScope格式')
    convert_parser.add_argument('input', type=Path, help='输入文件路径')
    convert_parser.add_argument('output', type=Path, help='输出文件路径')
    convert_parser.set_defaults(func=handle_convert)
    

    
    # 可视化命令
    visualize_parser = subparsers.add_parser('visualize', help='可视化评估结果')
    visualize_parser.add_argument('results', help='评估结果文件路径')
    visualize_parser.add_argument('-output', help='可视化结果输出目录')
    visualize_parser.set_defaults(func=handle_visualize)
    
    # 2. 参数模式（新版本）
    # 基本参数
    parser.add_argument("-set", help="数据集ID，例如: 1-1, 2-2等")
    parser.add_argument("-form", choices=["qa", "mcq"], help="评估形式: qa(问答题) 或 mcq(选择题)")
    parser.add_argument("-model", help="模型路径或名称")
    parser.add_argument("-output", help="结果输出目录")
    
    # 批量运行
    parser.add_argument("-run-all-qa", action="store_true", help="运行所有问答题评估")
    parser.add_argument("-run-all-mcq", action="store_true", help="运行所有选择题评估")
    
    # 数据转换
    parser.add_argument("-convert", choices=["jsonl2csv", "csv2jsonl", "dynamic-choice", "focus", "evalscope"], 
                        help="数据转换功能")
    parser.add_argument("-input", help="输入文件路径")
    parser.add_argument("-output-file", help="输出文件路径")
    

    
    # 可视化
    parser.add_argument("-visualize", help="可视化结果文件")
    
    # GUI
    parser.add_argument("-gui", action="store_true", help="启动图形用户界面")
    
    args = parser.parse_args()
    
    # 处理子命令模式
    if hasattr(args, 'func'):
        if args.command == 'gui' and len(sys.argv) > 2:
            parser.error("gui命令不能与其他参数同时使用")
        args.func(args)
        return
    
    # 处理参数模式
    # 启动GUI
    if args.gui:
        handle_gui(args)
        return
    
    # 可视化结果
    if args.visualize:
        visualize_evalscope_results(args.visualize, args.output)
        return
    

    
    # 数据转换
    if args.convert:
        if not args.input or not args.output_file:
            print("错误: 数据转换需要指定 -input 和 -output-file 参数")
            return
        
        if args.convert == "evalscope":
            convert_to_evalscope_format(args.input, args.output_file)
        else:
            from .utils.data_converter import convert_format
            convert_format(Path(args.input), Path(args.output_file), args.convert)
        return
    
    # 运行所有问答题
    if args.run_all_qa:
        if not args.model:
            print("错误: 请指定 -model 参数")
            return
        
        datasets = get_all_datasets("qa")
        for dataset_path in datasets:
            evaluate_dataset(args.model, str(dataset_path), args.output)
        return
    
    # 运行所有选择题
    if args.run_all_mcq:
        if not args.model:
            print("错误: 请指定 -model 参数")
            return
        
        datasets = get_all_datasets("mcq")
        for dataset_path in datasets:
            evaluate_dataset(args.model, str(dataset_path), args.output)
        return
    
    # 单个数据集评估
    if args.set and args.form and args.model:
        try:
            dataset_path = get_dataset_path(args.set, args.form)
            evaluate_dataset(args.model, str(dataset_path), args.output)
        except FileNotFoundError as e:
            print(f"错误: {e}")
        return
    
    # 如果没有匹配任何命令，显示帮助
    parser.print_help()

def handle_convert(args):
    try:
        if args.type == 'evalscope':
            convert_to_evalscope_format(args.input, args.output)
        elif args.type == 'dynamic-choice':
            convert_dynamic_choice(args.input, args.output)
        else:
            # 内联数据转换函数
            if args.type == 'focus':
                convert_focus(args.input, args.output)
            elif args.type == 'mcq':
                convert_mcq(args.input, args.output)
            elif args.type == 'qa':
                convert_qa(args.input, args.output)
        print(f"✅ 转换完成: {args.output}")
    except Exception as e:
        print(f"❌ 转换失败: {str(e)}")
        exit(1)

# 数据转换函数实现
def convert_focus(input_path, output_path):
    records, bad_lines = load_records(input_path)
    with output_path.open('w', encoding='utf-8') as f:
        for rec in records:
            f.write(json.dumps({
                "instruction": "判断句子包含的争议焦点类别，每个句子只包含一个争议焦点类别。",
                "question": rec["question"],
                "answer": f"正确答案：{'、'.join(extract_categories(rec['answer']))}。"
            }) + '\n')

def convert_mcq(input_path, output_path):
    cats = extract_categories_from_first_line(input_path)
    rows = [parse_item(obj, cats) for obj in load_jsonl(input_path)]
    
    with output_path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'question'] + list(cats.values()) + ['answer'])
        for idx, r in enumerate(rows, 1):
            writer.writerow([idx, r['question']] + [cats[l] for l in cats] + [r['answer']])

def convert_qa(input_path, output_path):
    with input_path.open(encoding='utf-8') as fin, output_path.open('w', encoding='utf-8') as fout:
        for line in fin:
            data = json.loads(line)
            fout.write(json.dumps({
                "instruction": data.get("instruction", ""),
                "question": data["question"],
                "answer": data["answer"]
            }) + '\n')

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

# ================= 辅助函数 =================
def get_dataset_path(dataset_id: str, form: str) -> Path:
    """获取数据集文件路径"""
    # 确定数据集目录
    if form.lower() == "qa":
        base_dir = "qa"
        ext = ".jsonl"
    elif form.lower() == "mcq":
        base_dir = "mcq"
        ext = ".csv"
    else:
        raise ValueError(f"不支持的形式: {form}，请使用 'qa' 或 'mcq'")
    
    # 查找匹配的数据集文件
    dataset_dir = Path(__file__).parent / "dataset" / base_dir
    
    # 如果是精确匹配（如1-1）
    exact_match = list(dataset_dir.glob(f"{dataset_id}*{ext}"))
    if exact_match:
        return exact_match[0]
    
    # 如果没有找到，返回错误
    raise FileNotFoundError(f"找不到数据集: {dataset_id} (形式: {form})")

def get_all_datasets(form: str) -> List[Path]:
    """获取指定形式的所有数据集文件路径"""
    if form.lower() == "qa":
        base_dir = "qa"
        ext = ".jsonl"
    elif form.lower() == "mcq":
        base_dir = "mcq"
        ext = ".csv"
    else:
        raise ValueError(f"不支持的形式: {form}，请使用 'qa' 或 'mcq'")
    
    dataset_dir = Path(__file__).parent / "dataset" / base_dir
    return list(dataset_dir.glob(f"*{ext}"))

# ================= 评估函数 =================
def evaluate_dataset(model_name: str, dataset_path: str, 
                    output_dir: Optional[str] = None) -> str:
    """评估模型在指定数据集上的表现"""
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
    result_file = Path(output_dir) / f"{model_name}_{dataset_path.stem}_results.json"
    
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

# ================= EvalScope集成函数 =================
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


def resolve_datasets(args) -> List[str]:
    """解析数据集参数，支持--run-all时自动加载对应类型的所有数据集"""
    if args.run_all:
        data_dir = Path(__file__).parent / 'dataset' / args.form
        return [f.stem for f in data_dir.glob('*.*') if f.suffix in ('.csv', '.jsonl')]
    return args.set if args.set else []

def handle_evalscope(args):
    """处理EvalScope评估命令"""
    try:
        result_file = evaluate_with_evalscope(
            model_name=args.model,
            dataset_path=args.dataset,
            output_dir=args.output
        )
        if result_file:
            print(f"✅ EvalScope评估完成，结果已保存至: {result_file}")
    except Exception as e:
        print(f"❌ EvalScope评估失败: {str(e)}")
        exit(1)

def handle_visualize(args):
    """处理可视化命令"""
    try:
        visualize_evalscope_results(args.results, args.output)
        print(f"✅ 可视化完成")
    except Exception as e:
        print(f"❌ 可视化失败: {str(e)}")
        exit(1)
        
def handle_test(args):
    """处理测试命令"""
    import subprocess
    
    test_cmd = ["python", "-m", "unittest", "discover", "tests"]
    if args.coverage:
        test_cmd = ["coverage", "run", "-m", "unittest", "discover", "tests"]
    
    try:
        subprocess.run(test_cmd, check=True)
        if args.coverage:
            subprocess.run(["coverage", "report"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"测试失败: {e}")
        sys.exit(1)

def convert_dynamic_choice(input_file: Path, output_file: Path) -> None:
    """将动态选择题转换为标准格式"""
    try:
        # 读取输入文件
        if input_file.suffix.lower() == ".jsonl":
            with open(input_file, "r", encoding="utf-8") as f:
                data = [json.loads(line) for line in f if line.strip()]
        elif input_file.suffix.lower() in [".json"]:
            with open(input_file, "r", encoding="utf-8") as f:
                text = f.read().lstrip()
                if text.startswith("["):
                    data = json.loads(text)
                else:
                    data = [json.loads(line) for line in text.split("\n") if line.strip()]
        else:
            print(f"错误: 不支持的文件格式 {input_file.suffix}")
            return
        
        # 处理每条记录
        converted_data = []
        for item in data:
            # 从instruction中提取标签
            instruction = item.get("instruction", "")
            question = item.get("question", "")
            answer = item.get("answer", "")
            
            # 提取标签列表
            match = re.search(r"标签包括：(.+?)。", instruction)
            if not match:
                print(f"警告: 无法从instruction中提取标签列表: {instruction[:50]}...")
                continue
                
            labels_text = match.group(1)
            labels = [lab.strip() for lab in re.split(r"[、,，;；\s]+", labels_text) if lab.strip()]
            
            # 创建标签到字母的映射
            label_to_letter = {label: chr(65 + i) for i, label in enumerate(labels)}
            
            # 从answer中提取标签
            answer_labels = []
            
            # 尝试不同格式
            # 格式1: "类别: xxx"
            match = re.search(r"类别[:：]\s*([^\.;。]+)", answer)
            if match:
                answer_labels = [t.strip() for t in re.split(r"[、,，;\s]+", match.group(1)) if t.strip()]
            
            # 格式2: "[类别]xxx<eoa>"
            if not answer_labels:
                match = re.search(r"\[类别\]\s*([^\[<]+?)<\s*eoa\s*>", answer, flags=re.I)
                if match:
                    answer_labels = [t.strip() for t in re.split(r"[、,，;\s]+", match.group(1)) if t.strip()]
            
            # 格式3: "正确答案：A、B。"
            if not answer_labels:
                match = re.search(r"正确答案[:：]\s*([A-Z](?:[、,，;][A-Z])*)", answer, flags=re.I)
                if match:
                    answer_letters = [s.strip().upper() for s in re.split(r"[、,，;]", match.group(1))]
                    # 反向查找标签
                    letter_to_label = {v: k for k, v in label_to_letter.items()}
                    answer_labels = [letter_to_label.get(letter, "") for letter in answer_letters if letter in letter_to_label]
            
            # 格式4: 直接使用中文标签
            if not answer_labels:
                potential_labels = [t.strip() for t in re.split(r"[、,，;\s]+", answer) if t.strip()]
                answer_labels = [label for label in potential_labels if label in label_to_letter]
            
            if not answer_labels:
                print(f"警告: 无法从answer中提取标签: {answer}")
                continue
            
            # 获取答案字母
            answer_letters = [label_to_letter[label] for label in answer_labels if label in label_to_letter]
            answer_letters = sorted(set(answer_letters))
            
            # 创建新的instruction
            parts = [f"{letter}、{label}" for label, letter in label_to_letter.items()]
            new_instruction = f"判断句子所属类别，可为单选或多选。类别包括:{';'.join(parts)}。选择正确的答案。"
            
            # 创建新记录
            converted_item = {
                "instruction": new_instruction,
                "question": question,
                "answer": f"正确答案：{'、'.join(answer_letters)}。"
            }
            
            converted_data.append(converted_item)
        
        # 写入输出文件
        with open(output_file, "w", encoding="utf-8") as f:
            for item in converted_data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        
        print(f"✅ 已将 {len(converted_data)} 条记录转换为标准格式: {output_file}")
        
    except Exception as e:
        print(f"❌ 动态选择题转换失败: {str(e)}")


def handle_gui(args):
    from .gui.window import MainWindow
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

def handle_eval(args):
    from .utils.evaluator import run_evaluation
    try:
        datasets = resolve_datasets(args)
        print(f"🚀 开始评估: {args.form} 形式, 共 {len(datasets)} 个数据集")
        
        results = run_evaluation(
            model_path=args.model,
            dataset_ids=datasets,
            eval_type=args.form
        )
        
        print("\n✅ 评估完成:")
        for dataset_id, metrics in results.items():
            print(f"📊 {dataset_id}: {metrics}")
    except Exception as e:
        print(f"❌ 评估失败: {str(e)}")
        exit(1)

def handle_version(args):
    from unilawbench import __version__
    print(f"UniLawBench 版本: {__version__}")

if __name__ == '__main__':
    main()