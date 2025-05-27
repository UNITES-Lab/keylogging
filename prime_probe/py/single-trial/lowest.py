import json

# Load the JSON data (as a list of dicts)
with open("data/cleaned_data/across_participant_across_sentence_test.jsonl", "r", encoding="utf-8") as f:
    data = json.load(f)

min_interval = float('inf')
min_record = {}

for record in data:
    intervals = record.get("intervals", [])
    if intervals:
        record_min = min(intervals)
        if record_min < min_interval:
            min_interval = record_min
            min_record = {
                "participant_id": record["participant_id"],
                "test_section_id": record["test_section_id"],
                "sentence_id": record["sentence_id"],
                "min_interval": record_min
            }

print("Absolute Minimum Interval Info:")
print(min_record)
