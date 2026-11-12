"""定量分析：4 s 网格重建、变量统计、阶段识别、自相关、拓扑分组。"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "process_4s.csv"
EDGES = ROOT / "data" / "cedar_edges_4s.csv"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

# ---------- 1. 4 s 网格 ----------
df = pd.read_csv(DATA, parse_dates=["timestamp"])
dt = df.timestamp.diff().dt.total_seconds().dropna()
assert (dt == 4).all(), "记录间隔应为 4 s，实际出现非 4 s 步长"
vars_ = list(df.columns[1:])
T = len(df)

groups = {
    "JKT": ["JKT-F1", "JKT-T1", "JKT-P1"],
    "KTL": ["KTL-T1", "KTL-P1", "KTL-I1"],
    "COL": ["COL-P1", "COL-P2", "COL-P3", "COL-T1", "COL-T2", "COL-T3", "COL-T4"],
    "CND": ["CND-T1", "CND-T2", "CND-T3", "CND-T4", "CND-TA1", "CND-TA2"],
    "RFD": ["RFD-L1", "RFD-P1", "RFD-T1", "RFD-F1"],
    "ITK": ["ITK-L1", "ITK-P1", "ITK-T1", "ITK-V1"],
}
grp_of = {v: g for g, vs in groups.items() for v in vs}

# ---------- 2. 变量统计 ----------
desc = df[vars_].describe(percentiles=[0.05, 0.5, 0.95]).T
desc["group"] = [grp_of[v] for v in desc.index]
desc.round(4).to_csv(OUT / "variable_statistics.csv", encoding="utf-8-sig")

# ---------- 3. 阶段识别 ----------
t0, t1 = df.timestamp.iloc[0], df.timestamp.iloc[-1]
hours = (t1 - t0).total_seconds() / 3600
kt = df["KTL-T1"].rolling(31, center=True, min_periods=1).mean()
dkt = kt.diff(30) / 120.0                       # ℃/min, 30 步 = 2 min
prod = df["RFD-F1"].rolling(31, center=True, min_periods=1).mean()

heat = dkt > 0.05
ramp_idx = np.flatnonzero(heat.values)
prod_act = prod > (prod.max() * 0.15)
prod_idx = np.flatnonzero(prod_act.values)

stages = {}
if ramp_idx.size:
    stages["升温段"] = [df.timestamp.iloc[ramp_idx[0]], df.timestamp.iloc[ramp_idx[-1]]]
if prod_idx.size:
    stages["采出活跃段"] = [df.timestamp.iloc[prod_idx[0]], df.timestamp.iloc[prod_idx[-1]]]

# 用分位数把全过程切成 6 段，给出每段的釜温/塔温/液位中位数
df["seg"] = pd.qcut(np.arange(T), 6, labels=False)
seg_tab = df.groupby("seg").agg(
    起始=("timestamp", "first"), 结束=("timestamp", "last"),
    釜温=("KTL-T1", "median"), 塔顶温=("COL-T1", "median"),
    夹套压=("JKT-P1", "median"), 回流罐液位=("RFD-L1", "median"),
    采出流量=("RFD-F1", "median"), 中间罐液位=("ITK-L1", "median"),
).round(3)
seg_tab.to_csv(OUT / "segment_profile.csv", encoding="utf-8-sig")

# ---------- 4. 自相关：AR(1) 强度 ----------
def acf1(x):
    x = pd.Series(x).astype(float)
    if x.std() == 0:
        return np.nan
    return float(np.corrcoef(x[:-1], x[1:])[0, 1])

acf = pd.DataFrame({
    "var": vars_,
    "group": [grp_of[v] for v in vars_],
    "acf_lag1": [acf1(df[v]) for v in vars_],
})
acf.round(4).to_csv(OUT / "autocorr_lag1.csv", index=False, encoding="utf-8-sig")

# ---------- 5. 拓扑分组 ----------
edges = pd.read_csv(EDGES)
edges = edges[edges.auto == False].copy()
ordered_main = {("JKT", "KTL"), ("KTL", "COL"), ("COL", "CND"), ("CND", "RFD"), ("ITK", "RFD")}

def topo(src, dst):
    gs, gd = grp_of[src], grp_of[dst]
    if gs == gd:
        return "同单元"
    if (gs, gd) in ordered_main:
        return "顺流相邻"
    if (gd, gs) in ordered_main:
        return "逆流相邻"
    return "跨单元远端"

edges["源组"] = edges.src.map(grp_of)
edges["目标组"] = edges.dst.map(grp_of)
edges["拓扑关系"] = [topo(s, d) for s, d in zip(edges.src, edges.dst)]
edges["强度"] = edges.val.round(6)
edges["绝对强度"] = edges.val.abs()
edges = edges.sort_values("绝对强度", ascending=False).reset_index(drop=True)
edges.drop(columns=["auto"]).to_csv(OUT / "edges_48_classified.csv", index=False, encoding="utf-8-sig")

topo_counts = edges["拓扑关系"].value_counts().to_dict()
same_unit = int(topo_counts.get("同单元", 0))
adj_flow = int(topo_counts.get("顺流相邻", 0))
adj_rev = int(topo_counts.get("逆流相邻", 0))
far = int(topo_counts.get("跨单元远端", 0))

# ---------- 6. 相关分析未纳入 ----------
# 精馏回路为非线性、非平稳过程，Pearson/Spearman 等线性或秩统计不能作为依赖度量，
# 亦不设互信息等对称基线，故此处不计算相关矩阵，论文中亦不报告任何相关系数。

stats = {
    "rows": int(T),
    "n_vars": len(vars_),
    "start": str(t0),
    "end": str(t1),
    "hours": round(hours, 2),
    "n_edges_total": 75,
    "n_edges_cross": len(edges),
    "n_autoreg": 27,
    "n_tests": 1323,
    "density": round(len(edges) / (27 * 26) * 100, 2),
    "topo_same_unit": same_unit,
    "topo_adj_flow": adj_flow,
    "topo_adj_rev": adj_rev,
    "topo_far": far,
    "acf_median": round(float(acf.acf_lag1.median()), 3),
    "acf_min": round(float(acf.acf_lag1.min()), 3),
    "acf_max": round(float(acf.acf_lag1.max()), 3),
    "acf_over_08": int((acf.acf_lag1 > 0.8).sum()),
    "stage_ramp": [str(x) for x in stages.get("升温段", [])],
    "stage_prod": [str(x) for x in stages.get("采出活跃段", [])],
    "edge_abs_max": round(float(edges["绝对强度"].max()), 6),
    "edge_abs_min": round(float(edges["绝对强度"].min()), 6),
    "edge_abs_sum": round(float(edges["绝对强度"].sum()), 6),
}
(OUT / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps(stats, ensure_ascii=False, indent=2))
print("\n阶段剖面：\n", seg_tab.to_string())
print("\n拓扑分组：", topo_counts)
print("\nACF 中位数 %.3f，>0.8 的变量 %d 个" % (stats["acf_median"], stats["acf_over_08"]))
print("\n未计算相关矩阵：非线性过程中线性与秩相关不作依赖度量")
