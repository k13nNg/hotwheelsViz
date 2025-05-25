import pandas as pd

# read in the raw csv scrape file
df = pd.read_csv("./Phase 1/rawPhase1.csv")

print(f"Before drop duplicates: {df.shape}")

# drop duplicated rows (rows that have the same model listed, but in different years)
processed = df.drop_duplicates(subset=['Name', "Link"])

# Sanity check - After dropping duplicates, the number of rows should be smaller
print(f"After drop duplicates: {processed.shape}")

# save changes
processed.to_csv("processedPhase1.csv", index= False)
