import numpy as np
import walkE_math
import dictkeys

#################################################################################################

def calibrate_flex(joint_data, first, sec, third):
    flex_data = {item: [] for item in dictkeys.flex_list}
    
    for data_point in range(len(joint_data[first])):
        flex_list, time_list = [], []
        
        first_pt = joint_data[first][data_point]
        sec_pt = joint_data[sec][data_point]
        third_pt = joint_data[third][data_point]

        flex_list.append(180 - walkE_math.cal_threeD_angle(first_pt, sec_pt, third_pt))
        time_list.append(joint_data["time"][data_point])

        flex_data["flex_data"].append(flex_list)
        flex_data["time"].append(time_list)

    return flex_data

def calibrate_plane(joint_data, first, sec):
    angle_data = {item: [] for item in dictkeys.angle_list}

    for data_point in range(len(joint_data[first])):
        flex_list, time_list = [], []
        
        first_pt = joint_data[first][data_point]
        sec_pt = joint_data[sec][data_point]

        flex_list.append(walkE_math.cal_twopt_angle(first_pt, sec_pt))
        time_list.append(joint_data["time"][data_point])

        angle_data["angle_data"].append(flex_list)
        angle_data["time"].append(time_list)

    return angle_data

def calibrate(calibrate_data):        
    ref_list = []
    for elem in calibrate_data["ref_heel"]:
        ref_list.append(elem["y"])

    heelY_list = [data_point["y"] for data_point in calibrate_data["ref_heel"]]
    
    hipflex_data = calibrate_flex(calibrate_data, "left_shoulder", "left_hip", "knee")
    kneeflex_data = calibrate_flex(calibrate_data, "left_hip", "knee", "ankle")
    ankleflex_data = calibrate_flex(calibrate_data, "knee", "ankle", "toe")

    shoulder_data = calibrate_plane(calibrate_data, "left_shoulder", "right_shoulder")
    hip_data = calibrate_plane(calibrate_data, "left_hip", "right_hip")

    offset_json = {
        "cut_off": np.mean(heelY_list),
        "shoulder": np.mean(shoulder_data["angle_data"]),
        "hip": np.mean(hip_data["angle_data"]),
        "hipflex": np.mean(hipflex_data["flex_data"]),
        "kneeflex": np.mean(kneeflex_data["flex_data"]),
        "ankleflex": np.mean(ankleflex_data["flex_data"])
    }

    print("Calibration Complete")

    return offset_json

#################################################################################################

#  .\venv\Scripts\python.exe -m pylint .\Walk-E\gaitAnalysis.py