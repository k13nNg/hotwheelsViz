from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
import time

def getHTMLdocument(url):
    response = requests.get(url)
    return response.text

def generateScrapeURL(year):
    return f"https://hotwheels.fandom.com/wiki/Category:{year}_Hot_Wheels"

for year in range(1968, 2027):
    print("Opening year:", year)
    soup = BeautifulSoup(getHTMLdocument(generateScrapeURL(year)), 'html.parser')

    yearList = []

    for carElem in soup.find_all("a", {"class": "category-page__member-link"}):
        yearList.append({
            "Year": year,
            "Name": carElem.get("title"),
            "Link": carElem.get("href")
        })

    if yearList:  # only write if there's something to write
        df = pd.DataFrame(yearList)
        if not os.path.exists("Name_and_Link.csv"):
            df.to_csv("Name_and_Link.csv", index=False)
        else:
            df.to_csv("Name_and_Link.csv", mode='a', header=False, index=False)

    time.sleep(3)

print("Scrape process done!")
