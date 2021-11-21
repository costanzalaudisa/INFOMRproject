import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
pd.set_option('display.float_format', lambda x: '%.3f' % x)

# Plot histograms of specified value
def plot(df, value):
    plt.figure(figsize=(18,6))
    plt.xlabel(value)
    plt.ylabel('count')
    plt.hist(df[value], bins=25, rwidth = 0.9) # recommended 10-25 bins
    plt.show()

# Gather database statistics and run checks
def plot_stats(db_path):
    df = pd.read_csv(db_path)
    stats = df[df.columns.difference(["Model Number"])].describe()
    print('\r')
    print("#############")
    print("### STATS ###")
    print("#############")
    print(stats)

    min_vertices = df['Number of vertices'].min()
    mean_vertices = df['Number of vertices'].mean()
    max_vertices = df['Number of vertices'].max()
    min_faces = df['Number of faces'].min()
    mean_faces = df['Number of faces'].mean()
    max_faces = df['Number of faces'].max()

    print("\n# Vertices and faces stats #")
    print("Number of vertices -> min:", min_vertices, " | max:", max_vertices, " | mean:", round(mean_vertices, 2))
    print("Number of faces -> min:", min_faces, " | max:", max_faces, " | mean:", round(mean_faces, 2))

    # Get count of meshes with certain type of faces
    triangles_count = len(df[df['Type of faces'] == 'triangles'])
    quads_count = len(df[df['Type of faces'] == 'quads'])
    print("\n# Type of faces #")
    print("Number of meshes with triangle faces:", triangles_count)
    print("Number of meshes with quads faces:", quads_count)

    plot(df, "Number of vertices")
    plot(df, "Number of faces")

    count_outliers(df)
    check_centering(df)
    check_scaling(df)
    features_stats(df)

# Count database's outliers
def count_outliers(df):
    # Gather models with minimum and maximum values
    outliers = []

    min_vertices = df['Number of vertices'].min()
    mean_vertices = df['Number of vertices'].mean()
    max_vertices = df['Number of vertices'].max()
    min_faces = df['Number of faces'].min()
    mean_faces = df['Number of faces'].mean()
    max_faces = df['Number of faces'].max()

    # Get count of meshes around average
    threshold = 1000
    below_opt = df.apply(lambda x : True if x['Number of vertices'] <= mean_vertices - threshold else False, axis = 1)
    above_opt = df.apply(lambda x : True if x['Number of vertices'] >= mean_vertices + threshold else False, axis = 1)
    count_below = len(below_opt[below_opt == True].index)
    count_above = len(above_opt[above_opt == True].index)

    print("\n# Meshes outside average #")
    print("Total number of meshes:", df.shape[0], " |   average number of vertices:", mean_vertices)
    print("Number of meshes below average number of vertices:", count_below)
    print("Number of meshes above average number of vertices:", count_above)

    # Get outliers
    print("\r")
    print("################")
    print("### OUTLIERS ###")
    print("################")

    min_vertices_models = df.loc[df['Number of vertices'] == min_vertices]["Model number"]
    print("Models with minimum number of vertices:", end=' ')
    for model in min_vertices_models:
        print(model, end=' ')
        outliers.append(model)

    max_vertices_models = df.loc[df['Number of vertices'] == max_vertices]["Model number"]
    print("\nModels with maximum number of vertices:", end=' ')
    for model in max_vertices_models:
        print(model, end=' ')
        outliers.append(model)

    min_faces_models = df.loc[df['Number of faces'] == min_faces]["Model number"]
    print("\nModels with minimum number of faces:", end=' ')
    for model in min_faces_models:
        print(model, end=' ')
        outliers.append(model)

    max_faces_models = df.loc[df['Number of faces'] == max_faces]["Model number"]
    print("\nModels with maximum number of faces:", end=' ')
    for model in max_faces_models:
        print(model, end=' ')
        outliers.append(model)

    outliers = sorted(list(set(outliers)))
    print("\nDatabase outliers:", outliers)

# Check if centering process was successful
def check_centering(df):
    # Get distance from origin to check centering process
    print("\r")
    print("#################")
    print("### CENTERING ###")
    print("#################")

    df['Barycenter'] = df['Barycenter'].str.replace("nan", "0")
    df['Barycenter'] = df['Barycenter'].apply(eval).apply(np.array)

    df["Distance from origin"] = df["Barycenter"].apply(np.linalg.norm)
    df["Distance from origin"] = df["Distance from origin"].round(5)
    print(df["Distance from origin"])

    print("DISTANCE FROM ORIGIN STATS:")
    print(df["Distance from origin"].describe())
   
    plot(df, "Distance from origin")

# Check if scaling process was successful
def check_scaling(df):
    # Get bounding box diagonal and max edge to check scaling process
    print("\r")
    print("###############")
    print("### SCALING ###")
    print("###############")

    df['Bounding box'] = df['Bounding box'].str.replace("nan", "0")
    df['Bounding box'] = df['Bounding box'].apply(eval).apply(np.array)
    df['Max bound'] = df['Bounding box'].apply(lambda x: max(np.abs(x[0] - x[1])))

    print("MAX BOUND STATS")
    print(df["Max bound"].describe())

    print("\r")
    print("DIAGONAL STATS")
    print(df["Diagonal"].describe())

    # Plot two histograms in the same plot
    plt.figure(figsize=(18,6))
    plt.ylabel('count')
    plt.hist(df["Max bound"], bins=25, rwidth = 0.9, label="Longest edge") # recommended 10-25 bins
    plt.hist(df["Diagonal"], bins=25, rwidth = 0.9, label="Diagonal")
    plt.legend(loc="upper left")
    plt.show()

# Gather feature's stats
def features_stats(df):
    # Get descriptors statistics
    print("\r")
    print("################")
    print("### FEATURES ###")
    print("################")

    print("SURFACE STATS")
    print(df["Surface"].describe())

    print("BOUNDING BOX VOLUME STATS")
    print(df["Bounding box volume"].describe())

    print("CONVEX HULL VOLUME STATS")
    print(df["Convex hull volume"].describe())

    print("COMPACTNESS STATS")
    print(df["Compactness"].describe())

    print("ECCENTRICITY STATS")
    print(df["Eccentricity"].describe())