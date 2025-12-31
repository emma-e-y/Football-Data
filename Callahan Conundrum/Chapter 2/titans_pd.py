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

# --- Filter for Titans/Oilers (team code 'oti') ---
titans = df[df['team'] == 'oti'].copy()
titans = titans.sort_values('Year').reset_index(drop=True)

# --- Keep only the metrics we need ---
metrics = ['W', 'L', 'PF', 'PA', 'PD', 'SRS', 'OSRS', 'DSRS']
titans = titans[['Year', 'Coaches'] + metrics]

# --- Compute 5-year rolling averages for long-term trend ---
for m in metrics:
    titans[f'{m}_roll5'] = titans[m].rolling(window=5).mean()

#--- Compute 3-year rolling mean PD ---
titans["PD_roll3"] = titans["PD"].rolling(window=3).mean()


# --- Plotting ---
plt.style.use("seaborn-v0_8-whitegrid")

fig, ax = plt.subplots(figsize=(14, 6))

# --- Plot 3-year rolling average ---
sns.lineplot(
    data=titans,
    x='Year', y='PD_roll3',
    color='#222a82',
    linewidth=2,
    label='3-Year Rolling Avg'
)

# --- Plot 5-year rolling average ---
sns.lineplot(
    data=titans,
    x='Year', y='PD_roll5',
    color='#4095D1',
    linewidth=2,
    label='5-Year Rolling Avg'
)

# --- Plot season PD ---
sns.lineplot(
    data=titans,
    x='Year', y='PD',
    color='grey',
    linewidth=0.8,
    label='Season PD'
)

# --- Highlight Callahan 2024 ---
callahan_year = 2024
callahan_pd = titans.loc[titans['Year'] == callahan_year, 'PD'].values[0]
# --- Highlight Callahan 2024 with 💩 ---
imagebox = OffsetImage(poop_img, zoom=0.025)  # adjust size here
ab = AnnotationBbox(
    imagebox,
    (callahan_year, callahan_pd),
    frameon=False,
    box_alignment=(0.5, 0.5),
    zorder=2
)
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

# We'll compute Y positions AFTER first plot
plt.pause(0.01)
ymin, ymax = ax.get_ylim()

# Top label row = 5% below top of chart
top_y = ymax - 0.02 * (ymax - ymin)

# Mularkey slightly below that
mularkey_y = top_y - 0.05 * (ymax - ymin)

for coach, start, end, color in eras:
    ax.axvspan(start, end, color=color, alpha=0.25, zorder=0)
    duration = end - start + 1
    mid = (start + end) / 2

    if duration >= 3 or coach == "Mike Mularkey":
        if coach == "Mike Mularkey":
            y_pos = mularkey_y
        else:
            y_pos = top_y

        ax.text(
            mid, y_pos, coach,
            ha='center', va='top', fontsize=8, weight='bold', color='black',
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.6)
        )



# --- Reference line for league average ---
ax.axhline(0, color='black', linewidth=1, linestyle='--')

# ---------- Dynamic Milestones (works for any metric scale) ----------
# Make sure axis autoscale has taken effect
plt.draw()
plt.pause(0.01)
ymin, ymax = ax.get_ylim()
yrange = ymax - ymin
offset = 0.06 * yrange   # 3% of vertical range for annotation offset
x_offset_years = 2       # horizontal text offset in years

# 'Below' milestones (arrow coming from below)
milestones = [
    (1978, titans.loc[titans['Year']==1978, 'PD'].values[0] if not titans.loc[titans['Year']==1978, 'PD'].isna().all() else None, "Lost AFC Championship"),
      (2002, titans.loc[titans['Year']==2002, 'PD'].values[0] if not titans.loc[titans['Year']==2002, 'PD'].isna().all() else None, "Lost AFC Championship"),
    (2024, titans.loc[titans['Year']==2024, 'PD'].values[0] if not titans.loc[titans['Year']==2024, 'PD'].isna().all() else None, "Brian Callahan")
]

