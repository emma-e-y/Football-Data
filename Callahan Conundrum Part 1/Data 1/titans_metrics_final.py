import pandas as pd

# --------------------
# Load CSVs
# --------------------
team_years = pd.read_csv("team_years.csv")
titans_season_metrics = pd.read_csv("titans_metrics_1.csv")

# --------------------
# Filter team_years to Titans
# --------------------
titans_srs = team_years[
    team_years["team"] == "oti"
][["Year", "Tm", "Coaches", "OSRS", "DSRS", "SRS", "PF", "PA", "PD"]].copy()

# --------------------
# Merge into titans_season_metrics
# --------------------
titans_season_metrics = titans_season_metrics.merge(
    titans_srs,
    left_on="season",
    right_on="Year",
    how="left"
)

# Drop duplicate Year column after merge
titans_season_metrics.drop(columns=["Year"], inplace=True)

# --------------------
# Save updated CSV
# --------------------
titans_season_metrics.to_csv(
    "titans_metrics_final.csv",
    index=False
)

print("OSRS, DSRS, SRS, PF, PA, and PD successfully added to titans_season_metrics.")
