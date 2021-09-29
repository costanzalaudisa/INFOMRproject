import argparse

from classes import define_classes
from filter import generate_db
from stats import plot_stats
from object import Object
from viewer import Viewer
from pathlib import Path

VERTEX_COUNT, THRESHOLD = 1000, 200
ORIGINAL_MODEL_DIR = Path("./models")
PROCESSED_MODEL_DIR = Path("./processed-models")

parser = argparse.ArgumentParser(description="INFOMR Project")
parser.add_argument("-p", "--pre-process", action="store_true", help="pre-process all models")
parser.add_argument("-c", "--generate-classes", action="store_true", help="generates the classes.txt")
parser.add_argument("-s", "--plot-stats", action="store_true", help="plots stats saved in the db")
parser.add_argument("-g", "--generate-database", choices=["o", "p"], help="generates database for either (o)riginal or (p)rocessed")
parser.add_argument("object_id", type=int, nargs='?', default=0, help="id of the pre-processed model to perform operations on")
parser.add_argument("-i", "--info", action="store_true", help="view info of selected model")
parser.add_argument("-v", "--view", action="store_true", help="view selected model")

args = parser.parse_args()

if args.pre_process:
     # Get all off_files in this directory
    off_files = list(ORIGINAL_MODEL_DIR.glob("**/*.off"))
    file_count = len(off_files)

    for i, f in enumerate(off_files):
        print(f"Pre-processing file {i} of {file_count}", end="\r")
        object = Object.load_mesh(f)
        object.remesh_to(VERTEX_COUNT, THRESHOLD)
        object.scale()
        object.center()
        object.save_mesh(PROCESSED_MODEL_DIR / f.name)

if args.generate_classes:
    define_classes(list(Path("./classes").iterdir()))

if args.plot_stats:
    plot_stats()

if args.generate_database:
    if args.generate_database.lower() == "o":
        generate_db(ORIGINAL_MODEL_DIR, Path("./psb_orig.csv"))
    elif args.generate_database.lower() == "p":
        generate_db(PROCESSED_MODEL_DIR, Path("./psb_proc.csv"))
    else:
        print(f"No valid input was found, {args.generate_database} does not equal, `o` or `p`.")

#-------------------------------------------------------#
# All subsequent functions require a model to be loaded #
#-------------------------------------------------------#
obj = None

if args.object_id is not None:
    obj = Object.load_mesh(PROCESSED_MODEL_DIR / Path(f"m{args.object_id}.off"))
else:
    if args.info or args.view:
        print("No object was selected")
    exit()

if args.info:
    # Print info on the selected mesh
    model_num, label, num_vertices, num_faces, type_faces, bounding_box = obj.get_info()

    print("#################")
    print("### MESH INFO ###")
    print("#################")
    print("Model number:", model_num)
    print("Label:", label)
    print("Number of vertices:", num_vertices)
    print("Number of faces:", num_faces)
    print("Type of faces:", type_faces)
    print("Bounding box:", bounding_box)

if args.view:
    # View the selected mesh
    viewer = Viewer(obj)
    viewer.mainLoop()