for year, val, label in milestones:
    if val is None:
        continue

    # --- default arrow tip ---
    arrow_x = year
    arrow_y = val

    # --- special handling for Callahan to avoid 💩 overlap ---
    if year == 2024:
        arrow_x = year - 0.40    # small left nudge
        arrow_y = val - 0.02 * yrange  # small downward nudge

    text_x = arrow_x - x_offset_years
    text_y = arrow_y - offset

    min_allowed = ymin + 0.02 * yrange
    if text_y < min_allowed:
        text_y = min_allowed

    ax.annotate(
        label,
        xy=(arrow_x, arrow_y),        # 👈 THIS is the arrow tip
        xytext=(text_x, text_y),
        arrowprops=dict(facecolor='gray', arrowstyle='->', lw=1),
        fontsize=12,
        color='black',
        ha='center',
        va='top',
        bbox=dict(facecolor='none', edgecolor='none', alpha=0.7),
        path_effects=[
            pe.Stroke(linewidth=3, foreground="white"),
            pe.Normal()
        ]
    )



# Diagonal / above milestones (text up-right)
diagonal_milestones = [
    (1979, titans.loc[titans['Year']==1979, 'PD'].values[0] if not titans.loc[titans['Year']==1979, 'PD'].isna().all() else None, "Lost AFC Championship"),
     (1999, titans.loc[titans['Year']==1999, 'PD'].values[0] if not titans.loc[titans['Year']==1999, 'PD'].isna().all() else None, "Lost Super Bowl XXXIV"),
    (2019, titans.loc[titans['Year']==2019, 'PD'].values[0] if not titans.loc[titans['Year']==2019, 'PD'].isna().all() else None, "Lost AFC Championship")
]

for year, val, label in diagonal_milestones:
    if val is None:
        continue
    text_x = year + x_offset_years
    text_y = val + offset
    # Avoid putting annotation outside plot top (below top labels)
    max_allowed = top_y - 0.03 * yrange
    if text_y > max_allowed:
        text_y = max_allowed
    ax.annotate(
        label,
        xy=(year, val),
        xytext=(text_x, text_y),
        arrowprops=dict(facecolor='gray', arrowstyle='->', lw=1),
        fontsize=12,
        color='black',
        ha='center',
        va='bottom',
        bbox=dict(facecolor='none', edgecolor='none', alpha=0.7),
        path_effects=[
            pe.Stroke(linewidth=3, foreground="white"),
            pe.Normal()
        ]
    )

# --- Titles & labels ---
ax.set_title("Tennessee Titans Historical Performance (1960–2024)\nPoint Differential with Coaching Eras Highlighted and Milestones",
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel("Season", fontsize=12)
ax.set_ylabel("PD (Point Differential)", fontsize=12)

# --- Legend ---
ax.legend(frameon=False, loc='lower left', fontsize=10)

# --- Caption ---
plt.figtext(
    0.5, -0.05,
    "PD is the total points a team scores minus the points their opponents scored over a season.\nData: Pro-Football-Reference.",
    ha="center", fontsize=9, color="gray"
)

plt.tight_layout()
plt.savefig("titans_pd_trend_final.png")

# === PRINT OUT WHAT THE GRAPH IS SHOWING ===

print("\n=== SEASON PD VALUES ===")
print(titans[['Year', 'PD']].to_string(index=False))

print("\n=== 3-YEAR ROLLING PD ===")
print(titans[['Year', 'PD_roll3']].round(3).to_string(index=False))

print("\n=== 5-YEAR ROLLING PD ===")
print(titans[['Year', f'PD_roll5']].round(3).to_string(index=False))

# Callahan year
print("\n=== CALLAHAN 2024 PD ===")
print(titans.loc[titans['Year'] == 2024, ['Year', 'PD', 'PD_roll3', 'PD_roll5']])

# Milestone values
print("\n=== MILESTONE PD VALUES ===")
for year, _, label in milestones:
    val = titans.loc[titans['Year'] == year, 'PD'].values[0]
    print(f"{year}: {label} — PD = {val}")

for year, _, label in diagonal_milestones:
    val = titans.loc[titans['Year'] == year, 'PD'].values[0]
    print(f"{year}: {label} — PD = {val}")
