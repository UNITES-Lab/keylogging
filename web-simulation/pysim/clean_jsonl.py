import json
import os
import re

raw_data_src = "data/raw_data"
clean_data_src = "data/cleaned_data"

# Make sure output directory exists
os.makedirs(clean_data_src, exist_ok=True)

# List all files in raw_data
filenames = os.listdir(raw_data_src)

for filename in filenames:
    raw_file_path = os.path.join(raw_data_src, filename)
    clean_file_path = os.path.join(clean_data_src, filename)

    if os.path.exists(clean_file_path):
        print(f"[=] Skipping {filename} (already cleaned).")
        continue

    print(f"[+] Cleaning {filename}...")

    data = []

    # Load each file and parse each JSON object string
    with open(raw_file_path, 'r') as file:
        json_list = list(file)

    for json_str in json_list:
        try:
            json_obj = json.loads(json_str)
            data.append(json_obj)
        except json.JSONDecodeError as e:
            print(f"[!] Failed to decode JSON in {filename}: {e}")
            continue

    cleaned_data = []
    dropped_count = 0

    for obj in data:
        interval_str_list = obj.get("intervals", "").split(',')

        if '' in interval_str_list:
            dropped_count += 1
            continue

        try:
            obj["intervals"] = [int(s) for s in interval_str_list]
            obj["keystrokes"] = re.findall(r'<(.*?)>', obj.get("keystrokes", ""))
            obj["participant_id"] = int(obj.get("participant_id", 0))
            cleaned_data.append(obj)
        except Exception as e:
            print(f"[!] Error processing entry in {filename}: {e}")
            continue

    # Write cleaned data
    with open(clean_file_path, 'w') as out_file:
        json.dump(cleaned_data, out_file)

    print(f"[✓] Finished cleaning {filename} ({len(cleaned_data)} entries, dropped {dropped_count}).")

