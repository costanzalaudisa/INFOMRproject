import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.preprocessing import StandardScaler

from collections import defaultdict
from scipy.spatial import distance
from scipy.stats import wasserstein_distance

from annoy import AnnoyIndex

from object import Object
from viewer import Viewer

def normalize(df):
    # List string to numpy array
    for col in ["Bounding box", "Barycenter", "A3", "D1", "D2", "D3", "D4"]:
        df[col] = df[col].str.replace("nan", "0")
        df[col] = df[col].apply(eval).apply(np.array)

    # Drop models with NaNs and inf (better than replacing NaNs with 0 and inf with maximum value possible, as StandardScaler causes issues)
    df.replace(np.inf, np.nan, inplace=True)
    df.dropna(inplace=True)

    scaler = StandardScaler()

    # Standardize single-value features only
    for col in ["Surface", "Bounding box volume", "Convex hull volume", "Compactness", "Diameter", "Eccentricity"]:
        X = df[col].values
        X = scaler.fit_transform(X.reshape(-1, 1))
        df[col] = X

    # Weight features
    TOTAL_FEATURES = 11
    SINGLE_FEATURES = 6
    HISTOGRAM_FEATURES = 5
    GAP = 0.05 # 0.05
    single_weight = ((1/2)-GAP)/SINGLE_FEATURES
    histogram_weight = ((1/2)+GAP)/HISTOGRAM_FEATURES
    #print("Single weight:", single_weight, "    |   histogram weight:", histogram_weight)

    # Ensure sum of weights sums up to 1
    assert (single_weight*SINGLE_FEATURES)+(histogram_weight*HISTOGRAM_FEATURES) == 1.0

    # Apply weight to single-value features first (weight should be smaller than histogram features)
    for col in ["Surface", "Bounding box volume", "Convex hull volume", "Compactness", "Diameter", "Eccentricity"]:
        df[col] = df[col].apply(lambda x: x * single_weight)

    # Apply weight to single-value features first (weight should be smaller than histogram features)
    for col in ["A3", "D1", "D2", "D3", "D4"]:
        df[col] = df[col].apply(lambda x: x * histogram_weight)

    # Calculate the feature vector for every entry in the dataset
    df["Feature Vector"] = df.apply(lambda x: np.array([x["Surface"], x["Compactness"], x["Bounding box volume"], x["Convex hull volume"], x["Diameter"], x["Eccentricity"], *x["A3"], *x["D1"], *x["D2"], *x["D3"], *x["D4"]]), axis=1)

    return df

def build_ann(metric):
    # Gather processed dataset and normalize
    df = pd.read_csv("./psb_proc.csv")
    df = normalize(df)

    # Define constants for ANN
    K = 5
    K = K+1 # first model is always the query model, so must be +1
    N_TREES = 1000
    FEATURE_NUM = df['Feature Vector'].iloc[0].shape[0]
    SEED = 1
    METRIC = metric

    # Build ANN
    ann = AnnoyIndex(FEATURE_NUM, METRIC)
    ann.set_seed(SEED)

    # NOTE: ANN fills missing models with all zeros
    for model_num in df['Model number']:
        vec = df['Feature Vector'].loc[df['Model number'] == model_num].iloc[0]
        ann.add_item(model_num, vec)
    ann.build(N_TREES)

    return ann

 #print(ann.get_nns_by_item(MODEL_NUM, K, include_distances=True)) # will find the K nearest neighbors

