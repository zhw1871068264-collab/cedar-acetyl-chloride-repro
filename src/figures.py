"""Fig 2–6：批次运行剖面、CEDAR 网络、强度排名、工艺预期对照、数据诊断。"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib.patches import Circle, FancyArrowPatch
import matplotlib.patheffects as pe

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "process_4s.csv"
EDGES = ROOT / "outputs" / "edges_48_classified.csv"
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.family": "Microsoft YaHei",
    "font.size": 7.6,
    "axes.linewidth": 0.6,
    "axes.edgecolor": "#4D4D4D",
    "xtick.direction": "out",
    "ytick.direction": "out",
    "legend.frameon": True,
    "legend.framealpha": 0.92,
    "legend.edgecolor": "none",
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
})

C = {"JKT": "#D55E00", "KTL": "#E69F00", "COL": "#009E73",
     "CND": "#0072B2", "RFD": "#CC79A7", "ITK": "#6F6F6F"}
GRID = dict(color="#E2E2E2", linewidth=0.45)

df = pd.read_csv(DATA, parse_dates=["timestamp"])
edges = pd.read_csv(EDGES)

stats = json.loads((ROOT / "outputs" / "stats.json").read_text(encoding="utf-8"))


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"{name}.{ext}", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", name)


# ================= Fig 2 批次运行剖面 =================
t = df.timestamp
lvl = df["RFD-L1"]
t_fill = t[(lvl > 900) & (lvl.shift(3) <= 900)]
t_drop = t[(lvl < 200) & (lvl.shift(3) > 500)]
t_start, t_end = t.iloc[0], t.iloc[-1]
b_fill = t_fill.iloc[0] if len(t_fill) else t.iloc[int(len(t) * 0.2)]
b_drop = t_drop.iloc[0] if len(t_drop) else t.iloc[int(len(t) * 0.8)]

prod = df["RFD-F1"].rolling(9, center=True, min_periods=1).mean()
idx = np.flatnonzero((prod > prod.max() * 0.25).values)
d0, d1 = (t.iloc[idx[0]], t.iloc[idx[-1]]) if idx.size else (b_fill, b_drop)

fig, axes = plt.subplots(4, 1, figsize=(7.28, 6.9), sharex=True,
                         gridspec_kw=dict(hspace=0.24))
bands = [(t_start, b_fill, "建立回流", "#F7F7F7"),
         (b_fill, b_drop, "精馏与采出", "#EFEFEF"),
         (b_drop, t_end, "卸料与降温", "#F7F7F7")]
for ax in axes:
    for a, b, lab, col in bands:
        ax.axvspan(a, b, color=col, zorder=0, lw=0)
    ax.axvspan(d0, d1, color="#FCE9C9", zorder=0, lw=0, alpha=0.9)
    ax.grid(True, **GRID)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

axes[0].plot(t, df["KTL-T1"], color=C["KTL"], lw=0.9, label="釜温 KTL-T1")
axes[0].plot(t, df["COL-T1"], color=C["COL"], lw=0.9, label="塔顶温 COL-T1")
axes[0].plot(t, df["COL-T4"], color="#3C8C74", lw=0.8, ls="--", label="塔底温 COL-T4")
axes[0].set_ylabel("温度 / ℃")
axes[0].set_ylim(20, 138)
axes[0].legend(ncol=3, loc="upper left", fontsize=6.3, handlelength=1.6)

axes[1].plot(t, df["CND-T1"], color="#4C9BD1", lw=0.8, label="循环水出口 CND-T1")
axes[1].plot(t, df["CND-TA2"], color="#0072B2", lw=0.9, label="一级冷凝出口 CND-TA2")
axes[1].plot(t, df["CND-TA1"], color="#7FC9E8", lw=0.8, label="二级冷凝出口 CND-TA1")
axes[1].plot(t, df["CND-T4"], color="#123B66", lw=0.8, label="盐水Ⅱ出口 CND-T4")
axes[1].set_ylabel("温度 / ℃")
axes[1].set_ylim(-30, 62)
axes[1].legend(ncol=2, loc="upper left", fontsize=6.2, handlelength=1.6)

axes[2].plot(t, df["RFD-L1"] / df["RFD-L1"].max(), color=C["RFD"], lw=0.9, label="回流罐液位")
axes[2].plot(t, df["ITK-L1"] / df["ITK-L1"].max(), color=C["ITK"], lw=0.8, ls="--",
             label="中间罐液位")
axes[2].plot(t, df["RFD-F1"] / df["RFD-F1"].max(), color="#7B3294", lw=0.8, label="成品采出流量")
axes[2].set_ylabel("归一化值")
axes[2].set_ylim(-0.08, 1.18)
axes[2].legend(ncol=3, loc="upper left", fontsize=6.2, handlelength=1.6)

axes[3].plot(t, (df["JKT-P1"] - df["JKT-P1"].min()) / (df["JKT-P1"].max() - df["JKT-P1"].min()),
             color=C["JKT"], lw=0.9, label="夹套压力 JKT-P1")
axes[3].plot(t, (df["COL-P1"] - df["COL-P1"].min()) / (df["COL-P1"].max() - df["COL-P1"].min()),
             color=C["COL"], lw=0.8, label="塔顶压力 COL-P1")
axes[3].set_ylabel("归一化值")
axes[3].set_ylim(-0.15, 1.35)
axes[3].legend(ncol=2, loc="upper left", fontsize=6.2, handlelength=1.6)
axes[3].set_xlabel("时间（2026-09-16 至 09-17）")

axes[3].xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=8))
axes[3].xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
for lab in axes[3].get_xticklabels():
    lab.set_fontsize(6.4)

for a, b, lab, _ in bands:
    axes[0].text(a + (b - a) / 2, 116.0, lab, ha="center", va="top",
                 fontsize=6.6, color="#555555")
fig.text(0.5, -0.008, "灰色分区依据回流罐液位转折点划分运行阶段；浅黄色为成品采出流量活跃窗口。"
                      "第 3、4 子图为各自归一化后的无量纲值。",
         ha="center", fontsize=6.0, color="#555555")
save(fig, "Fig2_batch_profile")


# ================= Fig 3 CEDAR 网络 =================
pos = {
    "JKT-F1": (5, 74), "JKT-P1": (5, 64), "JKT-T1": (5, 54),
    "KTL-T1": (20, 66), "KTL-P1": (20, 56), "KTL-I1": (20, 46),
    "COL-P1": (34, 82), "COL-P2": (34, 72), "COL-P3": (34, 62),
    "COL-T1": (40, 78), "COL-T2": (40, 68), "COL-T3": (40, 58), "COL-T4": (40, 48),
    "CND-T1": (56, 84), "CND-T2": (56, 75), "CND-T3": (56, 66), "CND-T4": (56, 57),
    "CND-TA1": (62, 78), "CND-TA2": (62, 69),
    "RFD-L1": (74, 46), "RFD-P1": (74, 38), "RFD-T1": (74, 30), "RFD-F1": (68, 22),
    "ITK-L1": (88, 44), "ITK-P1": (88, 36), "ITK-T1": (88, 28), "ITK-V1": (88, 20),
}
grp = {}
for g, vs in {"JKT": ["JKT-F1", "JKT-P1", "JKT-T1"],
              "KTL": ["KTL-T1", "KTL-P1", "KTL-I1"],
              "COL": ["COL-P1", "COL-P2", "COL-P3", "COL-T1", "COL-T2", "COL-T3", "COL-T4"],
              "CND": ["CND-T1", "CND-T2", "CND-T3", "CND-T4", "CND-TA1", "CND-TA2"],
              "RFD": ["RFD-L1", "RFD-P1", "RFD-T1", "RFD-F1"],
              "ITK": ["ITK-L1", "ITK-P1", "ITK-T1", "ITK-V1"]}.items():
    for v in vs:
        grp[v] = g

fig, ax = plt.subplots(figsize=(7.28, 5.2))
ax.set_xlim(0, 98)
ax.set_ylim(10, 94)
ax.axis("off")

topo_style = {"同单元": ("#1B1B1B", "-", 1.0), "顺流相邻": ("#009E73", "-", 0.95),
              "逆流相邻": ("#D55E00", "--", 0.9), "跨单元远端": ("#9E9E9E", ":", 0.8)}
for r in edges.itertuples():
    p1, p2 = pos[r.src], pos[r.dst]
    color, ls, base = topo_style[r.拓扑关系]
    lw = 0.5 + 3.2 * (np.log10(max(r.绝对强度, 1e-7)) + 6) / 4.8
    lw = float(np.clip(lw, 0.35, 3.4))
    rad = 0.24 if r.拓扑关系 == "跨单元远端" else 0.10
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=5.5,
                                 connectionstyle=f"arc3,rad={rad}", color=color,
                                 lw=lw, linestyle=ls, alpha=0.50 + 0.50 * base,
                                 zorder=2, shrinkA=1.8, shrinkB=2.2))

for name, (x, y) in pos.items():
    ax.add_patch(Circle((x, y), 1.5, facecolor=C[grp[name]], edgecolor="white",
                        linewidth=1.1, zorder=4))
    ax.text(x, y - 2.6, name, ha="center", va="top", fontsize=5.3, color="#222222",
            zorder=6, bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.78))

for gname, gx in [("夹套蒸汽", 5), ("精馏釜", 20), ("精馏塔", 37), ("分级冷凝", 59),
                  ("回流罐", 74), ("中间罐", 88)]:
    ax.text(gx, 90.6, gname, ha="center", fontsize=6.6, color="#111111")

handles = [plt.Line2D([], [], color=topo_style[k][0], ls=topo_style[k][1],
                      lw=topo_style[k][2] * 1.3, label=f"{k}（{v}）")
           for k, v in [("同单元", 3), ("顺流相邻", 9), ("逆流相邻", 6), ("跨单元远端", 30)]]
ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.0, 0.0), fontsize=6.4,
          ncol=2, handlelength=2.0, title="边的设备拓扑关系（共 48 条）", title_fontsize=6.4)
ax.text(0.0, -0.045, "线宽按 |边强度| 的对数尺度映射；箭头表示算法方向，不等同于已确认的物理因果关系。",
        transform=ax.transAxes, fontsize=5.9, color="#555555")
save(fig, "Fig3_cedar_network")


# ================= Fig 4 强度前 15 =================
top = edges.head(15).iloc[::-1]
fig, ax = plt.subplots(figsize=(7.28, 3.5))
for i, r in enumerate(top.itertuples()):
    color = topo_style[r.拓扑关系][0]
    ax.hlines(i, 1e-5, r.绝对强度, color=color, lw=1.5, alpha=0.85)
    ax.plot(r.绝对强度, i, "o", ms=5.2, color=color, zorder=3)
    ax.text(r.绝对强度 * 1.35, i, f"{r.强度:+.5f}", va="center", fontsize=6.3, color="#333333")
ax.set_xscale("log")
ax.set_xlim(1e-5, 6e-1)
ax.set_ylim(-0.8, 14.8)
ax.set_yticks(np.arange(len(top)))
ax.set_yticklabels([f"{r.src} → {r.dst}" for r in top.itertuples()], fontsize=6.6)
ax.set_xlabel("|CEDAR 边强度统计量|（对数坐标）")
ax.grid(True, axis="x", **GRID)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.tick_params(axis="y", length=0)
hl = [plt.Line2D([], [], color=topo_style[k][0], lw=1.6, marker="o", ms=5, label=k)
      for k in ["同单元", "顺流相邻", "逆流相邻", "跨单元远端"]]
ax.legend(handles=hl, fontsize=6.3, ncol=4, loc="lower left", bbox_to_anchor=(0.0, -0.02))
ax.text(0.0, 1.03, "数值为边强度统计量，仅表示算法内部相对强弱，不是物理效应系数",
        transform=ax.transAxes, fontsize=6.1, color="#555555")
save(fig, "Fig4_top15_strength")


# ================= Fig 5 工艺预期与检出对照 =================
fig, axes = plt.subplots(1, 2, figsize=(7.28, 1.95),
                         gridspec_kw=dict(width_ratios=[1.12, 1], wspace=0.26))

def stacked(ax, vals, labs, cols, total, title, sub):
    left = 0
    for v, l, c in zip(vals, labs, cols):
        ax.barh([0], [v], left=left, height=0.55, color=c, edgecolor="white", lw=1.0)
        ax.text(left + v / 2, 0, str(v), ha="center", va="center", fontsize=8.5,
                color="white" if c != "#C9C9C9" else "#333333")
        left += v
    ax.set_xlim(0, total)
    ax.set_ylim(-0.62, 0.62)
    ax.set_yticks([])
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="x", labelsize=6.4)
    ax.set_xlabel(f"{total} 条关系　{sub}", fontsize=6.4, labelpad=3)
    ax.set_title(title, fontsize=7.2, loc="left", pad=5)
    hs = [plt.Rectangle((0, 0), 1, 1, facecolor=c) for c in cols]
    ax.legend(hs, labs, fontsize=6.0, ncol=3, loc="upper left",
              bbox_to_anchor=(0.0, -0.36), handlelength=1.1, columnspacing=1.2,
              handletextpad=0.5)

stacked(axes[0], [4, 2, 21], ["同向检出", "骨架一致但反向", "未检出"],
        ["#009E73", "#D55E00", "#C9C9C9"], 27, "（a）以 27 条工艺预期为参照",
        "同向 14.8%，反向 7.4%，未检出 77.8%")
stacked(axes[1], [7, 20, 21], ["直接或较强依据", "间接或闭环反馈", "缺少资料支持"],
        ["#009E73", "#E69F00", "#C9C9C9"], 48, "（b）以 48 条算法边为对象",
        "有依据 14.6%，间接 41.7%，无支持 43.8%")
save(fig, "Fig5_expectation_vs_detected")


# ================= Fig 6 数据诊断 =================
def acf_curve(x, n=40):
    x = np.asarray(x, float)
    x = x - x.mean()
    v = np.dot(x, x)
    return np.array([np.dot(x[:-k], x[k:]) / v if k else 1.0 for k in range(n)])


rep = [("KTL-T1", "KTL"), ("JKT-P1", "JKT"), ("COL-T1", "COL"),
       ("CND-T1", "CND"), ("RFD-L1", "RFD"), ("ITK-V1", "ITK")]
fig, ax = plt.subplots(figsize=(7.28, 3.3))

lags = np.arange(40) * 4
for name, g in rep:
    ax.plot(lags, acf_curve(df[name]), color=C[g], lw=0.9, label=name)
ax.set_xlabel("时间滞后 / s（记录间隔 4 s）")
ax.set_ylabel("自相关函数")
ax.set_ylim(0, 1.02)
ax.grid(True, **GRID)
ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.legend(fontsize=5.8, ncol=3, loc="lower left", handlelength=1.2, columnspacing=0.9)
ax.set_title("代表性变量的自相关衰减", fontsize=7.0, loc="left", pad=6)
ax.text(0.40, 0.86, "27 个变量的一步自相关\n中位数 %.3f，最小值 %.3f"
        % (stats["acf_median"], stats["acf_min"]), transform=ax.transAxes,
        fontsize=6.1, color="#444444", va="top")
save(fig, "Fig6_data_diagnostics")

print("all figures done")
