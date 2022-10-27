import numpy as np
import cv2
import mediapipe as mp
import walkE_math
import walkE_plot
import time 

FONT_STYLE = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.5
LINE_THICK = 1
LINE_TYPE = cv2.LINE_AA

MIN_CHUNKSIZE = 3
MIN_STRIDETIME = 2
POINTS_SPACE = 20

WEBCAM_RES = [640, 480]

mp_pose = mp.solutions.pose  # Pose Estimation Model

def arraySortedOrNot(arr):
 
    # Calculating length
    n = len(arr)
 
    # Array has one or no element or the
    # rest are already checked and approved.
    if n == 1 or n == 0:
        return True
 
    # Recursion applied till last element
    return arr[0] <= arr[1] and arraySortedOrNot(arr[1:])

def get_lm(json, world_lm, start_time):
    def format_lm(bodypart, world_landmarks):
        body_part = mp_pose.PoseLandmark[bodypart].value

        data_json = {
            "x": world_landmarks[body_part].x,
            "y": world_landmarks[body_part].y,
            "z": world_landmarks[body_part].z
        }
        
        print(bodypart, ":", data_json["x"], ",",
                            data_json["y"], ",",
                            data_json["z"], "\n")

        return data_json
        
    # Extract landmarks
    json["ref_heel"].append(format_lm("LEFT_HEEL", world_lm))  # Heel Reference
    json["shoulder"].append(format_lm("LEFT_SHOULDER", world_lm))  # Shoulder Info
    json["hip"].append(format_lm("LEFT_HIP", world_lm))  # Hip Info
    json["knee"].append(format_lm("LEFT_KNEE", world_lm))  # Knee Info
    json["ankle"].append(format_lm("LEFT_ANKLE", world_lm))  # Ankle Info
    json["toe"].append(format_lm("LEFT_FOOT_INDEX", world_lm))  # Toe Info
    json["time"].append(time.time() - start_time)  # Time Info


