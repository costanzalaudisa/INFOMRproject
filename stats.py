import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def plot(df):
    # Plot histograms of number of vertices
    plt.figure(figsize=(18,6))
    plt.xlabel('Number of vertices')
    plt.ylabel('count')
    plt.hist(df["Number of vertices"], bins=25, rwidth = 0.9) # recommended 10-25 bins
    plt.show()

    # Plot histograms of number of faces
    plt.figure(figsize=(18,6))
    plt.xlabel('Number of faces')
    plt.ylabel('count')
    plt.hist(df["Number of faces"], bins=25, rwidth = 0.9) # recommended 10-25 bins
    plt.show()

def plot_stats(db_path):
    # Gather database statistics
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

    #count_outliers(df)
    #check_centering(df)
    check_scaling(df)
    #plot(df)

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

def check_centering(df):
    print("\r")
    print("#################")
    print("### CENTERING ###")
    print("#################")

    df['Barycenter'] = df['Barycenter'].str.replace("nan", "0")
    df['Barycenter'] = df['Barycenter'].apply(eval).apply(np.array)

    df["Distance from origin"] = df["Barycenter"].apply(np.linalg.norm)
    df["Distance from origin"] = df["Distance from origin"].round(5)
    print(df["Distance from origin"])

    min_dist = df["Distance from origin"].min()
    mean_dist = df["Distance from origin"].mean()
    max_dist = df["Distance from origin"].max()

    print("Distance from origin -> min:", round(min_dist, 5), " | max:", round(max_dist, 5), " | mean:", round(mean_dist, 5))

    plt.figure(figsize=(18,6))
    plt.xlabel('Distance from origin')
    plt.ylabel('count')
    plt.hist(df["Distance from origin"], bins=25, rwidth = 0.9) # recommended 10-25 bins
    plt.show()

def check_scaling(df):
    print("\r")
    print("###############")
    print("### SCALING ###")
    print("###############")

    df['Bounding box'] = df['Bounding box'].str.replace("nan", "0")
    df['Bounding box'] = df['Bounding box'].apply(eval).apply(np.array)
    df['Max bound'] = df['Bounding box'].apply(lambda x: max(np.abs(x[0] - x[1])))

    min_bound = df['Max bound'].min()
    mean_bound = df['Max bound'].mean()
    max_bound = df['Max bound'].max()

    print("Max border box bound -> min:", round(min_bound, 5), " | max:", round(max_bound, 5), " | mean:", round(mean_bound, 5))

    plt.figure(figsize=(18,6))
    plt.xlabel('Max bound')
    plt.ylabel('count')
    plt.hist(df["Max bound"], bins=25, rwidth = 0.9) # recommended 10-25 bins
    plt.show()

    