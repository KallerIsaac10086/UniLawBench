<h1 align="center">UniLawBench —— 原生兼容 EvalScope 的中文法律大模型评测基准</h1>
<p align="center">
  🌐 <a href="https://github.com/your-org/UniLawBench" target="_blank">GitHub</a> • 📑 <a href="https://arxiv.org/abs/2309.16289" target="_blank">背景论文</a> • ⚖️ <a href="https://github.com/open-compass/LawBench/tree/main/data">任务数据</a> • 🛠️ <a href="https://github.com/modelscope/evalscope" target="_blank">EvalScope</a>
</p>
<p align="center">
   📖 <a href="README.md">中文</a> | <a href="README_EN.md">English</a>
</p>

---

## ✨ 项目简介
**UniLawBench** 是在 LawBench 基准之上，针对 **EvalScope** 生态进行重构与轻量化改进的评测框架【turn0search0】【turn1search0】。  
它保留了 LawBench 的三大认知层次（记忆 / 理解 / 应用）与 20 个中文法律任务，但做了如下关键升级：

| 模块 | LawBench 现状 | UniLawBench 改进 |
| :-- | :-- | :-- |
| 执行引擎 | 自带脚本+OpenCompass | **官方 EvalScope 适配**，支持本地与 ModelScope Studio 一键调用【turn1search0】【turn1search4】 |
| 依赖体积 | 包含旧实验日志、截图、Docker | 纯 `pip install unilawbench`，剔除冗余文件、体积 < 60 MB |
| 数据获取 | 手动 clone | `ulb download-data` 自动拉取核心 JSON（≈ 5 GB） |
| CLI 体验 | 多条 bash | 统一 `ulb eval / eval-remote` 封装 EvalScope Yaml |
| 可扩展性 | 需手动 patch | 插件式任务/指标模板，可复用 EvalScope 100+ 官方指标【turn1search3】【turn1search6】 |

---

## 📦 快速安装
```bash
# Python 3.9+
pip install unilawbench        # 核心 + EvalScope 依赖
ulb download-data ./data       # 下载 20 个任务数据
```
完成后目录仅含 `data/ configs/ ulb/ docs/` 四个核心文件夹，去除了原 LawBench 的实验结果与表格文件，便于二次开发【turn0search0】。

---

## 🏃‍♂️ 快速上手
### 本地评测
```bash
ulb eval --model path/to/ChatGLM2-6B --mode zero-shot \
         --results ./runs/chatglm2_zero
```
命令实际调用 `evalscope run -c configs/unilawbench_zero.yaml`，结束后在 `./runs/chatglm2_zero/` 生成 HTML 报告和 JSON 评分。

### 云端评测（ModelScope Studio）
```bash
ulb eval-remote --model-id "iic/ChatGLM2-6B" --token <studio_token>
```
任务将异步运行并生成 EvalScope 官方报告，可在 Studio Web 端实时查看【turn1search1】。

---

## 📖 数据集与任务
与 LawBench 一致，UniLawBench 含 20 个任务、每项 500 例，覆盖生成、分类、抽取、回归四种输出形式【turn0search0】。

<details>
<summary>点击展开任务列表</summary>

| 认知层次 | 任务 ID | 任务名 | 类型 | 指标 |
| --- | --- | --- | --- | --- |
| 记忆 | 1-1 | 法条背诵 | 生成 | ROUGE-L |
| 记忆 | 1-2 | 知识问答 | 单选 | Accuracy |
| 理解 | 2-1 | 文书校对 | 生成 | F<sub>0.5</sub> |
| … | … | … | … | … |
| 应用 | 3-8 | 法律咨询 | 生成 | ROUGE-L |
</details>

> 详细格式说明见 `docs/tasks.md`【turn0search0】。

---

## ⚙️ 统一 CLI
```bash
ulb  <command>  [options]

主要命令:
  download-data        下载或更新全部任务数据
  eval                 本地评测 (Zero-/One-shot)
  eval-remote          在 ModelScope Studio 远程评测
  score                对已有 prediction 文件重新打分
```

---

## 🧩 如何扩展
| 场景 | 步骤 |
| --- | --- |
| **添加新任务** | 在 `data/` 放入 `<task-id>.json`；在 `configs/tasks/` 添加同名 YAML；即可被 `ulb eval` 自动识别。 |
| **自定义指标** | 在 `ulb/metrics/` 实现函数或直接引用 EvalScope 库指标【turn1search5】。 |
| **使用旧预测** | 将 LawBench 格式的 `predictions/` 复制到项目内，执行 `ulb score --pred-dir …` 即可复算新指标。 |

---

## 🔬 基线结果
| 模型 | Zero-shot Avg | One-shot Avg |
| --- | --- | --- |
| **GPT-4** | 52.35 | 53.85 |
| ChatGPT (23-06-13) | 42.15 | 44.52 |
| Qwen-7B-Chat | 37.00 | 38.99 |
| InternLM-Chat-7B-8K | 35.73 | 37.28 |
| LawGPT-7B-β1.1 | 32.76 | 32.63 |
> 具体按任务拆分的分数及弃权率可见 `docs/leaderboard.md`。【turn0search0】

---

## 📜 许可证
- 代码：Apache-2.0【turn0search3】  
- 每个数据文件保持其原许可证，详见 `data/README.md`。

---

## 🙏 引用
请首先引用 LawBench 原论文，以承认初始任务与评测指标的贡献【turn0search8】：
```bibtex
@article{fei2023lawbench,
  title={LawBench: Benchmarking Legal Knowledge of Large Language Models},
  author={Fei, Zhiwei and Shen, Xiaoyu and Zhu, Dawei et al.},
  journal={arXiv preprint arXiv:2309.16289},
  year={2023}
}
```

---

> UniLawBench 旨在为中文法律大模型提供**轻量化、标准化、可复现**的评测流水线，欢迎社区贡献新任务、指标与基线，共同完善中文法律 AI 生态！
