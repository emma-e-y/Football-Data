#line_off_epa_game
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.legend_handler import HandlerBase
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os
# =====================================================
# LOAD GAME-LEVEL DATA
# =====================================================
OUTDIR = "outputs_final"
df = pd.read_csv("Data/titans_epa_per_game.csv")

# Keep only 2023 and 2024
df = df[df["season"].isin([2023, 2024])]

# Sort properly
df = df.sort_values(["season", "week"])

# Game number within each season
df["game_num"] = (
    df.groupby("season")
      .cumcount()
      .add(1)
)

# Limit to regular season
df = df[df["week"].between(1, 18)]

# =====================================================
# COMPUTE TRUE 3-GAME ROLLING AVERAGE (BY GAME COUNT)
# =====================================================
df["rolling_3"] = (
    df.groupby("season")["off_epa_game"]
      .rolling(3)
      .mean()
      .reset_index(level=0, drop=True)
)

# =====================================================
# SANITY CHECK PRINT
# =====================================================
print("\n=== Titans Offensive EPA (Game-Level + 3-Game Rolling) ===\n")

for season in [2023, 2024]:
    print(f"\n--- Season {season} ---")
    s = df[df["season"] == season]

    for _, row in s.iterrows():
        rolling = (
            f"{row['rolling_3']:.4f}"
            if not pd.isna(row["rolling_3"])
            else "nan"
        )
        print(
            f"Game {int(row['game_num'])}: "
            f"Game EPA = {row['off_epa_game']:.4f}, "
            f"Rolling 3 = {rolling}"
        )

# =====================================================
# STYLING
# =====================================================
plt.style.use("seaborn-v0_8-white")

plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 17,
    "axes.labelsize": 13,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False
})

COLORS = {
    2023: "#4B92DB",   # Titans blue
    2024: "#7A4A2E"    # Bad vibes brown
}

# =====================================================
# CUSTOM LEGEND HANDLER (POOP EMOJI IMAGE)
# =====================================================
class HandlerPoop(HandlerBase):
    def __init__(self, image_path, zoom=0.034):
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

# =====================================================
# PLOTTING
# =====================================================
fig, ax = plt.subplots(figsize=(13, 6))

for season in [2023, 2024]:
    season_data = df[df["season"] == season]

    # Raw game EPA (dots)
    ax.scatter(
        season_data["game_num"],
        season_data["off_epa_game"],
        color=COLORS[season],
        alpha=0.25,
        s=45
    )

    # Rolling average (line)
    ax.plot(
        season_data["game_num"],
        season_data["rolling_3"],
        color=COLORS[season],
        linewidth=3,
        label=str(season)
    )

# Zero line
ax.axhline(0, color="black", linewidth=1, alpha=0.8)

# Axes
ax.set_xticks(range(1, 18))
ax.set_xlabel("Game Number")
ax.set_ylabel("EPA per Play")

ax.set_title(
    "Titans Offensive EPA per Play\n"
    "Game-Level Performance with 3-Game Rolling Average (2023 vs 2024)"
)

# Grid
ax.grid(axis="y", alpha=0.2)
ax.grid(axis="x", visible=False)

# =====================================================
# LEGEND (WITH POOP FOR 2024)
# =====================================================
handles, labels = ax.get_legend_handles_labels()

custom_handles = []
custom_labels = []

for h, l in zip(handles, labels):
    if l == "2024":
        placeholder = plt.Line2D([], [], color="none")
        custom_handles.append(placeholder)
        custom_labels.append("2024 (Callahan)")
    elif l == "2023":
        custom_handles.append(h)
        custom_labels.append("2023 (Vrabel)")

ax.legend(
    custom_handles,
    custom_labels,
    title="Season",
    frameon=False,
    handler_map={custom_handles[-1]: HandlerPoop("poop.png")}
)

# =====================================================
# SAVE OUTPUT
# =====================================================
plt.tight_layout()
outpath = os.path.join(OUTDIR, "line_off_epa_by_game_final.png")
plt.savefig(outpath, dpi=300)
plt.close()
