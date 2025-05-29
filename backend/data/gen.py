import pandas as pd

# Load the file, skipping any repeated header rows
df = pd.read_csv('laptops.csv', on_bad_lines='skip')

# Remove any rows that are exact duplicates
df = df.drop_duplicates()

# Remove duplicates based on Brand + Model
df = df.drop_duplicates(subset=['Brand', 'Model'])

# Save cleaned file
df.to_csv('laptops_cleaned.csv', index=False)
