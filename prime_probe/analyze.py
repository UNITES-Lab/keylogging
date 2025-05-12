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


# https://stackoverflow.com/questions/50916422/python-typeerror-object-of-type-int64-is-not-json-serializable
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


if __name__ == "__main__":
    tp_dict = {"chrome": {}, "gedit": {}}
    templates = os.listdir("templates")
    for template in templates:
        filename = template[:-4]  # Remove file extension
        print(f"processing {filename}")

        [program, target_elf, dummy] = filename.split("_")  # Extract library name

        # Read memory layout and template data
        if program == "chrome" and target_elf == "libgtk":
            mem_layout = get_lines_in_file(f"libmem_layout/{program}_{target_elf}.log")
        else:
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

        tp_dict[program][target_elf] = filtered_template

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

        # Ensure the counts match
        assert len(matched_functions) + len(unmatched_functions) == len(
            filtered_template
        )
        print(
            f"We matched {len(matched_functions)}/{len(filtered_template)} functions."
        )

    both_used_lines = {}
    for key in tp_dict["chrome"]:
        print(f"common addresses in {key} for chrome and gedit")
        temp_chrome = tp_dict["chrome"][key]
        temp_gedit = tp_dict["gedit"][key]
        both_used_lines[key] = []
        for i in range(len(temp_chrome)):
            for j in range(len(temp_gedit)):
                if (
                    abs(
                        int(temp_chrome[i]["addr"], 16) - int(temp_gedit[j]["addr"], 16)
                    )
                    < 3 * LINE_SIZE
                ):
                    already_appended = False
                    for obj in both_used_lines[key]:
                        if temp_chrome[i]["addr"] == obj["addr"]:
                            already_appended = True
                            break
                    if not already_appended:
                        both_used_lines[key].append(
                            {
                                **temp_chrome[i],
                                "gedit_hits": temp_gedit[j]["hits"],
                                "gedit_addr": temp_gedit[j]["addr"],
                            }
                        )

    with open("common_lines.json", "w") as f:
        json.dump(both_used_lines, f, indent=4, cls=NpEncoder)

    with open("hits.json", "w") as f:
        json.dump(tp_dict, f, indent=4, cls=NpEncoder)
