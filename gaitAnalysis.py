import numpy as np
import cv2
import mediapipe as mp
import walkE_math
import time 
from sklearn.metrics import mean_squared_error as mse

FONT_STYLE = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.5
LINE_THICK = 1
LINE_TYPE = cv2.LINE_AA

MIN_CHUNKSIZE = 3
MIN_STRIDETIME = 2
POINTS_SPACE = 20

MAX_MSE = 100
MAX_ITR = 10
WINLEN_PER = 1

mp_pose = mp.solutions.pose  # Pose Estimation Model

#################################################################################################

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
    json["left_heel"].append(format_lm("LEFT_HEEL", world_lm))
    json["shoulder"].append(format_lm("LEFT_SHOULDER", world_lm))  # Shoulder Info
    json["hip"].append(format_lm("LEFT_HIP", world_lm))  # Hip Info
    json["knee"].append(format_lm("LEFT_KNEE", world_lm))  # Knee Info
    json["ankle"].append(format_lm("LEFT_ANKLE", world_lm))  # Ankle Info
    json["toe"].append(format_lm("LEFT_FOOT_INDEX", world_lm))  # Toe Info
    json["time"].append(time.time() - start_time)  # Time Info

#################################################################################################

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

    # walkE_plot.calibrate(ref_list, heelX_list, heelY_list, heelZ_list, 
    #                     hipflex_data, kneeflex_data, ankleflex_data,
    #                     calibrate_data["time"])

    offset_json = {
        "cut_off": np.mean(heelY_list),
        "hipflex": np.mean(hipflex_data["flex_data"]),
        "kneeflex": np.mean(kneeflex_data["flex_data"]),
        "ankleflex": np.mean(ankleflex_data["flex_data"])
    }

    print("Complete")

    return offset_json

#################################################################################################

def add_points(joint_data, unit_space):
    new_jointdata = {
        "ref_heel": [],
        "shoulder": [],
        "hip": [],
        "knee": [],
        "ankle": [],
        "toe": [],
        "time": []
    }

    # For each component of joint_data
    for bodykey in joint_data:
        if bodykey == "time":
            for index in range(len(joint_data["ref_heel"])-1):
                new_time = list(np.linspace(joint_data[bodykey][index],
                                       joint_data[bodykey][index+1],
                                       num=unit_space))

                new_jointdata["time"] += new_time
        else:
            # For each data set of a component of joint_data
            for index in range(len(joint_data[bodykey])-1):
                # Create a new list of x,y and z_coord
                new_x = list(np.linspace(joint_data[bodykey][index]["x"],
                                    joint_data[bodykey][index+1]["x"],
                                    num=unit_space))

                new_y = list(np.linspace(joint_data[bodykey][index]["y"],
                                    joint_data[bodykey][index+1]["y"],
                                    num=unit_space))

                new_z = list(np.linspace(joint_data[bodykey][index]["z"],
                                    joint_data[bodykey][index+1]["z"],
                                    num=unit_space))

                # Append the new x,y and z_coord into new_join_data              
                for index in range(len(new_x)):
                    new_jointdata[bodykey].append({"x": new_x[index],
                                                    "y": new_y[index],
                                                    "z": new_z[index]})

    # print(len(new_jointdata["ref_heel"]), len(new_jointdata["shoulder"]), len(new_jointdata["hip"]), len(
    #     new_jointdata["knee"]), len(new_jointdata["ankle"]), len(new_jointdata["toe"]), len(new_jointdata["time"]))
        
    return new_jointdata

