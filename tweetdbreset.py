import csv
from glob import glob
import os

for filename in glob("./public_dataset/**/tweets/**/*.csv", recursive=True):
    with open(filename, 'r') as file:
        lines = file.readlines()

    if 'UserScreenName' in lines[0]:
        continue

    flines = [lines[0]]
    for l in lines[1:]:
        stripped_line = l.strip()  # Remove leading/trailing whitespace
        if stripped_line:
            token1 = stripped_line.split(",", 1)[0]
            if not token1.isnumeric():
                # If line starts with alphabet, combine with the previous line
                flines[-1] = flines[-1].strip() + " " + stripped_line + "\n"
            else:
                # Otherwise, add the line as a new one
                flines.append(l)
    
    # print(flines)
    with open(filename, 'w') as file:
        file.writelines(flines)