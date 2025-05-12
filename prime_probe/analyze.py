import os
import subprocess
import numpy as np
import json

LOAD_OFFSETS = {"libgdk": 0x2A000, "libgtk": 0x3B000, "libxcbcommon": 0x4500}
LINE_SIZE = 64


def load_trace(input_file):
    """Load a memory trace from a file."""
    return np.fromfile(input_file, dtype=np.uint64)


def get_lines_in_file(filepath):
    """Read lines from a file."""
    lines = []
    try:
        with open(filepath, "r") as file:
            lines = file.readlines()
        return lines
    except IOError:
        print(f"Error reading file: {filepath}")
        return lines


def parse_readelf_symbol(line):
    """
    Parse a line from `readelf -sW` output and return a dictionary with the symbol's details.
    """

    parts = line.strip().split()

    if len(parts) < 8:
        raise ValueError(
            f"Line doesn't contain enough fields: expected 8, received {len(parts)}"
        )

    return {
        "index": int(parts[0].rstrip(":")),
        "addr": int(parts[1], 16),
        "size": int(parts[2]),
        "type": parts[3],
        "binding": parts[4],
        "visibility": parts[5],
        "section_index": parts[6],
        "name": " ".join(parts[7:]),  # Remaining parts form the symbol name
    }


def process_layout(layout):
    """
    Process the layout (output of readelf) into a list of dictionaries.
    """
    layout_obj = []
    for line in layout:
        sym_obj = parse_readelf_symbol(line)
        layout_obj.append(sym_obj)
    return layout_obj


if __name__ == "__main__":
    templates = os.listdir("templates")
    for template in templates:
        filename = template[:-4]  # Remove file extension
        print(f"processing {filename}")

        target_elf = filename.split("_")[1]  # Extract library name

        # Read memory layout and template data
        mem_layout = get_lines_in_file(f"libmem_layout/{target_elf}.log")
        layout_dict = process_layout(mem_layout)
        template_data = load_trace(f"templates/{filename}.bin")

        # Filter and sort template data based on hits
        filtered_template = sorted(
            [
                {
                    "addr": hex(i * LINE_SIZE),
                    "hits": template_data[i],
                }
                for i in range(len(template_data))
                if template_data[i] > 0
            ],
            key=lambda x: x["hits"],
            reverse=True,
        )

        # Match addresses with symbols from readelf
        for line in filtered_template:
            for symbol in layout_dict:
                if (
                    abs(
                        int(line["addr"], 16)
                        - (symbol["addr"] - symbol["addr"] % LINE_SIZE)
                    )
                    < 3 * LINE_SIZE
                ):
                    line["name"] = symbol["name"]
                    break

        # Separate matched and unmatched functions
        matched_functions = [line for line in filtered_template if "name" in line]
        unmatched_functions = [line for line in filtered_template if "name" not in line]

        print([func for func in matched_functions if func["hits"] > 50])

        # Ensure the counts match
        assert len(matched_functions) + len(unmatched_functions) == len(
            filtered_template
        )
        print(
            f"We matched {len(matched_functions)}/{len(filtered_template)} functions."
        )

        # Write the results to JSON files
        # with open(f"json/{target_elf}_matched.json", "w") as file:
        #     json.dump(matched_functions, file, indent=4)
        # with open(f"json/{target_elf}_unmatched.json", "w") as file:
        #     json.dump(unmatched_functions, file, indent=4)
