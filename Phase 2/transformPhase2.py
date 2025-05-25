import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
import re
import os

BASE_URL = "https://hotwheels.fandom.com"

# Load original data
original_df = pd.read_csv("./Phase 1/processedPhase1.csv")

# Add Valid column if not present
if "Valid" not in original_df.columns:
    original_df["Valid"] = True

# Load previously processed data
save_path = "./Phase 2/processedPhase2.csv"
if os.path.exists(save_path):
    df = pd.read_csv(save_path)
else:
    df = original_df.copy()

df = df.reset_index(drop=True)

if "Valid" not in df.columns:
    df["Valid"] = True

# Load stopped index
index_path = "./Phase 2/stoppedIndex.txt"
if os.path.exists(index_path):
    with open(index_path, "r") as f:
        try:
            start_index = int(f.read().strip())
        except ValueError:
            start_index = 0
else:
    start_index = 0

print(f"Starting from index {start_index}")

def getHTMLdocument(url):
    response = requests.get(url)
    return response.text

for index in range(start_index, len(df)):
    row = df.iloc[index]

    if "Valid" in df.columns and df.loc[index, "Valid"] == False:
        continue

    print(f"Processing Index: {index}")

    try:
        soup = BeautifulSoup(getHTMLdocument(BASE_URL + row["Link"]), 'html.parser')

        if soup.find("span", id=re.compile(r"Versions")) is None:
            df.loc[index, "Valid"] = False

        # Save progress after each iteration
        df.to_csv(save_path, index=False)

        # Update stopped index
        with open(index_path, "w") as f:
            f.write(str(index + 1))  # +1 to start at the next row next time

        time.sleep(3)

    except Exception as e:
        print(f"Error at index {index}: {e}")
        break  # optionally: continue

# Final cleanup: remove invalid entries
df = df[df["Valid"] == True].drop(columns=["Valid"])
df.to_csv(save_path, index=False)
