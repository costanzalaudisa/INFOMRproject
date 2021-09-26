from object import Object
from viewer import Viewer
import pprint
import json

def define_classes(files):
    classes = []
    for file in files:
        # Read lines avoiding empty ones
        with open(file) as f_in:
            lines = (line.rstrip() for line in f_in) 
            lines = list(line for line in lines if line) # Non-blank lines in a list

        lines = lines[2:] # Ignore first 2 lines as they only contain info about DB's version

        for i in range(len(lines)):
            words = lines[i].split()                                        # Split each line into "words" using space separator
            if len(words) == 3:                                             # If line consists of 3 words it's listing classes (and not model numbers)
                if words[1].isnumeric() and not words[0] in classes:        # If second word is a number, the line is listing a parent class
                    classes.append(words[0])                                # Add class if it's not already there

    classes = sorted(classes)
    
    # Initialize dictionary
    dict = {}
    for c in classes:
        dict[c] = []

    current_class = ""
    for file in files:
            # Read lines avoiding empty ones
            with open(file) as f_in:
                lines = (line.rstrip() for line in f_in) 
                lines = list(line for line in lines if line)

            lines = lines[2:]                                   # Ignore first 2 lines as they only contain info about DB's version
            for i in range(len(lines)):
                words = lines[i].split()
                if words[0] in classes:                         # If first word is a class, note down the current class
                    current_class = words[0]                         
                if len(words) == 1:                             # If line consists of 1 word only it's listing model numbers (and not classes)
                    if current_class in dict.keys():            # If class is in the dictionary, add model number to the list
                        dict[current_class].append(words[0])

    # Sort the list of model numbers
    for value in dict:
        dict[value].sort()

    # Write dictionary to file
    with open('classes.txt', 'w') as convert_file:
     convert_file.write(json.dumps(dict))