# CEDAR-based temporal causal analysis of a batch distillation column

本仓库提供论文《基于 CEDAR 的乙酰氯间歇精馏过程时序因果关系分析》的复现代码与已保存结果。
获得受限过程数据的使用授权后，可从 DCS 记录复算描述统计、自相关与相关性诊断，
读取 CEDAR 结果，并重新生成论文中 Fig. 1–Fig. 6 的插图（300 dpi PNG + 矢量 PDF）。
过程数据不在此公开仓库中分发。

## 数据口径

| 项目 | 值 |
|---|---|
| 测点数量 | 27 |
| 记录间隔 | 4 s |
| 记录长度 | 24 345 行（27.05 h） |
| 起始时刻 | 2026-09-16 04:25:22 |
| 结束时刻 | 2026-09-17 07:28:18 |
| 变量命名 | `<设备组>-<量类型><序号>`，如 `KTL-T1` 为精馏釜 T1 温度 |

`data/process_4s.csv` 是复算所需的受限过程数据，**不包含在本仓库中**；
上表为该数据的记录口径，不表示数据可公开获取。
`data/cedar_4s.joblib` 为 CEDAR 计算结果对象（causalts `CedarResult`），
`data/cedar_edges_4s.csv` 为由此导出的 75 条边表。

## 目录

```
.
├── cedar_repro.ipynb          # 主入口：使用受限数据复算分析与图表
├── requirements.txt
├── data/                      # CEDAR 结果、边表；不含过程数据
├── src/
│   ├── analysis.py            # 统计、阶段划分、自相关、相关性、拓扑分级
│   ├── fig1_process.py        # Fig.1 工艺与测点布置图
│   └── figures.py             # Fig.2–Fig.6
├── outputs/                   # 分析中间结果（csv/json）
└── figures/                   # 生成图件（png/pdf）
```

## 运行

运行 notebook 或依赖原始测点的脚本前，须自行取得过程数据使用授权，
并将其置于 `data/process_4s.csv`。仓库内的 `outputs/` 和 `figures/` 提供已保存的分析结果与图件。

```bash
python -m pip install -r requirements.txt
jupyter lab cedar_repro.ipynb      # 或
python src/analysis.py && python src/fig1_process.py && python src/figures.py
```

分析代码不含抽样或模型训练；具备受限过程数据及相应环境时，可按上述步骤复算。
CEDAR 推断本身为确定性算法，但其运行需 GPU 与数小时机时，
故本包直接分发计算结果 `cedar_4s.joblib`，不做在线重训。

## 复现要点

1. `cedar_4s.joblib` 中的 `cg_tig[i, j, k]` 表示**由变量 i 指向变量 j、滞后 k 步**的边；
   本数据 lag0 为 0、lag1 共 75 条（27 条自回归 + 48 条跨测点）。
2. `n_tests = 1323 = 27 × 26 × 1.89…` 的成对条件独立检验次数由 CEDAR 内部候选筛选决定。
3. 48 条跨测点边的拓扑分级（同单元 / 顺流相邻 / 逆流相邻 / 跨单元远端）依据图 1 的设备连接关系。
4. 图件配色为 Okabe–Ito 色盲友好序列，正文字体为 Arial / 微软雅黑，版心宽 190 mm。

## 许可

过程数据不在本仓库中分发；代码以 MIT 许可发布。