def get_gait(heel_baseline, joint_data):
    cutoff_index, format_jointdata = [], joint_data

    # Identify cutoff points in data
    for elem in format_jointdata["ref_heel"]:
        if round(elem["y"], 2) == round(heel_baseline, 2):
            cutoff_index.append(format_jointdata["ref_heel"].index(elem))

    ##############################################################################################

    # Slice data points based on identified cutoff points
    modified_joint = {
        "ref_heel": [format_jointdata["ref_heel"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "shoulder": [format_jointdata["shoulder"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "hip": [format_jointdata["hip"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "knee": [format_jointdata["knee"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "ankle": [format_jointdata["ankle"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "toe": [format_jointdata["toe"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "time": [format_jointdata["time"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)]
    }

    try:
        modified_joint["ref_heel"].append(format_jointdata["ref_heel"][cutoff_index[-1]::])
        modified_joint["shoulder"].append(format_jointdata["ref_heel"][cutoff_index[-1]::])
        modified_joint["hip"].append(format_jointdata["ref_heel"][cutoff_index[-1]::])
        modified_joint["knee"].append(format_jointdata["ref_heel"][cutoff_index[-1]::])
        modified_joint["ankle"].append(format_jointdata["ref_heel"][cutoff_index[-1]::])
        modified_joint["toe"].append(format_jointdata["ref_heel"][cutoff_index[-1]::])
        modified_joint["time"].append(format_jointdata["time"][cutoff_index[-1]::])
    except:
        pass

    # Remove data points that are too short in length
    modified_joint = {
        "ref_heel": [data for data in modified_joint["ref_heel"] if len(data) > MIN_CHUNKSIZE],
        "shoulder": [data for data in modified_joint["shoulder"] if len(data) > MIN_CHUNKSIZE],
        "hip": [data for data in modified_joint["hip"] if len(data) > MIN_CHUNKSIZE],
        "knee": [data for data in modified_joint["knee"] if len(data) > MIN_CHUNKSIZE],
        "ankle": [data for data in modified_joint["ankle"] if len(data) > MIN_CHUNKSIZE],
        "toe": [data for data in modified_joint["toe"] if len(data) > MIN_CHUNKSIZE],
        "time": [data for data in modified_joint["time"] if len(data) > MIN_CHUNKSIZE]
    } 
            
    ##############################################################################################

    # Retrieve complete waveforms and remove wavelengths that are too long
    combined_joint = {
        "ref_heel": [],
        "shoulder": [],
        "hip": [],
        "knee": [],
        "ankle": [],
        "toe": [],
        "time": []
    }

    for wave in range(len(modified_joint["ref_heel"])):
        first_wave = [modified_joint["ref_heel"][wave][data_index]["y"]
                    for data_index in range(len(modified_joint["ref_heel"][wave]))]

        if max(first_wave) > heel_baseline:
            try:
                if (modified_joint["time"][wave+1][-1] - modified_joint["time"][wave][0]) < MIN_STRIDETIME:
                    combined_joint["ref_heel"].append(modified_joint["ref_heel"][wave] + modified_joint["ref_heel"][wave + 1])
                    combined_joint["shoulder"].append(modified_joint["shoulder"][wave] + modified_joint["shoulder"][wave + 1])
                    combined_joint["hip"].append(modified_joint["hip"][wave] + modified_joint["hip"][wave + 1])
                    combined_joint["knee"].append(modified_joint["knee"][wave] + modified_joint["knee"][wave + 1])
                    combined_joint["ankle"].append(modified_joint["ankle"][wave] + modified_joint["ankle"][wave + 1])
                    combined_joint["toe"].append(modified_joint["toe"][wave] + modified_joint["toe"][wave + 1])
                    combined_joint["time"].append(modified_joint["time"][wave] + modified_joint["time"][wave+1])
            except:
                pass
    
    ##############################################################################################

    # Identify waveforms based on Max Points and remove wavelengths that are too long
    gait_joint = {
        "ref_heel": [],
        "shoulder": [],
        "hip": [],
        "knee": [],
        "ankle": [],
        "time": [],
        "toe": [],
        "gait_cycle": []
    }

    for wave in range(len(combined_joint["ref_heel"])-1):
        ref_list_first = [combined_joint["ref_heel"][wave][data_index]["y"]
                        for data_index in range(len(combined_joint["ref_heel"][wave]))]
        ref_list_sec = [combined_joint["ref_heel"][wave + 1][data_index]["y"]
                        for data_index in range(len(combined_joint["ref_heel"][wave + 1]))]

        max_first_index = ref_list_first.index(max(ref_list_first))
        max_sec_index = ref_list_sec.index(max(ref_list_sec))

        gait_joint["ref_heel"].append(combined_joint["ref_heel"][wave][max_first_index::] + combined_joint["ref_heel"][wave+1][0:max_sec_index])       
        gait_joint["shoulder"].append(combined_joint["shoulder"][wave][max_first_index::] + combined_joint["shoulder"][wave+1][0:max_sec_index])
        gait_joint["hip"].append(combined_joint["hip"][wave][max_first_index::] + combined_joint["hip"][wave+1][0:max_sec_index])
        gait_joint["knee"].append(combined_joint["knee"][wave][max_first_index::] + combined_joint["knee"][wave+1][0:max_sec_index])
        gait_joint["ankle"].append(combined_joint["ankle"][wave][max_first_index::] + combined_joint["ankle"][wave+1][0:max_sec_index])
        gait_joint["toe"].append(combined_joint["toe"][wave][max_first_index::] + combined_joint["toe"][wave+1][0:max_sec_index])
        
        time_first = combined_joint["time"][wave][max_first_index::]
        time_sec = combined_joint["time"][wave+1][0:max_sec_index]

        if arraySortedOrNot(time_first + time_sec):
            print("Yes")
        else:
            print("No")
        
        gait_joint["time"].append(time_first + time_sec)

    for time in gait_joint["time"]:
        gait_joint["gait_cycle"].append(walkE_math.normalize_gait(time))
    
    ##############################################################################################
    
    walkE_plot.get_gait(joint_data, modified_joint, combined_joint, gait_joint)

    return gait_joint   

def get_flex(joint_data, first, sec, third):
    flex_data = {
        "flex_data": [],
        "gait_cycle": []
    }

    for wave in range(len(joint_data[first])):
        flex_list, gait_list = [], []

        for data in range(len(joint_data[first][wave])):
            first_pt = joint_data[first][wave][data]
            sec_pt = joint_data[sec][wave][data]
            third_pt = joint_data[third][wave][data]

            flex_list.append(180 - walkE_math.cal_threeD_angle(first_pt, sec_pt, third_pt))
            gait_list.append(joint_data["gait_cycle"][wave][data])

        flex_data["flex_data"].append(flex_list)
        flex_data["gait_cycle"].append(gait_list)

    return flex_data

def calibrate_flex(joint_data, first, sec, third):
    flex_data = {
        "flex_data": [],
        "time": []
    }

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

def polyfit_heel(joint_data, axis, dof):
    x, y = [], []

    for wave in range(len(joint_data["ref_heel"])):
        x += [joint_data["gait_cycle"][wave][index]
                     for index in range(len(joint_data["gait_cycle"][wave]))]
        y += [joint_data["ref_heel"][wave][index][axis]
                    for index in range(len(joint_data["ref_heel"][wave]))]

    curve = np.polyfit(x, y, dof)
    poly = np.poly1d(curve)

    x.sort()
    new_y = [poly(data) for data in x]

    return x, new_y, poly

def polyfit_flex(joint_data, dof):
    x, y = [], []

    for wave in range(len(joint_data["flex_data"])):
        x += [joint_data["gait_cycle"][wave][index]
                     for index in range(len(joint_data["gait_cycle"][wave]))]
        y += [joint_data["flex_data"][wave][index]
                     for index in range(len(joint_data["flex_data"][wave]))]
           
    curve = np.polyfit(x, y, dof)
    poly = np.poly1d(curve)

    x.sort()
    new_y = [poly(data) for data in x]
    
    return x, new_y, poly


def calibrate(calibrate_data):        
    ref_list = []
    for elem in calibrate_data["ref_heel"]:
        ref_list.append(elem["y"])

    heelX_list = [data_point["x"] for data_point in calibrate_data["ref_heel"]]
    heelY_list = [data_point["y"] for data_point in calibrate_data["ref_heel"]]
    heelZ_list = [data_point["z"] for data_point in calibrate_data["ref_heel"]]
    
    hipflex_data = calibrate_flex(calibrate_data, "shoulder", "hip", "knee")
    kneeflex_data = calibrate_flex(calibrate_data, "hip", "knee", "ankle")
    ankleflex_data = calibrate_flex(calibrate_data, "knee", "ref_heel", "toe")

    walkE_plot.calibrate(ref_list, heelX_list, heelY_list, heelZ_list, 
                        hipflex_data, kneeflex_data, ankleflex_data,
                        calibrate_data["time"])

    offset_json = {
        "cut_off": np.mean(heelY_list),
        "hipflex": np.mean(hipflex_data["flex_data"]),
        "kneeflex": np.mean(kneeflex_data["flex_data"]),
        "ankleflex": np.mean(ankleflex_data["flex_data"])
    }

    print("Complete")

    return offset_json




#  .\venv\Scripts\python.exe -m pylint .\Walk-E\gaitAnalysis.py