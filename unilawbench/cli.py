import argparse
from pathlib import Path
from typing import List

import evalscope

def main():
    parser = argparse.ArgumentParser(description='UniLawBench 法律评估工具')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
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
    convert_parser.add_argument('--type', choices=['mcq', 'qa', 'focus'], required=True,
                              help='转换类型: mcq-选择题 qa-问答题 focus-纠纷焦点')
    convert_parser.add_argument('input', type=Path, help='输入文件路径')
    convert_parser.add_argument('output', type=Path, help='输出文件路径')
    convert_parser.set_defaults(func=handle_convert)

    args = parser.parse_args()
    args.func(args)

def handle_convert(args):
    from .utils.data_converter import convert_format
    try:
        convert_format(args.input, args.output, args.type)
        print(f"✅ 转换完成: {args.output}")
    except Exception as e:
        print(f"❌ 转换失败: {str(e)}")
        exit(1)


def resolve_datasets(args) -> List[str]:
    """解析数据集参数，支持--run-all时自动加载对应类型的所有数据集"""
    if args.run_all:
        data_dir = Path(__file__).parent / 'dataset' / args.form
        return [f.stem for f in data_dir.glob('*.*') if f.suffix in ('.csv', '.jsonl')]
    return args.set if args.set else []

if __name__ == '__main__':
    main()