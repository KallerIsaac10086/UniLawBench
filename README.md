
<div align="center">
  <img width="500" src="https://raw.githubusercontent.com/your-org/UniLawBench/main/figs/UniLawBench_logo.png" alt="UniLawBench" />
</div>

<h1 align="center">UniLawBench · PyPI 版</h1>
<p align="center">
  <a href="https://pypi.org/project/unilawbench"><img src="https://img.shields.io/pypi/v/unilawbench?color=brightgreen" alt="PyPI"></a>
  <a href="https://github.com/modelscope/evalscope"><img src="https://img.shields.io/badge/EvalScope-%E2%9C%94-blue" alt="EvalScope"></a>
  <a href="https://github.com/your-org/UniLawBench"><img src="https://img.shields.io/badge/GitHub-Repo-black" alt="GitHub"></a>
</p>

---

## 🗂️ 项目简介
**UniLawBench** 是面向中文法律场景的大模型评测工具。  
PyPI 版内置全部 20 个任务数据，并通过 `console_scripts` 将主程序注册为 **`unilawbench`** 命令，真正实现 _pip → run_ 开箱即用。  
此外，本版本还集成了 **PyQt5** 图形界面，用户可通过命令行直接启动图形界面，完成模型选择、数据转换等操作。

> ⚠️ 包含完整数据集，不必再单独下载。

---

## 📦 安装

```bash
python -m pip install --upgrade pip
pip install unilawbench
```

安装时会自动拉取 `evalscope[all]` 及其依赖（包含 OpenCompass/VLMEvalKit 等后端）。同时，**PyQt5** 会作为依赖自动安装。

---

## 🚀 快速上手

### 1. 评测 (`eval`)
```bash
# 评估所有选择题数据集
unilawbench eval -form mcq --run-all -model ./weights

# 只评估 1-1、2-5 两个问答数据集
unilawbench eval -form qa -set 1-1 2-5 -model ./weights
```

### 2. 数据转换 (`convert`)
```bash
# JSON ↦ CSV（多选）
unilawbench convert --type mcq data/2-2.json data/2-2.csv

# JSON ↦ JSONL（纠纷焦点）
unilawbench convert --type focus data/focus.json data/focus.jsonl
```

---

## 🖥️ 启动图形界面

### 3. 启动图形界面
```bash
unilawbench gui
```

运行此命令后，会启动一个带有选项卡的 PyQt5 窗口，用户可以通过界面选择模型路径、进行文件转换等操作。

---

## 📚 任务列表（完整 20 项）

| 认知水平 | ID   | 任务名称                     | 数据源              | 指标                       | 类型 |
| -------- | ---- | ---------------------------- | ------------------- | -------------------------- | ---- |
| **法律知识记忆** | 1-1 | 法条背诵                   | FLK                 | ROUGE-L                    | 生成 |
|          | 1-2 | 知识问答                     | JEC_QA              | Accuracy                   | 单选 |
| **法律知识理解** | 2-1 | 文件校对                   | CAIL2022            | F<sub>0.5</sub>            | 生成 |
|          | 2-2 | 纠纷焦点识别                 | LAIC2021            | F1                         | 多选 |
|          | 2-3 | 婚姻纠纷鉴定                 | AIStudio            | F1                         | 多选 |
|          | 2-4 | 问题主题识别                 | CrimeKgAssitant     | Accuracy                   | 单选 |
|          | 2-5 | 阅读理解                     | CAIL2019            | rc-F1                      | 抽取 |
|          | 2-6 | 命名实体识别                 | CAIL2021            | soft-F1                    | 抽取 |
|          | 2-7 | 舆情摘要                     | CAIL2022            | ROUGE-L                    | 生成 |
|          | 2-8 | 论点挖掘                     | CAIL2022            | Accuracy                   | 单选 |
|          | 2-9 | 事件检测                     | LEVEN               | F1                         | 多选 |
|          | 2-10 | 触发词提取                   | LEVEN               | soft-F1                    | 抽取 |
| **法律知识应用** | 3-1 | 法条预测（基于事实）       | CAIL2018            | F1                         | 多选 |
|          | 3-2 | 法条预测（基于场景）         | LawGPT_zh Project   | ROUGE-L                    | 生成 |
|          | 3-3 | 罪名预测                     | CAIL2018            | F1                         | 多选 |
|          | 3-4 | 刑期预测（无法条内容）       | CAIL2018            | Normalized log-distance    | 回归 |
|          | 3-5 | 刑期预测（给定法条内容）     | CAIL2018            | Normalized log-distance    | 回归 |
|          | 3-6 | 案例分析                     | JEC_QA              | Accuracy                   | 单选 |
|          | 3-7 | 犯罪金额计算                 | LAIC2021            | Accuracy                   | 回归 |
|          | 3-8 | 咨询                         | hualv.com           | ROUGE-L                    | 生成 |

---

## 🛠️ 目录结构

```
unilawbench/
├─ cli.py                 # 主入口
├─ dataset/               # 内置数据集 (mcq / qa)
├─ utils/                 # 数据转换等工具
├─ gui/                   # PyQt5 图形界面 (window.py)
└─ ...
```

---

## 📜 许可证

- **代码**：Apache-2.0  
- **数据**：遵循各上游数据集许可证，详见 `dataset/README.md`

---

## 📑 引用

```bibtex
@article{fei2023lawbench,
  title   = {LawBench: Benchmarking Legal Knowledge of Large Language Models},
  author  = {Fei, Zhiwei and Shen, Xiaoyu and others},
  journal = {arXiv preprint arXiv:2309.16289},
  year    = {2023}
}
```

> 如果 UniLawBench 对您的研究或业务有帮助，请引用上文，并在文中注明使用本工具 🙏
