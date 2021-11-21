# INFOMR Project: Content-based Shape Retrieval System

Given a certain 3D shape, this content-based 3D shape retrieval system is capable of returning the most similar shapes from a 3D shape database, namely the Princeton Shape Benchmark database. This process consists of several steps, including reading the 3D data, pre-processing the data, extracting features from the data, querying data, and so on.

## Instructions

The system was implemented in Python 3.9, so ensure the correct version of Python is installed in your local machine. It is required to install multiple libraries to make the system run properly. 

### Libraries installation

The list of required libraries can be found in the `requirements.txt` file. All libraries can be easily installed by running `pip install -r requirements.txt` in a terminal (ensure Pip is correctly installed), except for the Open3D library which must be installed manually, since no Python 3.9 release exists yet on PyPi.

#### Open3D installation on Windows
`pip install https://storage.googleapis.com/open3d-releases-master/python-wheels/open3d-0.13.0+61646ce-cp39-cp39-win_amd64.whl`

#### Open3D installation on MacOS
`pip install https://storage.googleapis.com/open3d-releases-master/python-wheels/open3d-0.13.0+61646ce-cp39-cp39-macosx_10_14_x86_64.whl`

#### Open3D installation on Linux
`pip install https://storage.googleapis.com/open3d-releases-master/python-wheels/open3d-0.13.0+61646ce-cp39-cp39-manylinux_2_27_x86_64.whl`

### System commands

The system works via terminal commands. Once the repository has been downloaded, open a terminal in the repository folder. The ```main.py``` file must be run with various arguments that allow different functions; running ```python main.py -h``` shows all the possible arguments with the appropriate usage.

The arguments are:

- `-p` which pre-processes the database
- `-c` which extracts classes from the database and generates the classes.txt file
- `-s {o,p}` which gathers and plots stats for either the (o)riginal or (p)rocessed database
- `-g {o,p}` which extracts features and generates a .csv file for either (o)riginal or (p)rocessed database
- `-i {o,p} {model_num}` which retrieves info and features of a selected model from either the (o)riginal or (p)rocessed database
- `-v {o,p} {model_num}` which visualized a selected model from either the (o)riginal or (p)rocessed database
- `-k {o,p} {model_num}` which checks for issues with a selected model from either the (o)riginal or (p)rocessed database
- `-K {o,p}` which checks for issues in the entire (o)riginal or (p)rocessed database
- `-q {ed,cd,emd,ann} {model_num} {k_value}` which finds similar k shapes for a selected model from the processed database ('ed' for Euclidean distance, 'cd' for Cosine distance, 'emd' for Earth Mover's distance, 'ann' for ANN on Manhattan distance)
- `-a {k_value}` which evaluates the system with a selected k value

If no `model_num` or `k_value` is specified, defaults will be used instead (model 0 from the database and k=5 respectively). All the necessary files are already included in this repository, so there is no need to pre-process the database, generate classes, or extract features.
