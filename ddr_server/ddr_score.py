import json
import math
import sys
import os


def load_file(input_file):
    with open(input_file) as data_file:
        pose_details = json.load(data_file)
    return pose_details


def jedi_match(json1, json2):
    pose_points1 = json1['people'][0]['pose_keypoints']
    pose_points2 = json2['people'][0]['pose_keypoints']
    pers_score = pose_match(pose_points1, pose_points2)
    return pers_score


def pose_match(pose_points1, pose_points2):
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
    num_points = int(min(len(pose_points1), len(pose_points2)) / 3)
    pt_distances = []
    pt_proximity = []
    imp_points = range(0, 14) # Ignore REye, LEye, REar, LEar, Background
    for i in imp_points:
        x1 = pose_points1[3 * i]
        y1 = pose_points1[3 * i + 1]
        c1 = pose_points1[3 * i + 2]
        x2 = pose_points2[3 * i]
        y2 = pose_points2[3 * i + 1]
        c2 = pose_points2[3 * i + 2]
        pt_distance = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
        pt_distances.append(pt_distance)
        pt_pct_closeness = max(100.0 - pt_distance, 20.0)
        pt_proximity.append(pt_pct_closeness)

    total_displacement = 0.0
    total_pct_proximity = 0.0
    total_conf_sum = 0.0

    for i in imp_points:
        total_displacement += pt_distances[i]
        total_pct_proximity += pt_proximity[i]

    return total_pct_proximity / len(imp_points)


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

    print(pose_match_result)

    return

if __name__ == '__main__':
    main(sys.argv[1:])

