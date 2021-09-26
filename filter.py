import os
import sys
import re
import json
import numpy as np

path = "./models"
txt_format = ".txt"
off_format = ".off"

# Read classes
with open('classes.txt') as f:
    data = f.read()
dict = json.loads(data)

# Get mesh info
def get_info(file):
    root = os.path.dirname(file)

    # Check if directory exists or if it's empty
    if not os.path.exists(root):
        print("Error: directory of file '", file, "' does not exist")
        sys.exit()
    if len(os.listdir(root)) == 0:
        print("Error: directory of file '", file, "' is empty")
        sys.exit()
 
    # List content of directory
    list_files = os.listdir(root)       
    
    # Initialize variables
    label = ""
    model_num = ""
    num_vertices = 0
    num_faces = 0
    type_face = ""
    min_box = np.array([0.0, 0.0, 0.0])
    max_box = np.array([0.0, 0.0, 0.0])

    for file in list_files:             
        ### Number of vertices & faces ###
        if off_format in file:                                  # If file is in off_format, pick up number of vertices and faces
            with open(root + "/" + file) as f_in:               # Open file and read lines
                lines = (line.rstrip() for line in f_in) 
                lines = list(line for line in lines if line)    # Non-blank lines in a list
            words = lines[1].split()                            # Number of vertices and faces are listed in the second line
            num_vertices = eval(words[0])                       # Number of vertices is first number
            num_faces = eval(words[1])                          # Number of faces is second number

        ### Class and bounding box ###
        if txt_format in file:                                  # If file is in off_format, pick up class and bounding box
            with open(root + "/" + file) as f_in:               # Open file and read lines
                lines = (line.rstrip() for line in f_in) 
                lines = list(line for line in lines if line)
                        
            ### Class ###
            for word in lines[0].split():                   # Model number is listed in the first line
                if word.isdigit():
                    model_num = word
                    for key in dict.keys():                 # Check which label belongs to model by looking up the dictionary
                        if model_num in dict[key]:
                            label = key

            ### Bounding box ###
            for word in lines[8].split(","):                # Bounding box is listed in the ninth line
                if "xmin" in word:
                    min_box[0] = float(re.findall("\d+\.\d+", word)[0])
                elif "ymin" in word:
                    min_box[1] = float(re.findall("\d+\.\d+", word)[0])
                elif "zmin" in word:
                    min_box[2] = float(re.findall("\d+\.\d+", word)[0])
                elif "xmax" in word:
                    max_box[0] = float(re.findall("\d+\.\d+", word)[0])
                elif "ymax" in word:
                    max_box[1] = float(re.findall("\d+\.\d+", word)[0])
                elif "zmax" in word:
                    max_box[2] = float(re.findall("\d+\.\d+", word)[0])                        
                bounding_box = np.concatenate((min_box, max_box), axis=0)
    
    print("#################")
    print("### MESH INFO ###")
    print("#################")
    print("Model number:", model_num)
    print("Label:", label)
    print("Number of vertices:", num_vertices)
    print("Number of faces:", num_faces)
    print("Bounding box:", bounding_box)