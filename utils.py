import numpy as np
import math

def normalize_vector(v: np.ndarray):
    return v / np.linalg.norm(v)

def compute_normal(triangle: np.ndarray):
    # Triangle consists of three vertices
    if len(triangle) != 3:
        raise ValueError("Something other than a triangle was passed")

    v1, v2, v3 = triangle

    normal = normalize_vector(np.cross(v2 - v1, v3 - v1))

    return normal

def angle_calculation(a,b):
    cos_a = np.dot(a, b) / (np.linalg.norm(a)*np.linalg.norm(b))
    r = math.degrees(math.acos( min(1,max(cos_a,-1)) ))
    return r