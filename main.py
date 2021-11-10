import argparse

from classes import define_classes
from filter import generate_db
from stats import plot_stats
from object import Object
from viewer import Viewer
from pathlib import Path
from query import query, normalize, build_ann, get_query_accuracy

import matplotlib.pyplot as plt

VERTEX_COUNT, THRESHOLD = 1000, 200
ORIGINAL_MODEL_DIR = Path("./models")
PROCESSED_MODEL_DIR = Path("./processed-models")
ORIGINAL_DB = Path("./psb_orig.csv")
PROCESSED_DB = Path("./psb_proc.csv")

parser = argparse.ArgumentParser(description="INFOMR Project")
parser.add_argument("-p", "--pre-process", action="store_true", help="pre-process all models.")
parser.add_argument("-c", "--generate-classes", action="store_true", help="generate the classes.txt file.")
parser.add_argument("-s", "--plot-stats", choices=["o", "p"], help="plot stats saved in the db for either (o)riginal or (p)rocessed.")
parser.add_argument("-g", "--generate-database", choices=["o", "p"], help="generate database for either (o)riginal or (p)rocessed.")
parser.add_argument("object_id", type=int, nargs='?', default=0, help="id of the pre-processed model to perform operations on.")
parser.add_argument("k_value", type=int, nargs='?', default=5, help="k-value for the query.")
parser.add_argument("-i", "--info", choices=["o", "p"], help="view info of selected model. Usage: {database} {model number}.")
parser.add_argument("-v", "--view", choices=["o", "p"], help="view selected model. Usage: {database} {model number}.")
parser.add_argument("-k", "--check-model", choices=["o", "p"], help="check issues of selected model. Usage: {database} {model number}.")
parser.add_argument("-K", "--check-db", choices=["o", "p"], help="check issues of entire dataset. Usage: {database} {model number}.")
parser.add_argument("-q", "--query", choices=["ed", "cd", "emd", "ann"], help="find similar shapes ('ed' for Euclidean distance, 'cd' for Cosine distance, 'emd' for Earth Mover's distance, 'ann' for ANN (on Manhattan distance). Usage: {metric} {model number} {k value}.")
parser.add_argument("-a", "--accuracy", type=int, help="get accuracy of distance functions.")

args = parser.parse_args()

if args.pre_process:
     # Get all off_files in this directory
    off_files = list(ORIGINAL_MODEL_DIR.glob("**/*.off"))
    file_count = len(off_files)

    for i, f in enumerate(off_files):
        print(f"Pre-processing file {i} of {file_count}", end="\r")
        object = Object.load_mesh(f)
        object.preprocess(VERTEX_COUNT, THRESHOLD)
        object.save_mesh(PROCESSED_MODEL_DIR / f.name)

if args.generate_classes:
    define_classes(list(Path("./classes").iterdir()))

if args.plot_stats:
    if args.plot_stats.lower() == "o":
        plot_stats(ORIGINAL_DB)
    elif args.plot_stats.lower() == "p":
        plot_stats(PROCESSED_DB)
    else:
        print(f"No valid input was found, {args.plot_stats} does not equal, `o` or `p`.")

if args.generate_database:
    if args.generate_database.lower() == "o":
        generate_db(ORIGINAL_MODEL_DIR, ORIGINAL_DB)
    elif args.generate_database.lower() == "p":
        generate_db(PROCESSED_MODEL_DIR, PROCESSED_DB)
    else:
        print(f"No valid input was found, {args.generate_database} does not equal, `o` or `p`.")

#-------------------------------------------------------#
# All subsequent functions require a model to be loaded #
#-------------------------------------------------------#
obj = None

if args.object_id is None:
    if args.info or args.view or args.query:
        print("No object was selected")
    exit()

if args.k_value is None:
    if args.info or args.view or args.query:
        print("No k-value was selected")
    exit()

