import json
import math
import sys
import os
import numpy as np

def load_file(input_file):
    with open(input_file) as data_file:
        pose_details = json.load(data_file)
    return pose_details


def jedi_match(json1, json2):
    pose_points1 = json1['people'][0]['pose_keypoints']
    pose_points2 = json2['people'][0]['pose_keypoints']
    pers_score = pose_match(pose_points1, pose_points2)
    return pers_score


def pose_match(model_points, input_points):
    """
    # // Result for COCO (18 body parts)
    # // POSE_COCO_BODY_PARTS {
    # //     {0,  "Nose"},
    # //     {1,  "Neck"},
    # //     {2,  "RShoulder"},
    # //     {3,  "RElbow"},
    # //     {4,  "RWrist"},
    # //     {5,  "LShoulder"},
    # //     {6,  "LElbow"},
    # //     {7,  "LWrist"},
    # //     {8,  "RHip"},
    # //     {9,  "RKnee"},
    # //     {10, "RAnkle"},
    # //     {11, "LHip"},
    # //     {12, "LKnee"},
    # //     {13, "LAnkle"},
    # //     {14, "REye"},
    # //     {15, "LEye"},
    # //     {16, "REar"},
    # //     {17, "LEar"},
    # //     {18, "Background"},
    # // }
    # // Important points: [0 - 13]
    Compares pose similarity between reference model and input image
    :param pose_points1: (x1, y1, c1 ...) array of reference image
    :param pose_points2: (x2, y2, c2 ...) array of input model
    :return: similarity score
    """
    num_points = int(min(len(model_points), len(input_points)) / 3)
    pose_points1 = feature_vector(model_points)
    print(pose_points1)
    pose_points2 = affine_transform(model_points, input_points)
    print(pose_points2)
    pt_distances = []
    pt_proximity = []
    imp_points = range(0, 18)

    dist = np.linalg.norm(pose_points1 - pose_points2)
    print("Distance: {}".format(dist))
    for i in imp_points:
        x1 = pose_points1[i][0]
        y1 = pose_points1[i][1]

        x2 = pose_points2[i][0]
        y2 = pose_points2[i][1]

        pt_distance = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
        pt_distances.append(pt_distance)
        pt_pct_closeness = max(100.0 - pt_distance, 40.0)
        pt_proximity.append(pt_pct_closeness)

    total_displacement = 0.0
    total_pct_proximity = 0.0
    total_conf_sum = 0.0

    for i in imp_points:
        total_displacement += pt_distances[i]
        total_pct_proximity += pt_proximity[i]

    return total_pct_proximity / len(imp_points)

def affine_transform(pose_points1, pose_points2):
    model_features = feature_vector(pose_points1)
    input_features = feature_vector(pose_points2)

    # In order to solve the augmented matrix (incl translation),
    # it's required all vectors are augmented with a "1" at the end
    # -> Pad the features with ones, so that our transformation can do translations too
    pad = lambda x: np.hstack([x, np.ones((x.shape[0], 1))])
    unpad = lambda x: x[:, :-1]

    # Pad to [[ x y 1] , [x y 1]]
    Y = pad(model_features)
    X = pad(input_features)

    # Solve the least squares problem X * A = Y
    # and find the affine transformation matrix A.
    A, res, rank, s = np.linalg.lstsq(X, Y, rcond=None)
    A[np.abs(A) < 1e-10] = 0  # set really small values to zero

    transform = lambda x: unpad(np.dot(pad(x), A))
    input_transform = transform(input_features)
    return input_transform

def feature_vector(pose_points):
    # input_features = [[x1,y2],[x2,y2],...]
    features = []
    for i in range(0,18):
        xi = pose_points[3 * i]
        yi = pose_points[3 * i + 1]
        ci = pose_points[3 * i + 2] # Ignored
        ithCoordinate = [xi, yi]
        features.append(ithCoordinate)
    return np.array(features)

def fetch_score(file1, file2):
    """
        Calculates average movement score between two consecutive dance image snapshots
    :param file1: Computed JSON file for dance image captured at time T1
    :param file2: Computed JSON file for dance image captured at time T2
    :return: An array containing: [average group score, total group score, number of people, array of individual scores]
    """
    pose_details1 = load_file(file1)
    pose_details2 = load_file(file2)
    return jedi_match(pose_details1, pose_details2)


def main(argv):
    file1 = os.path.expanduser('~') + '/dev/ddr/tmp/jedi12018-06-07T01_20_07.196285.json'
    file2 = os.path.expanduser('~') + '/dev/ddr/tmp/imag12018-06-07T11_49_06.275068.json'

    pose_match_result = fetch_score(file1, file2)

    print("Score: " + str(pose_match_result))

    return

if __name__ == '__main__':
    main(sys.argv[1:])

