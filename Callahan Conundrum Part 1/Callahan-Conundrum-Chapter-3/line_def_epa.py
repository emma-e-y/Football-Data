#line_def_epa

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os
import numpy as np
import matplotlib.patheffects as pe

# -----------------------------
# FILES
# -----------------------------
DATA_FILE = "Data/titans_metrics_final.csv"
POOP_IMG = "poop.png"
OUTDIR = "outputs_final"
os.makedirs(OUTDIR, exist_ok=True)
# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(DATA_FILE)
df.columns = df.columns.str.lower()
df["season"] = df["season"].astype(int)

df = df[(df["season"] >= 2000) & (df["season"] <= 2024)].copy()

# -----------------------------
# ROLLING SMOOTHING
# -----------------------------
df["def_sr_roll3"] = df["def_epa_per_play"].rolling(3).mean()
df["def_sr_roll5"] = df["def_epa_per_play"].rolling(5).mean()

# -----------------------------
# COACH ERAS (pastel backgrounds)
# -----------------------------
eras = [
    ("Jeff Fisher",   2000, 2010, "#D6EAF8"),
    ("Mike Munchak",  2011, 2013, "#FADBD8"),
    ("Mike Mularkey", 2015, 2017, "#E8DAEF"),
    ("Mike Vrabel",   2018, 2023, "#D5F5E3"),
   # ("Brian Callahan",2024, 2024, "#FDEBD0"),
]

# -----------------------------
# PLOT SETUP
# -----------------------------
sns.set_style("whitegrid")
fig, ax = plt.subplots(figsize=(14, 6))

# -----------------------------
# BACKGROUND COACH BANDS
# -----------------------------
for coach, start, end, color in eras:
    ax.axvspan(start, end, color=color, alpha=0.45, zorder=0)

# -----------------------------
# LINES (smooth trends)
# -----------------------------
ax.plot(
    df["season"], df["def_sr_roll5"],
    color="#4095D1", linewidth=2, zorder=2,
    label="5-Year Rolling Avg"
)

ax.plot(
    df["season"], df["def_sr_roll3"],
    color="#222a82", linewidth=2, linestyle="-", zorder=3,
    label="3-Year Rolling Avg"
)

# -----------------------------
# SEASON DOTS
# -----------------------------

sns.lineplot(data=df, x="season", y="def_epa_per_play", color="grey", linewidth=0.8, zorder=1,
    label="Defensive EPA"
)

# -----------------------------
# 💩 CALLAHAN MARKER
# -----------------------------
poop_img = mpimg.imread(POOP_IMG)

callahan_year = 2024
callahan_val = df.loc[df["season"] == 2024, "def_epa_per_play"].values[0]

ab = AnnotationBbox(
    OffsetImage(poop_img, zoom=0.028),
    (callahan_year, callahan_val),
    frameon=False,
    zorder=6
)
ax.add_artist(ab)

# -----------------------------
# COACH NAMES AT TOP (acts as legend)
# -----------------------------
ymin, ymax = ax.get_ylim()
yrange = ymax - ymin
top_y = ymax - 0.03 * yrange

for coach, start, end, _ in eras:
    mid = (start + end) / 2
    ax.text(
        mid, top_y, coach,
        ha="center", va="top",
        fontsize=9, weight="bold",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.65)
    )

# -----------------------------
# MILESTONES / ANNOTATIONS (flexible)
# -----------------------------

# Common arrow geometry
dx_years = 0.65
season_range = df["season"].max() - df["season"].min()
dy_units = dx_years * np.tan(np.deg2rad(60)) * (yrange / season_range)

# List of all events you want arrows for
events = [
    (2024, "Brian Callahan", 1),  # negative multiplier for dy_units: arrow from bottom
    (2002, "Lost AFC Championship", 1),  # positive multiplier: arrow from top
    (2019, "Lost AFC Championship", - 1)
]

for year, label, dir_mult in events:
    val = df.loc[df["season"] == year, "def_epa_per_play"].values[0]

    # optional emoji nudge for Callahan
    x_nudge = -0.25 if year == 2024 else 0.0

    ax.annotate(
        label,
        xy=(year + x_nudge, val),
        xytext=(year + x_nudge - dx_years, val + dir_mult * dy_units),
        arrowprops=dict(arrowstyle="->", lw=1, color="black"),
        fontsize=12,
        ha="center",
        va="bottom" if dir_mult > 0 else "top",
        path_effects=[
            pe.Stroke(linewidth=3, foreground="white"),
            pe.Normal()
        ]
    )


# -----------------------------
# AXES & TITLES
# -----------------------------
ax.set_title(
    "Titans Defensive EPA/Play (2000–2024)\n"
    "Smoothed Trends with Coaching Eras Highlighted",
    fontsize=16,
    weight="bold",
    pad=18
)

ax.set_xlabel("Season", fontsize=12)
ax.set_ylabel("Defensive EPA", fontsize=12)

ax.set_xticks(df["season"])
ax.set_xticklabels([f"{s % 100:02d}" for s in df["season"]])

ax.grid(alpha=0.25, linestyle="--")

# -----------------------------
# FINALIZE
# -----------------------------
plt.tight_layout()
outpath = os.path.join(OUTDIR, "line_def_epa_final.png")
plt.savefig(outpath, dpi=300)
plt.close()
print(f"Saved → {outpath}")

# =================================================
# EXTENSIVE FACTUAL PRINT (UNCHANGED INTENT)
# =================================================
print("\n" + "="*75)
print("FULL NUMERICAL DESCRIPTION OF PLOTTED DATA")
print("="*75)

df_sorted = df.sort_values("season").copy()
df_sorted["yoy_change"] = df_sorted["def_epa_per_play"].diff()

print("\nSEASON-BY-SEASON VALUES\n")
print(
    df_sorted[
        ["season", "def_epa_per_play", "def_sr_roll3", "def_sr_roll5", "yoy_change"]
    ].round(4).to_string(index=False)
)

print("\nRANKINGS (BEST TO WORST)\n")
ranked = df_sorted.sort_values("def_epa_per_play", ascending=True).reset_index(drop=True)
ranked["rank"] = ranked.index + 1
print(ranked[["rank", "season", "def_epa_per_play"]].round(4).to_string(index=False))

print("\nANNOTATED SEASONS\n")
for yr in [2002, 2019, 2024]:
    r = df_sorted[df_sorted["season"] == yr].iloc[0]
    print(
        f"{yr}: value={r['def_epa_per_play']:.4f}, "
        f"3Y={r['def_sr_roll3']:.4f}, "
        f"5Y={r['def_sr_roll5']:.4f}"
    )

print("\nEND OF NUMERICAL DESCRIPTION")
print("="*75)
