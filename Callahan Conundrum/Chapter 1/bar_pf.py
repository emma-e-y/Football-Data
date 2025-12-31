#bar_pf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.legend_handler import HandlerBase
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.lines import Line2D
import seaborn as sns
import numpy as np
import os

# -----------------------------
# FILE AND OUTPUT SETUP
# -----------------------------
DATA_FILE = "Data/titans_season_metrics.csv"
POOP_IMG = "poop.png"
OUTDIR = "outputs_final"
os.makedirs(OUTDIR, exist_ok=True)

# -----------------------------
# COLORS
# -----------------------------
COLOR_VRABEL = "#4B92DB"
COLOR_CALLAHAN = "#7A4A2E"
COLOR_OTHER = "#0C2340"

# -----------------------------
# LOAD DATA
# -----------------------------
def load_data():
    df = pd.read_csv(DATA_FILE)
    df.columns = df.columns.str.lower()
    df["season"] = df["season"].astype(int)
    df = df[(df["season"] >= 2018) & (df["season"] <= 2024)].copy()
    return df

# =====================================================
# CUSTOM LEGEND HANDLER (💩)
# =====================================================
class HandlerPoop(HandlerBase):
    def __init__(self, image_path=POOP_IMG, zoom=0.028):
        super().__init__()
        self.image = mpimg.imread(image_path)
        self.zoom = zoom

    def create_artists(
        self, legend, orig_handle,
        xdescent, ydescent, width, height,
        fontsize, trans
    ):
        oi = OffsetImage(self.image, zoom=self.zoom)
        ab = AnnotationBbox(
            oi,
            (xdescent + width / 2, ydescent + height / 2),
            xycoords=trans,
            frameon=False
        )
        return [ab]

def poop_legend(ax):
    handles = [
        Line2D([], [], color=COLOR_VRABEL, lw=3),
        Line2D([], [], color="none")
    ]
    labels = ["2023 (Vrabel)", "2024 (Callahan)"]
    ax.legend(
        handles, labels,
        handler_map={handles[1]: HandlerPoop()},
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
        borderaxespad=0
    )

# =====================================================
# MAIN ANALYSIS
# =====================================================
df = load_data()

metric = "pf"

v23 = df[df["season"] == 2023][metric].iloc[0]
v24 = df[df["season"] == 2024][metric].iloc[0]

delta = v24 - v23
pct_change = (delta / v23) * 100 if v23 != 0 else np.nan

# =====================================================
# PRINT WHAT THE GRAPH IS SAYING
# =====================================================
print("\n=== Titans Points For: 2023 vs 2024 ===")
print(f"2023 value: {v23:.3f}")
print(f"2024 value: {v24:.3f}")
print(f"Absolute change: {delta:+.3f}")
print(f"Percent change: {pct_change:+.2f}%")

# =====================================================
# PLOT
# =====================================================
x = np.arange(2)
y = [v23, v24]
colors = [COLOR_VRABEL, COLOR_CALLAHAN]

plt.figure(figsize=(8,5))
sns.set_style("whitegrid")

plt.bar(x, y, color=colors, edgecolor="black")

# Label values on bars
offset = max(y) * 0.01
for xi, yi in zip(x, y):
    plt.text(xi, yi + offset, f"{yi:.3f}", ha="center", va="bottom", fontsize=10)

plt.title("Titans Points For: 2023 vs 2024", fontsize=16, weight="bold")
plt.ylabel("PF", fontsize=14)
plt.xticks(x, ["2023", "2024"])

poop_legend(plt.gca())

plt.tight_layout()
outpath = os.path.join(OUTDIR, "bar_pf_23vs24_final.png")
plt.savefig(outpath, dpi=300)
plt.close()

print(f"\nSaved → {outpath}")