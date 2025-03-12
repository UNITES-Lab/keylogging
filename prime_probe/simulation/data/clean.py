import json
import os
import re

raw_data_src = "raw_data"
clean_data_src = "cleaned_data"

# list out all files in the raw_data folder 
filenames = os.listdir(raw_data_src)

for filename in filenames:
    data = [] # store the raw data for each file

    # open each file and convert to a json object strings 
    with open(f'{raw_data_src}/{filename}', 'r') as file:
        json_list = list(file);

    # convert each json string in the list to an object and add to raw_data 
    for json_str in json_list:
        json_obj = json.loads(json_str)
        data.append(json_obj)
    
    for obj in data:
        # convert interval to a list of integers 
        interval_str_list = obj["intervals"].split(',') 
        intervals = [int(interval_str) for interval_str in interval_str_list]
        obj["intervals"] = intervals
        
        # convert keystroke to a list of strings
        keystroke_str = obj["keystrokes"]
        keystrokes = re.findall(r'<(.*?)>', keystroke_str)
        obj["keystrokes"] = keystrokes

        # convert participant id to integer
        obj["participant_id"] = int(obj["participant_id"])
    
    # write-back clean file to cleaned_dir
    with open(f'{clean_data_src}/{filename}', 'w') as file:
        json.dump(data, file)

