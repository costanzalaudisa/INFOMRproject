import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from scipy.spatial import distance
from scipy.stats import wasserstein_distance

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
    print("Single weight:", single_weight, "    |   histogram weight:", histogram_weight)

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

def query(obj):
    view_object = False

    if view_object:
        viewer = Viewer(obj)
        viewer.mainLoop()

    # Normalize features and gather model's feature_vector
    df = pd.read_csv("./psb_proc.csv")
    df = normalize(df)
    fv = df.loc[df['Model number'] == obj.model_num]
    feature_vector = np.array([fv['Surface'].iloc[0], fv['Compactness'].iloc[0], fv['Bounding box volume'].iloc[0], fv['Convex hull volume'].iloc[0], fv['Diameter'].iloc[0], fv['Eccentricity'].iloc[0], *fv['A3'].iloc[0], *fv['D1'].iloc[0], *fv['D2'].iloc[0], *fv['D3'].iloc[0], *fv['D4'].iloc[0]])

    # Calculate the distance of each object in the shapebase to the feature vector using a euclidean distance metric
    df["Euclidean Distance"] = df.apply(lambda x: distance.euclidean(x["Feature Vector"], feature_vector), axis=1)
    df["Cosine Distance"] = df.apply(lambda x: distance.cosine(x["Feature Vector"], feature_vector), axis=1)
    df["Earth Mover's Distance"] = df.apply(lambda x: wasserstein_distance(x["Feature Vector"], feature_vector), axis=1)

    # Take the smallest n distances and display their features
    print(df.nsmallest(5, "Euclidean Distance"))
    print(df.nsmallest(5, "Cosine Distance"))
    print(df.nsmallest(5, "Earth Mover's Distance"))

    k = 5
    ED_match_counts = []
    CD_match_counts = []
    EMD_match_counts = []

    ED_matches = []
    CD_matches = []
    EMD_matches = []

    for i, row in df.iterrows():
        vec = row["Feature Vector"]
        label = row["Label"]
        model_num = row["Model number"]

        df["Euclidean Distance"] = df.apply(lambda x: distance.euclidean(x["Feature Vector"], vec), axis=1)
        df["Cosine Distance"] = df.apply(lambda x: distance.cosine(x["Feature Vector"], vec), axis=1)
        df["Earth Mover's Distance"] = df.apply(lambda x: wasserstein_distance(x["Feature Vector"], vec), axis=1)

        ED_top_k = df.nsmallest(k + 1, "Euclidean Distance")
        CD_top_k = df.nsmallest(k + 1, "Cosine Distance")        
        EMD_top_k = df.nsmallest(k + 1, "Earth Mover's Distance")        

        ED_top_k = ED_top_k[ED_top_k["Model number"] != model_num]
        CD_top_k = CD_top_k[CD_top_k["Model number"] != model_num]
        EMD_top_k = EMD_top_k[EMD_top_k["Model number"] != model_num]

        ED_match_count = len(ED_top_k[ED_top_k["Label"] == label])
        CD_match_count = len(CD_top_k[CD_top_k["Label"] == label])
        EMD_match_count = len(EMD_top_k[EMD_top_k["Label"] == label])

        ED_match = max(set(ED_top_k["Label"]), key = list(ED_top_k["Label"]).count) == label
        CD_match = max(set(CD_top_k["Label"]), key = list(CD_top_k["Label"]).count) == label
        EMD_match = max(set(EMD_top_k["Label"]), key = list(EMD_top_k["Label"]).count) == label

        ED_matches.append(ED_match)
        CD_matches.append(CD_match)
        EMD_matches.append(EMD_match)

        ED_match_counts.append(ED_match_count)
        CD_match_counts.append(CD_match_count)
        EMD_match_counts.append(EMD_match_count)

    print("### EUCLIDEAN DISTANCE ###")
    print("Count: ", len(ED_match_counts))
    print("Max: ", max(ED_match_counts))
    print("Min: ", min(ED_match_counts))
    print("Avg: ", sum(ED_match_counts) / len(ED_match_counts))
    print("Correct matches: ", sum(ED_matches))
    print(f"Correct matches: {sum(ED_matches) / len(ED_match_counts) * 100: .2f}%")
    print("--------------------------------")

    print("### COSINE DISTANCE ###")
    print("Count: ", len(CD_match_counts))
    print("Max: ", max(CD_match_counts))
    print("Min: ", min(CD_match_counts))
    print("Avg: ", sum(CD_match_counts) / len(CD_match_counts))
    print("Correct matches: ", sum(CD_matches))
    print(f"Correct matches: {sum(CD_matches) / len(CD_match_counts) * 100: .2f}%")
    print("--------------------------------")

    print("### EARTH MOVER'S DISTANCE ###")
    print("Count: ", len(EMD_match_counts))
    print("Max: ", max(EMD_match_counts))
    print("Min: ", min(EMD_match_counts))
    print("Avg: ", sum(EMD_match_counts) / len(EMD_match_counts))
    print("Correct matches: ", sum(EMD_matches))
    print(f"Correct matches: {sum(EMD_matches) / len(EMD_match_counts) * 100: .2f}%")
    print("--------------------------------")