def get_gait(heel_baseline, raw_joint):
    cutoff_index, format_jointdata = [], add_points(raw_joint, POINTS_SPACE)

    # Identify cutoff points in data
    for elem in format_jointdata["ref_heel"]:
        if round(elem["y"], 2) == round(heel_baseline, 2):
            cutoff_index.append(format_jointdata["ref_heel"].index(elem))

    ##############################################################################################

    # Slice data points based on identified cutoff points
    sine_joint = {
        "ref_heel": [format_jointdata["ref_heel"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "shoulder": [format_jointdata["shoulder"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "hip": [format_jointdata["hip"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "knee": [format_jointdata["knee"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "ankle": [format_jointdata["ankle"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "toe": [format_jointdata["toe"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "time": [format_jointdata["time"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)]
    }

    try:
        sine_joint["ref_heel"].append(format_jointdata["ref_heel"][cutoff_index[-1]:])
        sine_joint["shoulder"].append(format_jointdata["ref_heel"][cutoff_index[-1]:])
        sine_joint["hip"].append(format_jointdata["ref_heel"][cutoff_index[-1]:])
        sine_joint["knee"].append(format_jointdata["ref_heel"][cutoff_index[-1]:])
        sine_joint["ankle"].append(format_jointdata["ref_heel"][cutoff_index[-1]:])
        sine_joint["toe"].append(format_jointdata["ref_heel"][cutoff_index[-1]:])
        sine_joint["time"].append(format_jointdata["time"][cutoff_index[-1]:])
    except:
        pass

    # Remove data points that are too short in length
    sine_joint = {
        "ref_heel": [data for data in sine_joint["ref_heel"] if len(data) > MIN_CHUNKSIZE],
        "shoulder": [data for data in sine_joint["shoulder"] if len(data) > MIN_CHUNKSIZE],
        "hip": [data for data in sine_joint["hip"] if len(data) > MIN_CHUNKSIZE],
        "knee": [data for data in sine_joint["knee"] if len(data) > MIN_CHUNKSIZE],
        "ankle": [data for data in sine_joint["ankle"] if len(data) > MIN_CHUNKSIZE],
        "toe": [data for data in sine_joint["toe"] if len(data) > MIN_CHUNKSIZE],
        "time": [data for data in sine_joint["time"] if len(data) > MIN_CHUNKSIZE]
    } 
            
    ##############################################################################################

    # Retrieve complete waveforms and remove wavelengths that are too long
    gait_joint = {
        "ref_heel": [],
        "shoulder": [],
        "hip": [],
        "knee": [],
        "ankle": [],
        "toe": [],
        "time": [],
        "gait_cycle": []
    }
    
    ref_first = [sine_joint["ref_heel"][0][data_index]["y"]
                        for data_index in range(len(sine_joint["ref_heel"][0]))]
    
    if max(ref_first) <= heel_baseline:
        start_elem = 1
    else:
        start_elem = 0

    for wave in range(start_elem, len(sine_joint["ref_heel"]),2):
        try:
            ref_list_first = [sine_joint["ref_heel"][wave][data_index]["y"]
                        for data_index in range(len(sine_joint["ref_heel"][wave]))]
            ref_list_third = [sine_joint["ref_heel"][wave + 2][data_index]["y"]
                        for data_index in range(len(sine_joint["ref_heel"][wave + 2]))]
            
            max_first_index = ref_list_first.index(max(ref_list_first))
            max_third_index = ref_list_third.index(max(ref_list_third))

            gait_joint["ref_heel"].append(sine_joint["ref_heel"][wave][max_first_index:] + sine_joint["ref_heel"][wave + 1] + sine_joint["ref_heel"][wave + 2 ][:max_third_index])       
            gait_joint["shoulder"].append(sine_joint["shoulder"][wave][max_first_index:] + sine_joint["shoulder"][wave + 1] + sine_joint["shoulder"][wave + 2][:max_third_index])
            gait_joint["hip"].append(sine_joint["hip"][wave][max_first_index:] + sine_joint["hip"][wave + 1] + sine_joint["hip"][wave + 2][:max_third_index])
            gait_joint["knee"].append(sine_joint["knee"][wave][max_first_index:] + sine_joint["knee"][wave + 1] + sine_joint["knee"][wave + 2][:max_third_index])
            gait_joint["ankle"].append(sine_joint["ankle"][wave][max_first_index:] + sine_joint["ankle"][wave + 1] + sine_joint["ankle"][wave + 2][:max_third_index])
            gait_joint["toe"].append(sine_joint["toe"][wave][max_first_index:] + sine_joint["toe"][wave + 1] + sine_joint["toe"][wave + 2][:max_third_index])
            gait_joint["time"].append(sine_joint["time"][wave][max_first_index:] + sine_joint["time"][wave + 1] + sine_joint["time"][wave + 2][:max_third_index])
            
        except:
            pass

    for time in gait_joint["time"]:
        gait_joint["gait_cycle"].append(walkE_math.normalize_gait(time))

    return gait_joint   

#################################################################################################
def digi_filter(y):
    """
    Applies Savitzky-Golay filter
    """
    win_len = int(len(y) * WINLEN_PER)

    if win_len % 2 == 1:
        win_len = win_len
    else:
        win_len = win_len - 1

    dof, mean_square = 0, MAX_MSE

    for dof_itera in range(1, MAX_ITR):
        try:
            filtered_y = list(savgol_filter(y, win_len, dof_itera))
            
            msq = mse(y, filtered_y) 

            if msq < mean_square:
                mean_square = msq
                dof = dof_itera

        except:
            pass

    return list(savgol_filter(y, win_len, dof))

def poly_fit(x,y):
    
    mse_dof, mean_square =  0, MAX_MSE

    def poly_func(x,y,dof):
        curve = np.polyfit(x, y, dof)
        poly = np.poly1d(curve)

        new_x = x
        new_x.sort()

        return new_x, [poly(data) for data in new_x]

    for dof_itera in range(1, MAX_ITR):
        try:
            msq = mse(y, poly_func(x,y,dof_itera)[1]) 

            if msq < mean_square:
                mean_square = msq
                mse_dof = dof_itera

        except:
            pass
    
    return poly_func(x,y,mse_dof)

def get_heel(gait_data, waveform, axis):
    x, y = [], []

    x += [gait_data["gait_cycle"][waveform][index]
                for index in range(len(gait_data["gait_cycle"][waveform]))]
    y += [gait_data["ref_heel"][waveform][index][axis]
                for index in range(len(gait_data["ref_heel"][waveform]))]
   
    new_x, new_y = poly_fit(x, y)
    
    return new_x, new_y, y

def get_flex(gait_data, waveform, first, secnd, third):
    x, y = [], []

    for index in range(len(gait_data[first][waveform])):
        first_pt = gait_data[first][waveform][index]
        secnd_pt = gait_data[secnd][waveform][index]
        third_pt = gait_data[third][waveform][index]

        x.append(gait_data["gait_cycle"][waveform][index])
        y.append(180 - walkE_math.cal_threeD_angle(first_pt, secnd_pt, third_pt)) 
        
    new_x, new_y = poly_fit(x,y)

    return new_x, new_y, y

def best_fit(json, dof):
    x, y = json["x"], json["y"]
    
    curve = np.polyfit(x, y, dof)
    poly = np.poly1d(curve)

    x.sort()
    new_y = [poly(data) for data in x]
    
    return x, new_y

#################################################################################################

def stats(raw_data, gait_data, offset):

    gaitCycle_list, superGaitCycle_list = [], []
    
    heelX_list, heelY_list, heelZ_list = [], [], []
    oldHeelX_list, oldHeelY_list, oldHeelZ_list = [], [], []
    
    hipflex_list, kneeflex_list, ankleflex_list = [], [], []
    oldHipFlex_list, oldKneeFlex_list, oldAnkleFlex_list = [], [], []

    for wave in range(len(gait_data["ref_heel"])):
        ###############################q##########################################################
       
        gaitCycle_list.append({"x": [gait_data["time"][wave][index] 
                                    for index in range(len(gait_data["time"][wave]))], 
                            "y": [gait_data["ref_heel"][wave][index]["y"]
                                    for index in range(len(gait_data["ref_heel"][wave]))]})

        #########################################################################################
                
        superGaitCycle_list.append({"x": [gait_data["gait_cycle"][wave][index]
                                        for index in range(len(gait_data["gait_cycle"][wave]))],
                                    "y": [gait_data["ref_heel"][wave][index]["y"]
                                        for index in range(len(gait_data["ref_heel"][wave]))]})

        #########################################################################################

        heelX_x, heelX_y, old_heelX_y = get_heel(gait_data, wave, "x")
        heelY_x, heelY_y, old_heelY_y = get_heel(gait_data, wave, "y")
        heelZ_x, heelZ_y, old_heelZ_y = get_heel(gait_data, wave, "z")

        heelX_list.append({"x": heelX_x, "y": heelX_y})
        heelY_list.append({"x": heelY_x, "y": heelY_y})
        heelZ_list.append({"x": heelZ_x, "y": heelZ_y})

        oldHeelX_list.append({"x": heelX_x, "y": old_heelX_y})
        oldHeelY_list.append({"x": heelY_x, "y": old_heelY_y})
        oldHeelZ_list.append({"x": heelZ_x, "y": old_heelZ_y})

        #########################################################################################

        hipflex_x, hipflex_y, old_hipflex_y = get_flex(gait_data, wave, "shoulder", "hip", "knee")
        kneeflex_x, kneeflex_y, old_kneeflex_y= get_flex(gait_data, wave, "hip", "knee", "ankle")
        ankleflex_x, ankleflex_y, old_ankleflex_y = get_flex(gait_data, wave, "knee", "ankle", "toe")

        hipflex_list.append({"x": hipflex_x, "y": list(np.array(hipflex_y) - offset["hipflex"])})
        kneeflex_list.append({"x": kneeflex_x, "y": list(np.array(kneeflex_y) - offset["kneeflex"])})
        ankleflex_list.append({"x": ankleflex_x, "y": list(np.array(ankleflex_y) - offset["ankleflex"])})

        oldHipFlex_list.append({"x": hipflex_x, "y": list(np.array(old_hipflex_y) - offset["hipflex"])})
        oldKneeFlex_list.append({"x": kneeflex_x, "y": list(np.array(old_kneeflex_y) - offset["kneeflex"])})
        oldAnkleFlex_list.append({"x": ankleflex_x, "y": list(np.array(old_ankleflex_y) - offset["ankleflex"])})
        
        #########################################################################################

    stats = {
        "rawGaitCycle": gaitCycle_list,
        "superGaitCycle": superGaitCycle_list,
        "heelX": heelX_list, 
        "heelY": heelY_list, 
        "heelZ": heelZ_list, 
        "hipflex": hipflex_list,
        "kneeflex": kneeflex_list,
        "ankleflex": ankleflex_list
    }

    raw = {
        "rawData": {"x": raw_data["time"], "y":[elem["y"] for elem in raw_data["ref_heel"]]},
        "heelX": oldHeelX_list,
        "heelY": oldHeelY_list,
        "heelZ": oldHeelZ_list,
        "hipflex": oldHipFlex_list,
        "kneeflex": oldKneeFlex_list,
        "ankleflex": oldAnkleFlex_list
    }

    return stats

#################################################################################################

#  .\venv\Scripts\python.exe -m pylint .\Walk-E\gaitAnalysis.py