import os
import sys
import re
import json
import numpy as np
import pandas as pd
import trimesh

path = "./models"
txt_format = ".txt"
off_format = ".off"

# Read classes
with open('classes.txt') as f:
    data = f.read()
dict = json.loads(data)

# Get mesh info
def get_info(file):
    # Get mesh
    mesh = trimesh.load(file, force="mesh")

    # Get file's directory name
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
    num_vertices = mesh.vertices.shape[0]
    num_faces = mesh.faces.shape[0]
    type_faces = mesh.faces.shape[1]
    bounding_box = mesh.bounds

    for file in list_files:             
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

    if label == "" or model_num == "":
        print("Mesh has no label.")
        model_num = "N/A"
        label = "N/A"

    if type_faces == "":
        print("No info regarding type of faces.")
        type_faces = "N/A"

    return model_num, label, num_vertices, num_faces, type_faces, bounding_box

def get_db_info(dir):
    data = []

    # List all directories inside the provided directory
    for root, dirs, files in os.walk(dir):
        if len(dirs) == 0 and len(files) > 0:   # If number of directories is zero we've reached the last child directory
            list_files = os.listdir(root)
            model_num, label, num_vertices, num_faces, type_faces, bounding_box = get_info(root+"/"+list_files[0])
            info = [model_num, label, num_vertices, num_faces, type_faces, bounding_box]
            data.append(info)

    # Save data as Dataframe and export it to CSV file
    df = pd.DataFrame(data, columns=['Model number', 'Label', '# of vertices', "# of faces", "Type of faces", "Bounding box"])
    df.to_csv("psb.csv", index=False)