import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.patheffects as pe

POOP_IMG = "poop.png"
poop_img = mpimg.imread(POOP_IMG)

# === Load the dataset ===
df = pd.read_csv("Data/team_years.csv")

# --- Filter for Titans/Oilers ---
titans = df[df['team'] == 'oti'].copy()
titans = titans.sort_values('Year').reset_index(drop=True)

# --- Keep metrics ---
metrics = ['W', 'L', 'PF', 'PA', 'PD', 'SRS', 'OSRS', 'DSRS']
titans = titans[['Year', 'Coaches'] + metrics]

# --- Rolling averages ---
for m in metrics:
    titans[f'{m}_roll5'] = titans[m].rolling(window=5).mean()

titans["SRS_roll3"] = titans["SRS"].rolling(window=3).mean()

# --- Plotting ---
plt.style.use("seaborn-v0_8-whitegrid")
fig, ax = plt.subplots(figsize=(14, 6))

sns.lineplot(data=titans, x='Year', y='SRS_roll3',
             color='#222a82', linewidth=2, label='3-Year Rolling Avg')

sns.lineplot(data=titans, x='Year', y='SRS_roll5',
             color='#4095D1', linewidth=2, label='5-Year Rolling Avg')

sns.lineplot(data=titans, x='Year', y='SRS',
             color='grey', linewidth=0.8, label='Season SRS')

# --- Highlight Callahan 2024 with 💩 ---
callahan_year = 2024
callahan_srs = titans.loc[titans['Year'] == callahan_year, 'SRS'].values[0]

imagebox = OffsetImage(poop_img, zoom=0.025)
ab = AnnotationBbox(imagebox, (callahan_year, callahan_srs),
                    frameon=False, box_alignment=(0.5, 0.5), zorder=3)
ax.add_artist(ab)

# --- Coach eras ---
eras = [
    ("Bum Phillips", 1975, 1980, "#76B7B2"),
    ("Jerry Glanville", 1986, 1989, "#B07AA1"),
    ("Jeff Fisher", 1994, 2010, "#4C72B0"),
    ("Mike Munchak", 2011, 2013, "#DD8452"),
    ("Mike Mularkey", 2015, 2017, "#8172B2"),
    ("Mike Vrabel", 2018, 2023, "#55A868"),
    ("Brian Callahan", 2024, 2024, "#E15759"),
]

plt.pause(0.01)
ymin, ymax = ax.get_ylim()
yrange = ymax - ymin
top_y = ymax - 0.02 * yrange
mularkey_y = top_y - 0.05 * yrange

for coach, start, end, color in eras:
    ax.axvspan(start, end, color=color, alpha=0.25, zorder=0)
    mid = (start + end) / 2
    duration = end - start + 1

    if duration >= 3 or coach == "Mike Mularkey":
        y_pos = mularkey_y if coach == "Mike Mularkey" else top_y
        ax.text(mid, y_pos, coach,
                ha='center', va='top', fontsize=8, weight='bold',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.6))

# --- League average ---
ax.axhline(0, color='black', linestyle='--', lw=1)

# ---------- Milestones (SRS — SAME SYSTEM FOR ALL) ----------
plt.draw()
plt.pause(0.01)
ymin, ymax = ax.get_ylim()
yrange = ymax - ymin

offset = 0.06 * yrange
x_offset_years = 2

# Bottom-left (mirrored diagonal)
milestones = [
    (1978, "Lost AFC Championship"),
    (1999, "Lost Super Bowl XXXIV"),
    (2024, "Brian Callahan")
]

for year, label in milestones:
    val = titans.loc[titans['Year'] == year, 'SRS'].values[0]

    arrow_x = year
    arrow_y = val

    # Callahan: move arrow TIP left + down (NOT shorter)
    if year == 2024:
        arrow_x = year - 0.4
        arrow_y = val - 0.02 * yrange

    text_x = arrow_x - x_offset_years
    text_y = arrow_y - offset

    if text_y < ymin + 0.02 * yrange:
        text_y = ymin + 0.02 * yrange

    ax.annotate(
        label,
        xy=(arrow_x, arrow_y),
        xytext=(text_x, text_y),
        arrowprops=dict(facecolor='gray', arrowstyle='->', lw=1),
        fontsize=12,
        ha='center',
        va='top',
        path_effects=[
            pe.Stroke(linewidth=3, foreground="white"),
            pe.Normal()
        ]
    )

# Top-right diagonal milestones
diagonal_milestones = [
    (1979, "Lost AFC Championship"),
    (2002, "Lost AFC Championship"),
    (2019, "Lost AFC Championship")
]

for year, label in diagonal_milestones:
    val = titans.loc[titans['Year'] == year, 'SRS'].values[0]

    text_x = year + x_offset_years
    text_y = val + offset

    if text_y > top_y - 0.03 * yrange:
        text_y = top_y - 0.03 * yrange

    ax.annotate(
        label,
        xy=(year, val),
        xytext=(text_x, text_y),
        arrowprops=dict(facecolor='gray', arrowstyle='->', lw=1),
        fontsize=12,
        ha='center',
        va='bottom',
        path_effects=[
            pe.Stroke(linewidth=3, foreground="white"),
            pe.Normal()
        ]
    )

# --- Titles & labels ---
ax.set_title(
    "Tennessee Titans Historical Performance (1960–2024)\n"
    "SRS with Coaching Eras Highlighted and Milestones",
    fontsize=16, fontweight='bold', pad=20
)
ax.set_xlabel("Season")
ax.set_ylabel("SRS (Simple Rating System)")

ax.legend(frameon=False, loc='lower left')
plt.tight_layout()
plt.savefig("titans_srs_trend_final.png")