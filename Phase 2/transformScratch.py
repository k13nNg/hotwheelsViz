import pandas as pd
import os
from bs4 import BeautifulSoup
import requests
import time
import re

# open processedPhase1.csv
# processedPhase1 = pd.read_csv("./Phase 1/processedPhase1.csv")

# if there exists a scrape file for Phase 2, use that. Otherwise, use processedPhase1
# Note: This is because for this phase, scrape process takes a significantly longer amount of time
rawPhase2Path = "./Phase 2/rawPhase2.csv"
processedPhase1Path = "./Phase 1/processedPhase1.csv"
BASE_URL = "https://hotwheels.fandom.com"


df = pd.read_csv(processedPhase1Path)

# retrieve scrapeIndex (saved in scrapeIndex.txt)
# this index tells us where we were in the last scraping instance
# Load stopped index
indexPath = "./Phase 2/stoppedIndex.txt"

if os.path.exists(indexPath):
    with open(indexPath, "r") as f:
        try:
            startIndex = int(f.read().strip())
        except ValueError:
            startIndex = 0
else:
    startIndex = 0

print(f"Starting from index {startIndex}")

def getHTMLdocument(url):
    response = requests.get(url)
    return response.text


for index in range(startIndex, len(df)):
    print(f"Index: {index}, Progress: {round(index/len(df)*100, 2)}%")
    row = df.iloc[index]

    try:
        soup = BeautifulSoup(getHTMLdocument(BASE_URL + row["Link"]), 'html.parser')

        if not(soup.find("span", id=re.compile(r"Versions")) is None):
            headersList = soup.find_all("span", id = re.compile(r"Versions"))

            for header in headersList:
                table = header.find_next("table")

                # Step 1: Parse headers from thead
                header_row = table.find("tr")
                headers = [th.get_text(strip=True) for th in header_row.find_all("th")]

                # Step 2: Map desired headers to their indices
                desired_headers = {"Year", "Series", "Color", "Window Color", "Interior Color", "Country"}
                col_indices = {name: i for i, name in enumerate(headers) if name in desired_headers}

                # Step 3: Extract only desired columns from tbody rows
                tbody = table.find("tbody")
                filtered_data = []

                for r in tbody.find_all("tr"):
                    cells = r.find_all("td")

                    row_data = {}
                    for name in desired_headers:
                        idx = col_indices.get(name)
                        if idx is not None and idx < len(cells):
                            row_data[name] = cells[idx].get_text(strip=True)
                        else:
                            row_data[name] = None

                    # Skip if all attributes are None
                    if all(not row_data[h] for h in desired_headers):
                        continue

                    row_data["Model Name"] = row["Model Name"]
                    filtered_data.append(row_data)

                file_exists = os.path.exists(rawPhase2Path)
                
                output_columns = ["Model Name", "Year", "Series", "Color", "Window Color", "Interior Color", "Country"]

                pd.DataFrame(filtered_data)[output_columns].to_csv(
                    rawPhase2Path,
                    mode="a",
                    header=not file_exists,  # Write header only if file doesn't exist
                    index=False
                )
                # Update stopped index
                with open(indexPath, "w") as f:
                    f.write(str(index + 1))  # +1 to start at the next row next time
        time.sleep(3)

    except Exception as e:
        print(f"Error at index {index}: {e}")
        break  # optionally: continue