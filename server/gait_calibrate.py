import numpy as np

import walkE_math
import walkE_dict

REF_POINT = walkE_dict.ref_pt

#################################################################################################

def calibrate_flex(joint_data, joint_list):   
    flex_data = []
    
    for data_point in range(len(joint_data[joint_list[0]])):
        coords = [joint_data[joint][data_point] for joint in joint_list]
        flex_data.append(180 - walkE_math.threePt_threeD_angle(*coords))

    return flex_data

def calibrate_plane(joint_data, joint_list):   
    angle_data = []

    for data_point in range(len(joint_data[joint_list[0]])):       
        coords = [joint_data[joint][data_point] for joint in joint_list]
        angle_data.append(walkE_math.cal_twopt_angle(*coords))

    return angle_data

def calibrate_hiplen(joint_data, joint_list):
    hiplen_data = []

    for data_point in range(len(joint_data[joint_list[0]])):       
        coords = [joint_data[joint][data_point] for joint in joint_list]
        hiplen_data.append(walkE_math.cal_twopt_angle(*coords))

    return hiplen_data

def calibrate(calibrate_data):        
    offset_json = {
        "cut_off": np.mean([data_point["y"] for data_point in calibrate_data[REF_POINT]]),
        "shoulder": np.mean(calibrate_plane(calibrate_data, walkE_dict.shoulderplane_joints)),
        "hip": np.mean(calibrate_plane(calibrate_data, walkE_dict.hipplane_joints)),
        "hipflex": np.mean(calibrate_flex(calibrate_data, walkE_dict.hipflex_joints)),
        "kneeflex": np.mean(calibrate_flex(calibrate_data, walkE_dict.kneeflex_joints)),
        "ankleflex": np.mean(calibrate_flex(calibrate_data, walkE_dict.ankleflex_joints))
    }

    print("Calibration Complete")

    return offset_json

#################################################################################################

#  .\venv\Scripts\python.exe -m pylint .\Walk-E\gaitAnalysis.py