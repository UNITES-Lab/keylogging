#!/usr/bin/env python3
import csv

def convert_space_separated_to_csv(input_file, output_file):
    """
    Reads a space-separated text file and writes a CSV where:
      1) PARTICIPANT_ID -> tokens[0]
      2) TEST_SECTION_ID -> tokens[1]
      3) SENTENCE_USER_INPUT -> everything from tokens[2] up to the last 5 tokens
      4) KEYSTROKE_ID -> tokens[-5]
      5) PRESS_TIME -> tokens[-4]
      6) RELEASE_TIME -> tokens[-3]
      7) LETTER -> tokens[-2]
      8) KEYCODE -> tokens[-1]
    """

    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', newline='', encoding='utf-8') as f_out:

        # Use csv.writer for proper CSV formatting
        writer = csv.writer(f_out)

        # Read lines and strip out trailing spaces/newlines
        lines = [line.strip() for line in f_in if line.strip()]

        # --------------------------
        # Process the header row
        # --------------------------
        # The first line is the header in your example. We split it to get
        # original 9 columns, but we will write only 8 columns in the new CSV
        # because SENTENCE and USER_INPUT become a single column.
        header_line = lines[0]
        header_tokens = header_line.split()

        # Create a new header reflecting the combined column
        # Original: [PARTICIPANT_ID, TEST_SECTION_ID, SENTENCE, USER_INPUT,
        #            KEYSTROKE_ID, PRESS_TIME, RELEASE_TIME, LETTER, KEYCODE]
        # New:      [PARTICIPANT_ID, TEST_SECTION_ID, SENTENCE_USER_INPUT,
        #            KEYSTROKE_ID, PRESS_TIME, RELEASE_TIME, LETTER, KEYCODE]
        new_header = [
            header_tokens[0],   # PARTICIPANT_ID
            header_tokens[1],   # TEST_SECTION_ID
            header_tokens[2] + "_" + header_tokens[3],  # SENTENCE_USER_INPUT combined
            header_tokens[4],   # KEYSTROKE_ID
            header_tokens[5],   # PRESS_TIME
            header_tokens[6],   # RELEASE_TIME
            header_tokens[7],   # LETTER
            header_tokens[8]    # KEYCODE
        ]
        writer.writerow(new_header)

        # --------------------------
        # Process the data lines
        # --------------------------
        for data_line in lines[1:]:
            tokens = data_line.split()

            # We must ensure we have enough tokens to parse:
            # - At least 2 tokens for participant/test_section
            # - At least 5 tokens for keystroke info
            # - Middle tokens for combined S+U
            if len(tokens) < 2 + 5:
                print(f"Skipping malformed line (not enough tokens): {data_line}")
                continue

            participant_id = tokens[0]
            test_section_id = tokens[1]

            # Last 5 tokens correspond to KEYSTROKE_ID, PRESS_TIME, RELEASE_TIME, LETTER, KEYCODE
            keystroke_id = tokens[-5]
            press_time = tokens[-4]
            release_time = tokens[-3]
            letter = tokens[-2]
            keycode = tokens[-1]

            # Everything between tokens[2] and tokens[-5] is the combined SENTENCE+USER_INPUT
            middle_tokens = tokens[2:-5]
            sentence_user_input = " ".join(middle_tokens)

            # Write 8 columns to CSV
            writer.writerow([
                participant_id,
                test_section_id,
                sentence_user_input,
                keystroke_id,
                press_time,
                release_time,
                letter,
                keycode
            ])

if __name__ == "__main__":
    # Adjust these paths as needed
    input_txt = "data.txt"
    output_csv = "data.csv"

    convert_space_separated_to_csv(input_txt, output_csv)
    print(f"Conversion complete. Output saved to {output_csv}")
