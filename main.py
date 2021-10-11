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
ORIGINAL_DB = Path("./psb_orig.csv")
PROCESSED_DB = Path("./psb_proc.csv")

parser = argparse.ArgumentParser(description="INFOMR Project")
parser.add_argument("-p", "--pre-process", action="store_true", help="pre-process all models")
parser.add_argument("-c", "--generate-classes", action="store_true", help="generate the classes.txt")
parser.add_argument("-s", "--plot-stats", choices=["o", "p"], help="plot stats saved in the db for either (o)riginal or (p)rocessed")
parser.add_argument("-g", "--generate-database", choices=["o", "p"], help="generate database for either (o)riginal or (p)rocessed")
parser.add_argument("object_id", type=int, nargs='?', default=0, help="id of the pre-processed model to perform operations on")
parser.add_argument("-i", "--info", choices=["o", "p"], help="view info of selected model")
parser.add_argument("-v", "--view", choices=["o", "p"], help="view selected model")
parser.add_argument("-k", "--check-model", choices=["o", "p"], help="check issues of selected model")
parser.add_argument("-K", "--check-db", choices=["o", "p"], help="check issues of entire dataset")

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
    if args.info or args.view:
        print("No object was selected")
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
    model_num, label, num_vertices, num_faces, num_edges, type_faces, bounding_box, surface, watertight = obj.get_info()

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
    print("Surface area:", surface)

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
