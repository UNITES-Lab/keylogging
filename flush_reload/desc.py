import json
import pandas as pd

def analyze_json(json_file):

    # Load the JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Ensure data is a list of dictionaries
    if isinstance(data, dict):
        data = [data]  # Convert single entry to a list

    # Skip the first entry
    if len(data) > 1:
        data = data[1:] 
        
    # Convert to Pandas DataFrame
    df = pd.DataFrame(data)

    # Compute descriptive statistics
    stats = df.describe()

    # Display results
    print(stats)

if __name__ == "__main__":
    stats = analyze_json("flush_reload.json")

