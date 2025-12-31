#team_years.py

#extract team labels
import requests
from bs4 import BeautifulSoup
import lxml
import pandas as pd
import time
import random

#Extract team codes
url = "https://www.pro-football-reference.com/teams/"
res = requests.get(url)
soup = BeautifulSoup(res.text, "lxml")

team_codes = []
for a in soup.select("table#teams_active tbody tr th a"):
    href = a["href"]   # e.g. "/teams/crd/"
    code = href.split("/")[2]  # "crd"
    team_codes.append(code)
    time.sleep(random.uniform(0.5, 1.8))


#Loop through each team code and extract data
all_team_years = []

for team in team_codes:
    url = f"https://www.pro-football-reference.com/teams/{team}/"
    df = pd.read_html(url, header=1)[0]

    # Drop rows that aren’t numeric seasons
    df = df[df["Year"].astype(str).str.isnumeric()]

    # Add team code
    df["team"] = team

    all_team_years.append(df)

team_years = pd.concat(all_team_years, ignore_index=True)

team_years.to_csv("team_years.csv", index=False)