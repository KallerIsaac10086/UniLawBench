
<h1 align="center">UniLawBench —— 原生兼容 EvalScope 的中文法律大模型评测基准</h1>
<p align="center">
  🌐 <a href="https://github.com/KallerIsaac10086/UniLawBench/" target="_blank">GitHub</a> • 📑 <a href="https://arxiv.org/abs/2309.16289" target="_blank">背景论文</a> • ⚖️ <a href="https://github.com/open-compass/LawBench/tree/main/data">任务数据</a> • 🛠️ <a href="https://github.com/modelscope/evalscope" target="_blank">EvalScope</a> • 📦 <a href="https://pypi.org/project/unilawbench">PyPI</a> • 📦 <a href="https://github.com/KallerIsaac10086/UniLawBench/tree/pypi">Pypi版源代码</a>
</p>
<p align="center">
   📖 <a href="README.md">中文</a> | <a href="README_EN.md">English</a>
</p>

---

## ✨ 项目简介
**UniLawBench** 是在 LawBench 基准上进行轻量化重构的法律大模型评测框架，保留了 20 项任务（记忆 → 理解 → 应用），并与 **EvalScope** 深度集成。  
- **main 分支**：开发 & 扩展；  
- **pipy 分支**：PyPI 打包源码。  

| 模块 | LawBench | UniLawBench |
| :-- | :-- | :-- |
| 执行引擎 | OpenCompass + 私有脚本 | **EvalScope 原生**（本地 / Studio） |
| 依赖 | notebook、旧实验结果 | `pip install unilawbench`，体积 < 60 MB |
| CLI | 无统一入口 | `ulb eval / convert / download-data` |
| 数据 | 手动 clone | `ulb download-data` 一键拉取（≈ 5 GB） |

---

## 📦 安装

### 1. PyPI（推荐）
```bash
python -m pip install --upgrade pip
pip install unilawbench
ulb download-data ./data
```

### 2. GitHub 源码
```bash
pip install git+https://github.com/your-org/UniLawBench.git
```

### 3. 开发模式
```bash
git clone https://github.com/your-org/UniLawBench.git
cd UniLawBench
pip install -e ".[dev]"
```

---

## 🏃‍♂️ 快速上手

### 评测 (`eval`)
| 场景 | 示例 |
|------|------|
| 全量零样本 | `ulb eval --model gpt-4o --mode zero-shot` |
| 本地 one-shot | `ulb eval --model ./weights/chatglm2-6b --mode one-shot` |
| 仅选择题 | `ulb eval -f mcq --run-all --model ./legal_llm` |
| 指定数据集 | `ulb eval -f qa -s 3-5 4-2 --model ./legal_llm` |
| Studio 远程 | `ulb eval-remote --model-id iic/Qwen-7B-Chat --token <studio_token>` |

### 数据转换 (`convert`)
```bash
# JSON → CSV（多选）
ulb convert --type mcq data/2-2.json data/2-2.csv
# JSON → JSONL（焦点识别）
ulb convert --type focus data/2-2.json data/2-2.jsonl
```

---

## 📚 任务列表

| 认知水平 | ID  | 任务 | 数据源 | 指标 | 类型 |
|----------|-----|------|--------|------|------|
| **法律知识记忆** | 1-1 | 法条背诵 | FLK | ROUGE-L | 生成 |
| | 1-2 | 知识问答 | JEC_QA | Accuracy | 单选 |
| **法律知识理解** | 2-1 | 文件校对 | CAIL2022 | F0.5 | 生成 |
| | 2-2 | 纠纷焦点识别 | LAIC2021 | F1 | 多选 |
| | 2-3 | 婚姻纠纷鉴定 | AIStudio | F1 | 多选 |
| | 2-4 | 问题主题识别 | CrimeKgAssitant | Accuracy | 单选 |
| | 2-5 | 阅读理解 | CAIL2019 | rc-F1 | 抽取 |
| | 2-6 | 命名实体识别 | CAIL2021 | soft-F1 | 抽取 |
| | 2-7 | 舆情摘要 | CAIL2022 | ROUGE-L | 生成 |
| | 2-8 | 论点挖掘 | CAIL2022 | Accuracy | 单选 |
| | 2-9 | 事件检测 | LEVEN | F1 | 多选 |
| | 2-10 | 触发词提取 | LEVEN | soft-F1 | 抽取 |
| **法律知识应用** | 3-1 | 法条预测（基于事实） | CAIL2018 | F1 | 多选 |
| | 3-2 | 法条预测（基于场景） | LawGPT_zh Project | ROUGE-L | 生成 |
| | 3-3 | 罪名预测 | CAIL2018 | F1 | 多选 |
| | 3-4 | 刑期预测（无法条内容） | CAIL2018 | Normalized log-distance | 回归 |
| | 3-5 | 刑期预测（给定法条内容） | CAIL2018 | Normalized log-distance | 回归 |
| | 3-6 | 案例分析 | JEC_QA | Accuracy | 单选 |
| | 3-7 | 犯罪金额计算 | LAIC2021 | Accuracy | 回归 |
| | 3-8 | 咨询 | hualv.com | ROUGE-L | 生成 |

---

## 🔧 扩展指南
| 场景 | 步骤 |
|------|------|
| 新增任务 | 将 `<id>.json` 放入 `data/` + 对应 YAML 到 `configs/tasks/` |
| 自定义指标 | 在 `ulb/metrics/` 实现或在 YAML 引用 EvalScope 内置指标 |
| 复算旧预测 | `ulb score --pred-dir <predictions>` |

---

## 许可证
- **代码**：Apache-2.0  
- **数据**：遵循各自原始许可证，详见 `data/README.md`。

---

## 引用
```bibtex
@article{fei2023lawbench,
  title   = {LawBench: Benchmarking Legal Knowledge of Large Language Models},
  author  = {Fei, Zhiwei and Shen, Xiaoyu and others},
  journal = {arXiv preprint arXiv:2309.16289},
  year    = {2023}
}
```

> 若 UniLawBench 对您的研究或产品有帮助，请引用上述论文并在文中注明使用了本评测框架 🙏。