if args.info:
    if args.object_id is not None:
        if args.info.lower() == "o":
            obj = Object.load_mesh(list(ORIGINAL_MODEL_DIR.glob(f"**/m{args.object_id}.off"))[0])
        elif args.info.lower() == "p":
            obj = Object.load_mesh(list(PROCESSED_MODEL_DIR.glob(f"**/m{args.object_id}.off"))[0])
        else:
            print(f"No valid input was found, {args.info} does not equal, `o` or `p`.")

    # Print info on the selected mesh
    model_num, label, num_vertices, num_faces, num_edges, type_faces, bounding_box, barycenter, diagonal, surface, bounding_box_volume, volume, compactness, diameter, eccentricity, A3, D1, D2, D3, D4 = obj.get_info()

    print("\r")
    print("#################")
    print("### MESH INFO ###")
    print("#################")
    print("Model number:", model_num)
    print("Label:", label)
    print("Number of vertices:", num_vertices)
    print("Number of faces:", num_faces)
    print("Number of edges:", num_edges)
    print("Type of faces:", type_faces)
    print("Bounding box:", bounding_box)
    print("\r")
    print("################")
    print("### FEATURES ###")
    print("################")
    print("Surface area:", surface)
    print("Bounding box volume:", bounding_box_volume)
    print("Mesh volume:", volume)
    print("Compactness:", compactness)
    print("Diameter:", diameter)
    print("Eccentricity", eccentricity)

if args.view:
    if args.object_id is not None:
        if args.view.lower() == "o":
            obj = Object.load_mesh(list(ORIGINAL_MODEL_DIR.glob(f"**/m{args.object_id}.off"))[0])
        elif args.view.lower() == "p":
            obj = Object.load_mesh(list(PROCESSED_MODEL_DIR.glob(f"**/m{args.object_id}.off"))[0])
        else:
            print(f"No valid input was found, {args.view} does not equal, `o` or `p`.")                           

    # View the selected mesh
    viewer = Viewer(obj)
    viewer.mainLoop()

if args.check_model:
    if args.object_id is not None:
        if args.check_model.lower() == "o":
            obj = Object.load_mesh(list(ORIGINAL_MODEL_DIR.glob(f"**/m{args.object_id}.off"))[0])
        elif args.check_model.lower() == "p":
            obj = Object.load_mesh(list(PROCESSED_MODEL_DIR.glob(f"**/m{args.object_id}.off"))[0])
        else:
            print(f"No valid input was found, {args.info} does not equal, `o` or `p`.")

    # Print info on the selected mesh
    model_num, watertight, winding, normals, pos_volume = obj.check_model()

    print("### Checking model", model_num, "###")
    print("Is mesh watertight?", watertight)
    print("Does mesh have consistent winding?", watertight)
    print("Does mesh have outward facing normals?", watertight)
    print("Does mesh have positive volume?", pos_volume)

if args.check_db:
    if args.object_id is not None:
        if args.check_db.lower() == "o":
            off_files = list(ORIGINAL_MODEL_DIR.glob("**/*.off"))
        elif args.check_db.lower() == "p":
            off_files = list(PROCESSED_MODEL_DIR.glob("**/*.off"))
        else:
            print(f"No valid input was found, {args.info} does not equal, `o` or `p`.")

    file_count = len(off_files)

    watertight_count = 0
    winding_count = 0
    normals_count = 0
    volume_count = 0

    for i, f in enumerate(off_files):
        print(f"Checking file {i} of {file_count}", end="\r")
        object = Object.load_mesh(f)
        model_num, watertight, winding, normals, pos_volume = object.check_model()

        if not watertight:
            watertight_count += 1
        if not winding:
            winding_count += 1
        if not normals:
            normals_count += 1
        if not pos_volume:
            volume_count += 1

    print("\n")
    print("# Number of non-watertight meshes:", watertight_count, "out of", file_count)
    print("# Number of meshes with inconsistent winding:", winding_count, "out of", file_count)
    print("# Number of meshes with no outward facing normals:", normals_count, "out of", file_count)
    print("# Number of meshes with non-positive volume:", volume_count, "out of", file_count)

if args.query:
    if args.object_id is not None:
        if args.k_value is not None:
            obj = Object.load_mesh(list(PROCESSED_MODEL_DIR.glob(f"**/m{args.object_id}.off"))[0])

            if args.query.lower() == "ed":
                query(obj, 'ed', args.k_value)
            elif args.query.lower() == "cd":
                query(obj, 'cd', args.k_value)
            elif args.query.lower() == "emd":
                query(obj, 'emd', args.k_value)
            elif args.query.lower() == "ann":
                query(obj, 'ann', args.k_value)
            else:
                print(f"No valid input was found, {args.query} does not equal `ed`, `cd`, `emd` or `ann`.")
    
if args.accuracy:           
    if args.accuracy is not None:
        get_query_accuracy(str(PROCESSED_DB), args.accuracy)