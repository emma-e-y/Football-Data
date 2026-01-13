# titans_season_metrics.py
import os
import pandas as pd
import numpy as np
from nfl_data_py import import_pbp_data

# --------------------
# Config
# --------------------
YEARS = list(range(2000, 2025))
TEAM = "TEN"

OUT_SEASON = "titans_metrics_1.csv"

# --------------------
# Success rate helper
# --------------------
def compute_success(df):
    yg = df["ydstogo"].replace(0, np.nan)
    gained = df["yards_gained"].fillna(0)

    s = pd.Series(False, index=df.index)
    s |= ((df["down"] == 1) & (gained >= 0.5 * yg))
    s |= ((df["down"] == 2) & (gained >= 0.7 * yg))
    s |= (((df["down"] == 3) | (df["down"] == 4)) & (gained >= yg))
    s |= (df["touchdown"] == 1)

    return s.fillna(False)

# --------------------
# Season aggregation helpers
# --------------------
def season_agg_off(df):
    early = df[df["down"].isin([1, 2])]

    return pd.Series({
        "plays": len(df),
        "off_epa_per_play": df["epa"].mean(),
        "off_early_epa_per_play": early["epa"].mean(),
        "off_success_rate_pct": df["success_flag"].mean()
    })

def season_agg_def(df):
    early = df[df["down"].isin([1, 2])]
    return pd.Series({
        "def_epa_per_play": df["epa"].mean(),
        "def_early_epa_per_play": early["epa"].mean(),
        "def_success_rate_pct": df["success_flag"].mean()
    })

# --------------------
# MAIN LOOP
# --------------------
for year in YEARS:
    print(f"\nLoading {year}...")

    try:
        try:
            pbp = import_pbp_data([year], downcast=True)
        except TypeError:
            pbp = import_pbp_data(year, downcast=True)
    except Exception as e:
        print(f"FAILED {year}: {e}")
        continue

    if pbp is None or len(pbp) == 0:
        print(f"No data for {year}")
        continue

    pbp["season"] = year

    # --------------------
    # Offense universe
    # --------------------
    ten_off = pbp[pbp["posteam"] == TEAM].copy()
    if ten_off.empty:
        print(f"No TEN offensive plays in {year}")
        continue

    ten_off["success_flag"] = compute_success(ten_off)

    # Season-level offense metrics
    season_off_df = ten_off.groupby("season").apply(season_agg_off).reset_index()

    # --------------------
    # Defense universe
    # --------------------
    ten_def = pbp[pbp["defteam"] == TEAM].copy()
    ten_def["success_flag"] = compute_success(ten_def)
    season_def_df = ten_def.groupby("season").apply(season_agg_def).reset_index()

    # --------------------
    # Merge offense + defense
    # --------------------
    season_df = season_off_df.merge(season_def_df, on="season")

    # --------------------
    # PROE (neutral situations only)
    # --------------------
    neutral = ten_off[
        (ten_off["down"].isin([1, 2])) &
        (ten_off["ydstogo"] <= 10) &
        (ten_off["qtr"] <= 3) &
        (ten_off["score_differential"].between(-10, 10)) &
        (ten_off["play_type"].isin(["run", "pass"]))
    ]

    league_neutral = pbp[
        (pbp["down"].isin([1, 2])) &
        (pbp["ydstogo"] <= 10) &
        (pbp["qtr"] <= 3) &
        (pbp["score_differential"].between(-10, 10)) &
        (pbp["play_type"].isin(["run", "pass"]))
    ]

    actual_pass_rate = neutral["pass"].mean()
    expected_pass_rate = league_neutral["pass"].mean()

    season_df["proe_pct_points"] = (actual_pass_rate - expected_pass_rate) * 100


    season_df.to_csv(
        OUT_SEASON,
        mode="a",
        index=False,
        header=not os.path.exists(OUT_SEASON)
    )

print("\nDone.")
print(f"- {OUT_SEASON}")