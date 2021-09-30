import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def plot_stats(db_path):
    # Gather database statistics
    df = pd.read_csv(db_path)
    stats = df[df.columns.difference(["Model Number"])].describe()
    print(stats)

    # Gather models with minimum and maximum values
    outliers = []

    min_vertices = df['Number of vertices'].min()
    max_vertices = df['Number of vertices'].max()
    min_faces = df['Number of faces'].min()
    max_faces = df['Number of faces'].max()

    print("Minimum and maximum number of vertices in the database:", min_vertices, ",", max_vertices)
    print("Minimum and maximum number of faces in the database:", min_faces, ",", max_faces)

    min_vertices_models = df.loc[df['Number of vertices'] == min_vertices]["Model number"]
    print("\n Models with minimum number of vertices:", end=' ')
    for model in min_vertices_models:
        print(model, end=' ')
        outliers.append(model)

    max_vertices_models = df.loc[df['Number of vertices'] == max_vertices]["Model number"]
    print("\n Models with maximum number of vertices:", end=' ')
    for model in max_vertices_models:
        print(model, end=' ')
        outliers.append(model)

    min_faces_models = df.loc[df['Number of faces'] == min_faces]["Model number"]
    print("\n Models with minimum number of faces:", end=' ')
    for model in min_faces_models:
        print(model, end=' ')
        outliers.append(model)

    max_faces_models = df.loc[df['Number of faces'] == max_faces]["Model number"]
    print("\n Modelss with maximum number of faces:", end=' ')
    for model in max_faces_models:
        print(model, end=' ')
        outliers.append(model)

    outliers = sorted(list(set(outliers)))
    print(outliers)

    # Plot histograms of number of vertices
    plt.figure(figsize=(12,10))
    plt.xlabel('Number of vertices')
    plt.ylabel('count')
    plt.hist(df["Number of vertices"], bins=25, rwidth = 0.9) # recommended 10-25 bins
    plt.show()

    # Plot histograms of number of faces
    plt.figure(figsize=(12,10))
    plt.xlabel('Number of faces')
    plt.ylabel('count')
    plt.hist(df["Number of faces"], bins=25, rwidth = 0.9) # recommended 10-25 bins
    plt.show()