def query(obj, dist, k):
    K = k
    view_object = True

    if view_object:
        viewer = Viewer(obj)
        viewer.mainLoop()

    print("### QUERY SHAPE: model #" + str(obj.model_num) + " - label: " + obj.label + " ###")
    print("\r")

    # Normalize features and gather model's feature_vector
    df = pd.read_csv("./psb_proc.csv")
    df = normalize(df)
    fv = df.loc[df['Model number'] == obj.model_num]
    feature_vector = np.array([fv['Surface'].iloc[0], fv['Compactness'].iloc[0], fv['Bounding box volume'].iloc[0], fv['Convex hull volume'].iloc[0], fv['Diameter'].iloc[0], fv['Eccentricity'].iloc[0], *fv['A3'].iloc[0], *fv['D1'].iloc[0], *fv['D2'].iloc[0], *fv['D3'].iloc[0], *fv['D4'].iloc[0]])

    # Calculate the distance of each object in the shapebase to the feature vector using a euclidean distance metric
    df["Euclidean Distance"] = df.apply(lambda x: distance.euclidean(x["Feature Vector"], feature_vector), axis=1)
    df["Cosine Distance"] = df.apply(lambda x: distance.cosine(x["Feature Vector"], feature_vector), axis=1)
    df["Earth Mover's Distance"] = df.apply(lambda x: wasserstein_distance(x["Feature Vector"], feature_vector), axis=1)

    # Build ANN
    a = build_ann("manhattan")
    ANN = a.get_nns_by_item(obj.model_num, K+1, include_distances=True)
    ANN_top_k = df[df['Model number'].isin(ANN[0])]
    ANN_top_k = ANN_top_k[ANN_top_k["Model number"] != obj.model_num]

    # Take the K nearest models and display their distance from query model (according to requested metric)
    if dist == 'ed':
        k_df = df.nsmallest(K+1, "Euclidean Distance")
        k_df = k_df[k_df["Model number"] != obj.model_num]
        model_nums = k_df["Model number"].values
        print("###", K, "nearest models using Euclidean Distance ###")
        for i, row in k_df.iterrows():
            print("Model #" + str(row["Model number"]) + " (label: " + row["Label"] + ") with distance: " + str(row["Euclidean Distance"]))
    elif dist == 'cd':
        k_df = df.nsmallest(K+1, "Cosine Distance")
        k_df = k_df[k_df["Model number"] != obj.model_num]
        model_nums = k_df["Model number"].values
        print("###", K, "nearest models using Cosine Distance ###")
        for i, row in k_df.iterrows():
            print("Model #" + str(row["Model number"]) + " (label: " + row["Label"] + ") with distance: " + str(row["Cosine Distance"]))
    elif dist == 'emd':
        k_df = df.nsmallest(K+1, "Earth Mover's Distance")
        k_df = k_df[k_df["Model number"] != obj.model_num]
        model_nums = k_df["Model number"].values
        print("###", K, "nearest models using Earth Mover's Distance ###")
        for i, row in k_df.iterrows():
            print("Model #" + str(row["Model number"]) + " (label: " + row["Label"] + ") with distance: " + str(row["Earth Mover's Distance"]))
    elif dist == 'ann':
        query_index = ANN[0].index(obj.model_num)
        ANN[0].pop(query_index)
        ANN[1].pop(query_index)
        model_nums = ANN[0]
        print("###", K, "nearest models using ANN (metric: Manhattan) ###")
        for i in range(len(ANN[0])):
            label = ANN_top_k['Label'].loc[ANN_top_k['Model number'] == ANN[0][i]].iloc[0]
            print("Model #" + str(ANN[0][i]) + " (label: " + label + ") with distance: " + str(ANN[1][i]))

    # Visualize best matches
    objs = []

    for model_num in model_nums:
        obj = Object.load_mesh(list(Path("./processed-models").glob(f"**/m{model_num}.off"))[0])
        viewer = Viewer(obj)
        viewer.mainLoop()

