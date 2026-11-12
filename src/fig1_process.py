"""Fig 1：乙酰氯间歇精馏装置流程与 27 个测点覆盖（出版级重绘，v2）。"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import matplotlib.patheffects as pe
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"

plt.rcParams.update({
    "font.family": "Microsoft YaHei",
    "font.size": 7.5,
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
})

C = {"JKT": "#D55E00", "KTL": "#E69F00", "COL": "#009E73",
     "CND": "#0072B2", "RFD": "#CC79A7", "ITK": "#6F6F6F"}
LINE = "#2B2B2B"
HALO = [pe.withStroke(linewidth=1.8, foreground="white")]

fig, ax = plt.subplots(figsize=(7.48, 4.33))
ax.set_xlim(0, 104)
ax.set_ylim(0, 100)
ax.axis("off")

def box(x, y, w, h, fc="white", ec=LINE, lw=0.9, r=1.2, z=3):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad=0,rounding_size={r}",
                                facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z))

def arrow(x1, y1, x2, y2, color=LINE, lw=0.9, ms=6, rad=0.0, z=2, ls="-", style="-|>"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=ms,
                                 color=color, linewidth=lw, zorder=z, linestyle=ls,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))

def tag(x, y, label, group, ha="left", dx=0.0, leader_to=None):
    """测点圆点 + 位号；可用 leader_to 拉出引线，避免与管线重叠。"""
    if leader_to is not None:
        ax.plot([x, leader_to[0]], [y, leader_to[1]], color="#9E9E9E", lw=0.45,
                ls=(0, (1.2, 1.2)), zorder=5)
    ax.add_patch(Circle(leader_to if leader_to is not None else (x, y), 0.4,
                        facecolor=C[group], edgecolor="white", linewidth=0.7, zorder=6))
    tx = (leader_to[0] if leader_to is not None else x) + dx
    ty = leader_to[1] if leader_to is not None else y
    ax.text(tx, ty, label, ha=ha, va="center", fontsize=6.1, color="#111111",
            zorder=7, path_effects=HALO)

# ---------- 设备 ----------
box(10, 18, 26, 30, fc="#F3F3F3", ec="#9A9A9A", lw=0.8, z=2)       # 夹套
box(12, 20, 22, 26, fc="white", ec=LINE, lw=1.0, z=3)               # 釜体
ax.plot([23, 23], [22, 28.5], color="#555555", lw=1.0, zorder=4)
ax.plot([19.5, 26.5], [28.5, 28.5], color="#555555", lw=0.8, zorder=4)
ax.plot([19.5, 26.5], [24, 24], color="#555555", lw=0.8, zorder=4)
ax.text(23, 32.5, "R12X03", ha="center", fontsize=6.2, color="#333333", zorder=5)

box(42, 24, 8.5, 56, fc="white", ec=LINE, lw=1.0, z=3)              # 塔
for yy in range(28, 78, 4):
    ax.plot([42.3, 50.2], [yy, yy], color="#B0B0B0", lw=0.45, zorder=4)
ax.text(46.2, 21.5, "T12X01", ha="center", fontsize=6.2, color="#333333")

cond_x = [62, 72, 82, 92]
for x, lab in zip(cond_x, ["E12X08", "E12X09", "E12X10", "E12X11"]):
    box(x, 56, 6.5, 26, fc="white", ec=LINE, lw=1.0, z=3, r=1.0)
    for yy in range(59, 81, 4):
        ax.plot([x + 0.4, x + 6.1], [yy, yy], color="#CFCFCF", lw=0.45, zorder=4)
    ax.text(x + 3.25, 58.6, lab, ha="center", va="bottom", rotation=90,
            fontsize=5.6, color="#3A3A3A")

box(58, 25, 14, 14, fc="white", ec=LINE, lw=1.0, z=3)               # 回流罐
ax.text(65, 22.4, "V12X09", ha="center", fontsize=6.2, color="#333333")
box(80, 24, 10, 13, fc="white", ec=LINE, lw=1.0, z=3)                # 中间罐
ax.text(85, 21.4, "中间罐", ha="center", fontsize=6.2, color="#333333")
for x in (74, 84):
    box(x, 5, 8, 8, fc="white", ec=LINE, lw=1.0, z=3, r=1.0)
ax.text(78, 2.8, "成品罐1", ha="center", fontsize=5.8, color="#333333")
ax.text(88, 2.8, "成品罐2", ha="center", fontsize=5.8, color="#333333")

# ---------- 管线 ----------
ax.annotate("", xy=(11.5, 18.5), xytext=(0.4, 18.5),
            arrowprops=dict(arrowstyle="-|>", color=C["JKT"], lw=1.5, mutation_scale=10))
ax.text(0.6, 20.4, "蒸汽", fontsize=6.5, color=C["JKT"])
ax.annotate("", xy=(17, 8.5), xytext=(17, 17.6),
            arrowprops=dict(arrowstyle="-|>", color="#8A8A8A", lw=1.0, mutation_scale=8))
ax.text(17, 6.8, "蒸汽凝液", ha="center", fontsize=6.0, color="#555555")

arrow(34.5, 47.5, 41.8, 46.5, color="#B25000", lw=1.1, ms=8)
ax.text(36.8, 44.6, "汽相", fontsize=5.8, color="#8A3D00")
arrow(50.6, 74.0, 61.7, 79.0, color="#B25000", lw=1.1, ms=8, rad=-0.12)
ax.text(55.2, 79.6, "塔顶汽相", ha="center", fontsize=5.8, color="#8A3D00")
for i in range(3):
    arrow(cond_x[i] + 6.7, 72.5, cond_x[i + 1] - 0.15, 72.5, color="#B25000", lw=0.9, ms=7)
arrow(98.7, 66.0, 103.4, 66.0, color="#777777", lw=0.9, ms=7)
ax.text(101.0, 68.0, "尾气", ha="center", fontsize=5.6, color="#555555")

arrow(63.0, 55.6, 66.0, 39.6, color="#2E6E9E", lw=1.1, ms=8, rad=0.25)
ax.text(60.4, 49.6, "冷凝液", fontsize=5.8, color="#2E6E9E", rotation=68)
ax.plot([58.0, 56.6], [32.0, 32.0], color="#2E6E9E", lw=0.9, zorder=2)
arrow(56.6, 32.0, 56.6, 62.0, color="#2E6E9E", lw=0.9, ms=7)
ax.plot([56.6, 51.0], [63.2, 63.2], color="#2E6E9E", lw=0.9, zorder=2)
ax.text(55.2, 47.5, "回流", fontsize=5.8, color="#2E6E9E", rotation=90, ha="center")

ax.plot([72.2, 72.2, 74.5], [25.4, 14.0, 14.0], color="#2E6E9E", lw=0.9, zorder=2)
arrow(74.5, 14.0, 73.7, 12.6, color="#2E6E9E", lw=0.9, ms=7)
ax.plot([90.0, 90.0, 84.6], [24.0, 11.0, 11.0], color="#6F6F6F", lw=0.8, zorder=2)
arrow(84.6, 11.0, 82.4, 12.2, color="#6F6F6F", lw=0.8, ms=7)

# ---------- 27 个测点 ----------
ax.add_patch(Circle((11.5, 18.5), 0.4, facecolor=C["JKT"], edgecolor="white",
                    linewidth=0.7, zorder=6))
ax.text(11.3, 16.0, "JKT-F1", ha="right", va="center", fontsize=6.1, color="#111111",
        zorder=7, path_effects=HALO)
tag(10.0, 44.0, "JKT-P1", "JKT", ha="right", dx=-0.9, leader_to=(10.6, 44.0))
tag(10.0, 33.0, "JKT-T1", "JKT", ha="right", dx=-0.9, leader_to=(10.6, 33.0))

tag(34.2, 42.0, "KTL-T1", "KTL", dx=0.9, leader_to=(33.0, 42.0))
tag(34.2, 34.5, "KTL-P1", "KTL", dx=0.9, leader_to=(33.0, 34.5))
tag(34.2, 26.5, "KTL-I1", "KTL", dx=0.9, leader_to=(33.0, 26.5))

for y, lab in zip([77.0, 64.0, 50.0], ["COL-P1", "COL-P2", "COL-P3"]):
    tag(41.2, y, lab, "COL", ha="right", dx=-0.9, leader_to=(42.6, y))
for y, lab in zip([72.0, 60.0, 48.0, 34.0], ["COL-T1", "COL-T2", "COL-T3", "COL-T4"]):
    tag(51.2, y, lab, "COL", dx=0.9, leader_to=(50.4, y))

for x, lab in zip(cond_x, ["CND-T1", "CND-T2", "CND-T3", "CND-T4"]):
    tag(x + 3.25, 86.5, lab, "CND", ha="center")
for x, lab, med in zip(cond_x[:2], ["CND-TA2", "CND-TA1"],
                        ["循环水", "5 ℃水"]):
    pass
ax.text(cond_x[0] + 3.25, 89.4, "循环水", ha="center", fontsize=5.5, color="#555555")
ax.text(cond_x[1] + 3.25, 89.4, "5 ℃水", ha="center", fontsize=5.5, color="#555555")
ax.text(cond_x[2] + 3.25, 89.4, "盐水I", ha="center", fontsize=5.5, color="#555555")
ax.text(cond_x[3] + 3.25, 89.4, "盐水II", ha="center", fontsize=5.5, color="#555555")

tag(65.0, 52.6, "CND-TA2", "CND", ha="center", leader_to=(64.5, 55.8))
tag(75.0, 52.6, "CND-TA1", "CND", ha="center", leader_to=(75.5, 55.8))

for y, lab in zip([36.0, 32.5, 29.0], ["RFD-L1", "RFD-P1", "RFD-T1"]):
    tag(72.8, y, lab, "RFD", dx=0.9)
for y, lab in zip([34.5, 31.0, 27.5, 24.5], ["ITK-L1", "ITK-P1", "ITK-T1", "ITK-V1"]):
    tag(90.8, y, lab, "ITK", dx=0.9)
tag(72.2, 18.0, "RFD-F1", "RFD", ha="center", leader_to=(72.2, 18.6))

# ---------- 图例与注释 ----------
leg = [("夹套蒸汽（3）", "JKT"), ("精馏釜（3）", "KTL"), ("精馏塔（7）", "COL"),
       ("分级冷凝（6）", "CND"), ("回流与采出（4）", "RFD"), ("中间罐（4）", "ITK")]
x0 = 1.0
for lab, g in leg:
    ax.add_patch(Circle((x0, 96.5), 0.45, facecolor=C[g], edgecolor="white", linewidth=0.7))
    ax.text(x0 + 1.2, 96.5, lab, va="center", fontsize=6.1, color="#222222")
    x0 += 17.0
ax.text(1.0, 92.2, "注：圆点为 DCS 测点，颜色表示功能组；图中连线只表示设备连接与物料/能量主流向，"
                   "不作为算法方向先验。", fontsize=5.6, color="#444444")

for ext in ("png", "pdf"):
    fig.savefig(FIG / f"Fig1_process_sensors.{ext}", dpi=300, bbox_inches="tight",
                facecolor="white")
plt.close(fig)
print("Fig1 saved v2")
