import json
import os
import math

def split_json_file(json_file, parts, output_prefix="split_"):
    """
    Splits a JSON file (assumed to contain a list of items) into a specified
    number of equal parts and saves each part into a new file.

    Parameters:
      json_file (str): Path to the input JSON file.
      parts (int): Number of parts to split the data into.
      output_prefix (str): Prefix for output files. Files will be named
                           <output_prefix>1.json, <output_prefix>2.json, etc.
    """
    # Load the JSON data from file.
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Ensure that the JSON data is a list.
    if not isinstance(data, list):
        raise ValueError("Expected the JSON data to be a list.")

    total_items = len(data)
    # Calculate the size of each chunk (round up to ensure all items are included)
    chunk_size = math.ceil(total_items / parts)

    print(f"Total items: {total_items}")
    print(f"Splitting into {parts} parts (chunk size: {chunk_size}).")

    # Create output directory if desired (optional)
    output_dir = "split_json_files"
    os.makedirs(output_dir, exist_ok=True)

    # Split and save each chunk.
    for i in range(parts):
        start = i * chunk_size
        end = start + chunk_size
        chunk = data[start:end]
        output_file = os.path.join(output_dir, f"{output_prefix}4_{i+1}.jsonl")
        with open(output_file, "w") as out:
            json.dump(chunk, out)
        print(f"Wrote {output_file} with {len(chunk)} items.")

if __name__ == "__main__":
    # Example usage:
    input_json = "split_json_files/split_4.jsonl"  # Replace with your JSON file path.
    num_parts = 2             # Replace with the number of parts you desire.
    split_json_file(input_json, num_parts)