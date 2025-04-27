from evalscope import TaskConfig, run_task

task_cfg = TaskConfig(
    model='/root/autodl-tmp/text-generation-webui-2.7/models/Qwen2.5-7B-1M',
    datasets=['general_qa'],  # 数据格式，选择题格式固定为 'general_qa'
    dataset_args={
        'general_qa': {
            "local_path": "/root/LawBench-eval/text",  # 自定义数据集路径
            "subset_list": [
                "1-1法条背诵",
                "2-1文件校对",
                "2-2纠纷焦点识别",
                "2-3婚姻纠纷鉴定",
                "2-4问题主题识别",
                "2-5阅读理解",
                "2-6命名实体识别",
                "2-7舆情摘要",
                "2-9事件检测",
                "2-10触发词提取",
                "3-1法条预测(基于事实)",
                "3-2法条预测(基于场景)",
                "3-3罪名预测",
                "3-4刑期预测(无法条内容)",
                "3-5刑期预测(给定法条内容)",
                "3-7犯罪金额计算",
                "3-8咨询" # 评测数据集名称，上述 *.jsonl 中的 *
            ]
        }
    },
)

run_task(task_cfg=task_cfg)