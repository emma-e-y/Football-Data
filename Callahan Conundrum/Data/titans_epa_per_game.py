#EPA/play per game for Titans offense and defense

import pandas as pd
import numpy as np
from nfl_data_py import import_pbp_data
import matplotlib.pyplot as plt

# -----------------------------
# 1. Load play-by-play data
# -----------------------------
seasons = [2023, 2024]
pbp = import_pbp_data(seasons)

# Filter for Titans drives
pbp_titans = pbp[(pbp['posteam'] == 'TEN') | (pbp['defteam'] == 'TEN')].copy()

# -----------------------------
# 2. Compute game-level EPA
# -----------------------------
# Offense EPA per play (Titans as posteam)
off = (
    pbp_titans[pbp_titans['posteam'] == 'TEN']
    .groupby(['season', 'game_id'])
    .agg(off_epa_game=('epa', 'mean'))
    .reset_index()
)

# Defense EPA per play (Titans as defteam)
defn = (
    pbp_titans[pbp_titans['defteam'] == 'TEN']
    .groupby(['season', 'game_id'])
    .agg(def_epa_game=('epa', 'mean'))
    .reset_index()
)

# Sort and add week number
off = off.sort_values(['season', 'game_id'])
off['week'] = off.groupby('season').cumcount() + 1

defn = defn.sort_values(['season', 'game_id'])
defn['week'] = defn.groupby('season').cumcount() + 1

# -----------------------------
# 3. Compute 3-game rolling average
# -----------------------------
off['off_rolling3'] = off.groupby('season')['off_epa_game'].rolling(3).mean().reset_index(level=0, drop=True)
defn['def_rolling3'] = defn.groupby('season')['def_epa_game'].rolling(3).mean().reset_index(level=0, drop=True)

# -----------------------------
# 4. Merge offense & defense for printing
# -----------------------------
combined = pd.merge(off, defn, on=['season', 'game_id', 'week'], how='outer')

# -----------------------------
# 5. Print numbers for verification
# -----------------------------
for season in seasons:
    print(f"\n=== Season {season} ===")
    season_data = combined[combined['season'] == season].sort_values('week')
    for _, row in season_data.iterrows():
        off_r3 = f"{row.off_rolling3:.4f}" if not np.isnan(row.off_rolling3) else "nan"
        def_r3 = f"{row.def_rolling3:.4f}" if not np.isnan(row.def_rolling3) else "nan"
        print(
            f"Week {int(row.week)}: "
            f"Off EPA/play = {row.off_epa_game:.4f}, "
            f"Def EPA/play = {row.def_epa_game:.4f}, "
            f"Off R3 = {off_r3}, "
            f"Def R3 = {def_r3}"
        )

# -----------------------------
# 6. Save CSV
# -----------------------------
combined.to_csv("titans_epa_per_game.csv", index=False)
