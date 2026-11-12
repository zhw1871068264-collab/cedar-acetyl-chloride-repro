# CEDAR-based temporal causal analysis of a batch distillation column

本仓库是论文《基于 CEDAR 的乙酰氯间歇精馏过程时序因果关系分析》的**完整复现包**：
从 DCS 记录出发，复算全部描述统计、自相关与相关性诊断，读取 CEDAR 结果，
并生成论文中 Fig. 1–Fig. 6 的全部出版级插图（300 dpi PNG + 矢量 PDF）。

## 数据口径

| 项目 | 值 |
|---|---|
| 测点数量 | 27 |
| 记录间隔 | 4 s |
| 记录长度 | 24 345 行（27.05 h） |
| 起始时刻 | 2026-09-16 04:25:22 |
| 结束时刻 | 2026-09-17 07:28:18 |
| 变量命名 | `<设备组>-<量类型><序号>`，如 `KTL-T1` 为精馏釜 T1 温度 |

`data/process_4s.csv` 为脱敏后的分析用数据表，列名即 27 个匿名测点标识；
`data/cedar_4s.joblib` 为 CEDAR 计算结果对象（causalts `CedarResult`），
`data/cedar_edges_4s.csv` 为由此导出的 75 条边表。

## 目录

```
.
├── cedar_repro.ipynb          # 主入口：逐步复现论文数据、诊断与图表
├── requirements.txt
├── data/                      # 4 s 记录、CEDAR 结果、边表
├── src/
│   ├── analysis.py            # 统计、阶段划分、自相关、相关性、拓扑分级
│   ├── fig1_process.py        # Fig.1 工艺与测点布置图
│   └── figures.py             # Fig.2–Fig.6
├── outputs/                   # 分析中间结果（csv/json）
└── figures/                   # 生成图件（png/pdf）
```

## 运行

```bash
python -m pip install -r requirements.txt
jupyter lab cedar_repro.ipynb      # 或
python src/analysis.py && python src/fig1_process.py && python src/figures.py
```

全部随机性为零（无抽样、无模型训练），结果可逐位复现。
CEDAR 推断本身为确定性算法，但其运行需 GPU 与数小时机时，
故本包直接分发计算结果 `cedar_4s.joblib`，不做在线重训。

## 复现要点

1. `cedar_4s.joblib` 中的 `cg_tig[i, j, k]` 表示**由变量 i 指向变量 j、滞后 k 步**的边；
   本数据 lag0 为 0、lag1 共 75 条（27 条自回归 + 48 条跨测点）。
2. `n_tests = 1323 = 27 × 26 × 1.89…` 的成对条件独立检验次数由 CEDAR 内部候选筛选决定。
3. 48 条跨测点边的拓扑分级（同单元 / 顺流相邻 / 逆流相邻 / 跨单元远端）依据图 1 的设备连接关系。
4. 图件配色为 Okabe–Ito 色盲友好序列，正文字体为 Arial / 微软雅黑，版心宽 190 mm。

## 许可

数据为脱敏工业记录，仅用于学术复现；代码以 MIT 许可发布。
