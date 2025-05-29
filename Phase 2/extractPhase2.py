import pandas as pd
from bs4 import BeautifulSoup
import requests
import os
import time

# since this is a large volume of data that we are extracting, we would have to do them in parts to avoid overwhelming the router
# => if the file exists, then we continue using that file
# => else, define a new dataframe with preset columns
if os.path.exists("./Phase 2/rawPhase2.csv"):
    df = pd.read_csv("./Phase 2/rawPhase2.csv")
else:
    df = pd.DataFrame(columns = ["Year", "Model Name", "Series", "Color", "Window Color", "Interior Color", "Country"])

# retrieve scrapeIndex (saved in scrapeIndex.txt)
# this index tells us where we were in the last scraping instance
# Load scrape index
indexPath = "./Phase 2/scrapeIndex.txt"

if os.path.exists(indexPath):
    with open(indexPath, "r") as f:
        try:
            scrapeIndex = int(f.read().strip())
        except ValueError:
            scrapeIndex = 0
else:
    scrapeIndex = 0

def getHTMLdocument(url):
    response = requests.get(url)
    return response.text

def generateScrapeURL(link):
    return f"https://hotwheels.fandom.com{link}"

processedPhase1 = pd.read_csv("./Phase 1/processedPhase1.csv")
processedPhase1 = processedPhase1.reset_index()

for index in range(scrapeIndex, len(processedPhase1)):
    row = processedPhase1.iloc[index]

    total = len(processedPhase1)
    remaining = total - index
    secondsRemaining = remaining * 3

    hours = secondsRemaining // 3600
    minutes = (secondsRemaining % 3600) // 60
    seconds = secondsRemaining % 60

    print(f"Progress: {(index / total * 100):.2f}% | Expected time to finish: {hours}h {minutes}m {seconds}s")

    # Step 1: Get the HTML doc
    soup = BeautifulSoup(getHTMLdocument(generateScrapeURL(row["Link"])), 'lxml')

    # Step 2: Find all elements with id containing 'versions'
    targets = soup.find_all(lambda tag: tag.has_attr("id") and "versions" in tag["id"].lower())

    # Step 3: Find the first <table> after each of those elements
    if targets:
        for target in targets:
            table = target.find_next("table")
            if table:
                # Step 4: Parse table with pandas
                dfTemp = pd.read_html(str(table))[0]
                
                # Add in a model name column
                dfTemp["Model Name"] = row["Model Name"]
                
                # Ensure all expected columns are present
                expected_columns = ["Year", "Model Name", "Series", "Color", "Window Color", "Interior Color", "Country"]

                for col in expected_columns:
                    if col not in dfTemp.columns:
                        dfTemp[col] = "NA"

                # Keep only selected columns
                dfTemp = dfTemp[expected_columns]

                # Update the csv file
                dfTemp.to_csv(
                    "./Phase 2/rawPhase2.csv",
                    mode="a",
                    header = not os.path.exists("./Phase 2/rawPhase2.csv"), # Write header only if file doesn't
                    index = False
                )

            else:
                print("No table found after the element with id containing 'versions'")

    # If no element with id containing 'versions' found, that implies that product is not a Hotwheels car, and we are not interested

    # Update scrapeIndex
    with open(indexPath, "w") as f:
        f.write(str(index + 1))  # +1 to start at the next row next time

    # wait for 3 seconds between each interval => Be nice to the server
    time.sleep(3)

    