def get_query_accuracy(db_path, k):
    print("Calculating accuracy for k=" + str(k) + "... (Warning: might take several minutes.)")

    # Gather processed dataset and normalize
    df = pd.read_csv(db_path)
    df = normalize(df)

    # Define K
    K = k

    # Calculate KNN's accuracy over different distance metrics
    metrics = ["angular", "euclidean", "manhattan", "hamming", "dot"]
    for metric in metrics:
        ann = build_ann(metric)

        ANN_match_counts = []
        ANN_matches = []

        ANN_label_matches = defaultdict(list)

        for model_num in df['Model number']:
            vec = df['Feature Vector'].loc[df['Model number'] == model_num].iloc[0]
            label = df['Label'].loc[df['Model number'] == model_num].iloc[0]
            model_num = df['Model number'].loc[df['Model number'] == model_num].iloc[0]

            ANN = ann.get_nns_by_item(model_num, K+1, include_distances=True)
            ANN_top_k = df[df['Model number'].isin(ANN[0])]
            ANN_top_k = ANN_top_k[ANN_top_k["Model number"] != model_num]
            ANN_match_count = len(ANN_top_k[ANN_top_k["Label"] == label])
            ANN_match = max(set(ANN_top_k["Label"]), key = list(ANN_top_k["Label"]).count) == label
            ANN_matches.append(ANN_match)
            ANN_match_counts.append(ANN_match_count)
            ANN_label_matches[label].append(ANN_match)

        print("### ANN ACCURACY, metric:", metric, "###")
        print("Count: ", len(ANN_match_counts))
        print("Max: ", max(ANN_match_counts))
        print("Min: ", min(ANN_match_counts))
        print("Avg: ", sum(ANN_match_counts) / len(ANN_match_counts))
        print("Correct matches: ", sum(ANN_matches))
        print(f"Correct matches: {sum(ANN_matches) / len(ANN_match_counts) * 100: .2f}%")
        
        # Print accuracy per label
        ANN_label_matches = {key:sum(v) / len(v) * 100 for (key, v) in ANN_label_matches.items()}
        ANN_label_matches = dict(sorted(ANN_label_matches.items(), key=lambda item: item[1], reverse=True))
        for key, v in ANN_label_matches.items():
            print(f"Label {key}: {v: .2f}%")
        print("--------------------------------")

    # Calculate accuracy of distance functions
    ED_match_counts = []
    CD_match_counts = []
    EMD_match_counts = []

    ED_matches = []
    CD_matches = []
    EMD_matches = []

    ED_label_matches = defaultdict(list)
    CD_label_matches = defaultdict(list)
    EMD_label_matches = defaultdict(list)

    for i, row in df.iterrows():
        vec = row["Feature Vector"]
        label = row["Label"]
        model_num = row["Model number"]

        # Calculate distances
        df["Euclidean Distance"] = df.apply(lambda x: distance.euclidean(x["Feature Vector"], vec), axis=1)
        df["Cosine Distance"] = df.apply(lambda x: distance.cosine(x["Feature Vector"], vec), axis=1)
        df["Earth Mover's Distance"] = df.apply(lambda x: wasserstein_distance(x["Feature Vector"], vec), axis=1)
        KNN = ann.get_nns_by_item(model_num, k+1, include_distances=True)

        # Pick k+1 nearest neighbor
        ED_top_k = df.nsmallest(K + 1, "Euclidean Distance")
        CD_top_k = df.nsmallest(K + 1, "Cosine Distance")
        EMD_top_k = df.nsmallest(K + 1, "Earth Mover's Distance")

        ED_top_k = ED_top_k[ED_top_k["Model number"] != model_num]
        CD_top_k = CD_top_k[CD_top_k["Model number"] != model_num]
        EMD_top_k = EMD_top_k[EMD_top_k["Model number"] != model_num]

        # Count how many k-nearest neighbors match the query model's label
        ED_match_count = len(ED_top_k[ED_top_k["Label"] == label])
        CD_match_count = len(CD_top_k[CD_top_k["Label"] == label])
        EMD_match_count = len(EMD_top_k[EMD_top_k["Label"] == label])

        # Return count of matches by label
        ED_match = max(set(ED_top_k["Label"]), key = list(ED_top_k["Label"]).count) == label
        CD_match = max(set(CD_top_k["Label"]), key = list(CD_top_k["Label"]).count) == label
        EMD_match = max(set(EMD_top_k["Label"]), key = list(EMD_top_k["Label"]).count) == label

        ED_matches.append(ED_match)
        CD_matches.append(CD_match)
        EMD_matches.append(EMD_match)

        ED_label_matches[label].append(ED_match)
        CD_label_matches[label].append(CD_match)
        EMD_label_matches[label].append(EMD_match)

        ED_match_counts.append(ED_match_count)
        CD_match_counts.append(CD_match_count)
        EMD_match_counts.append(EMD_match_count)

    print("### EUCLIDEAN DISTANCE'S ACCURACY ###")
    print("Count: ", len(ED_match_counts))
    print("Max: ", max(ED_match_counts))
    print("Min: ", min(ED_match_counts))
    print("Avg: ", sum(ED_match_counts) / len(ED_match_counts))
    print("Correct matches: ", sum(ED_matches))
    print(f"Correct matches: {sum(ED_matches) / len(ED_match_counts) * 100: .2f}%")
    ED_label_matches = {k:sum(v) / len(v) * 100 for (k, v) in ED_label_matches.items()}
    ED_label_matches = dict(sorted(ED_label_matches.items(), key=lambda item: item[1], reverse=True))
    for k, v in ED_label_matches.items():
        print(f"Label {k}: {v: .2f}%")
    print("--------------------------------")

    print("### COSINE DISTANCE'S ACCURACY ###")
    print("Count: ", len(CD_match_counts))
    print("Max: ", max(CD_match_counts))
    print("Min: ", min(CD_match_counts))
    print("Avg: ", sum(CD_match_counts) / len(CD_match_counts))
    print("Correct matches: ", sum(CD_matches))
    print(f"Correct matches: {sum(CD_matches) / len(CD_match_counts) * 100: .2f}%")
    CD_label_matches = {k:sum(v) / len(v) * 100 for (k, v) in CD_label_matches.items()}
    CD_label_matches = dict(sorted(CD_label_matches.items(), key=lambda item: item[1], reverse=True))
    for k, v in CD_label_matches.items():
        print(f"Label {k}: {v: .2f}%")
    print("--------------------------------")

    print("### EARTH MOVER'S DISTANCE'S ACCURACY ###")
    print("Count: ", len(EMD_match_counts))
    print("Max: ", max(EMD_match_counts))
    print("Min: ", min(EMD_match_counts))
    print("Avg: ", sum(EMD_match_counts) / len(EMD_match_counts))
    print("Correct matches: ", sum(EMD_matches))
    print(f"Correct matches: {sum(EMD_matches) / len(EMD_match_counts) * 100: .2f}%")
    EMD_label_matches = {k:sum(v) / len(v) * 100 for (k, v) in EMD_label_matches.items()}
    EMD_label_matches = dict(sorted(EMD_label_matches.items(), key=lambda item: item[1], reverse=True))
    for k, v in EMD_label_matches.items():
        print(f"Label {k}: {v: .2f}%")
    print("--------------------------------")


