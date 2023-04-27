import numpy as np
import mediapipe as mp
import cam_math
import cam_dict
import time 

REF_POINT = cam_dict.ref_pt
MIN_CHUNKSIZE = 3
POINTS_SPACE = 20

HIPFLEX_COEFF = 1
KNEEFLEX_COEFF = 1
ANKLEFLEX_COEFF = 1

mp_pose = mp.solutions.pose  # Pose Estimation Model

#################################################################################################

def calibrate_flex(joint_data, joint_list):   
    flex_data = []
    
    for data_point in range(len(joint_data[joint_list[0]])):
        coords = [joint_data[joint][data_point] for joint in joint_list]
        flex_data.append(180 - cam_math.cal_twoD_angle(*coords))

    return flex_data

def calibrate(calibrate_data):        
    offset_json = {
        "cut_off": np.mean([data_point["x"] for data_point in calibrate_data[REF_POINT]]),
        "hipflex": np.mean(calibrate_flex(calibrate_data, cam_dict.hipflex_joints)) - 10,
        "kneeflex": np.mean(calibrate_flex(calibrate_data, cam_dict.kneeflex_joints)) - 20,
        "ankleflex": np.mean(calibrate_flex(calibrate_data, cam_dict.ankleflex_joints)) - 20
    }

    print("Calibration Complete")

    return offset_json

#################################################################################################

# Functions for processing gait cycles
    
def add_points(joint_data, unit_space):
    new_jointdata = {item: [] for item in cam_dict.gaitkeys_list}

    # For each component of joint_data
    for bodykey in joint_data:
        if bodykey == "time":
            for index in range(len(joint_data[REF_POINT])-1):
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
        
    return new_jointdata

def get_lm(json, world_lm, start_time):
    def format_lm(bodypart, world_landmarks):
        body_part = mp_pose.PoseLandmark[bodypart].value

        data_json = {
            "x": world_landmarks[body_part].x,
            "y": world_landmarks[body_part].y,
            "z": world_landmarks[body_part].z
        }

        return data_json
    
    # Extract landmarks
    for item in cam_dict.gaitkeys_list:
        if item == "time":
            json["time"].append(time.time() - start_time)  # Time Info
        else:
            json[item].append(format_lm(cam_dict.mp_pose_dict[item], world_lm))

def get_gait(heel_baseline, raw_joint):
    format_jointdata = add_points(raw_joint, POINTS_SPACE)

    # Identify cutoff points in data
    cutoff_index = [index for index, elem in enumerate(format_jointdata[REF_POINT]) 
                    if round(elem["x"], 2) == -0.13]
    
    ##############################################################################################

    # Slice data points based on identified cutoff points
    
    sine_joint = {}

    for item in cam_dict.gaitkeys_list:
        sine_joint[item] = [format_jointdata[item][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)]

        sine_joint[item].append(format_jointdata[item][cutoff_index[-1]:]) if cutoff_index else None

        # Remove data points that are too short in length0
        sine_joint[item] = [data for data in sine_joint[item] if len(data) > MIN_CHUNKSIZE]

    ##############################################################################################

    # Retrieve complete waveforms and remove wavelengths that are too long
    gait_joint = {item: [] for item in cam_dict.gaitkeys_list}

    ref_first = [sine_joint[REF_POINT][0][data_index]["x"]
                        for data_index in range(len(sine_joint[REF_POINT][0]))]
    
    for wave in range(1 if max(ref_first) > heel_baseline else 0, len(sine_joint[REF_POINT]),2):
        try:
            ref_list_first = [sine_joint[REF_POINT][wave][data_index]["x"]
                        for data_index in range(len(sine_joint[REF_POINT][wave]))]
            ref_list_third = [sine_joint[REF_POINT][wave + 2][data_index]["x"]
                        for data_index in range(len(sine_joint[REF_POINT][wave + 2]))]
            
            max_first_index = ref_list_first.index(min(ref_list_first))
            max_third_index = ref_list_third.index(min(ref_list_third))

            for item in cam_dict.gaitkeys_list:
                gait_joint[item].append(sine_joint[item][wave][max_first_index:] + sine_joint[item][wave + 1] + sine_joint[item][wave + 2 ][:max_third_index])           
                        
        except IndexError:
            pass
    
    gait_joint["gait_cycle"] = [cam_math.normalize_gait(time) for time in gait_joint["time"]]

    return gait_joint  

#################################################################################################

# Functions for statistics processing 

def get_data(gait_data, waveform, joint_list):
    x, y = [], []

    for index in range(len(gait_data[joint_list[0]][waveform])):
        coords = [gait_data[joint][waveform][index] for joint in joint_list]

        if joint_list == ['left_shoulder', 'left_hip', 'left_knee']:
            if gait_data["left_knee"][waveform][index]["x"] > gait_data["left_hip"][waveform][index]["x"]: 
                x.append(gait_data["gait_cycle"][waveform][index])
                y.append(-(180 - cam_math.cal_twoD_angle(*coords)))
            else:
                x.append(gait_data["gait_cycle"][waveform][index])
                y.append(180 - cam_math.cal_twoD_angle(*coords))
        else:
            x.append(gait_data["gait_cycle"][waveform][index])
            y.append(180 - cam_math.cal_twoD_angle(*coords)) 

    return cam_math.poly_fit(x,y)

def gaitcycle_stats(gait_data, gaitcycle_num, offset):
    start_time = time.time()
    
    raw_stats = {}
    
    raw_stats["gaitCycle_list"] = {"x": [gait_data["time"][gaitcycle_num][index] 
                                        for index in range(len(gait_data["time"][gaitcycle_num]))], 
                                    "y": [gait_data[REF_POINT][gaitcycle_num][index]["x"]
                                        for index in range(len(gait_data[REF_POINT][gaitcycle_num]))]}

    #########################################################################################
            
    raw_stats["superGaitCycle_list"] = {"x": [gait_data["gait_cycle"][gaitcycle_num][index]
                                            for index in range(len(gait_data["gait_cycle"][gaitcycle_num]))],
                                        "y": [gait_data[REF_POINT][gaitcycle_num][index]["x"]
                                            for index in range(len(gait_data[REF_POINT][gaitcycle_num]))]}

    #########################################################################################

    hipflex_x, hipflex_y, raw_stats["hipflex_polylist"] = get_data(gait_data, gaitcycle_num, cam_dict.hipflex_joints)
    kneeflex_x, kneeflex_y, raw_stats["kneeflex_polylist"] = get_data(gait_data, gaitcycle_num, cam_dict.kneeflex_joints)
    ankleflex_x, ankleflex_y, raw_stats["ankleflex_polylist"] = get_data(gait_data, gaitcycle_num, cam_dict.ankleflex_joints)

    raw_stats["hipflex_list"] = {"x": hipflex_x, "y": list(np.array(hipflex_y)*HIPFLEX_COEFF - offset["hipflex"])}
    raw_stats["kneeflex_list"] = {"x": kneeflex_x, "y": list(np.array(kneeflex_y)*KNEEFLEX_COEFF - offset["kneeflex"])}
    raw_stats["ankleflex_list"] = {"x": ankleflex_x, "y": list(np.array(ankleflex_y)*ANKLEFLEX_COEFF - offset["ankleflex"])}
    
    #########################################################################################

    print("#", gaitcycle_num, "Gait Cycle Complete", time.time() - start_time)

    return raw_stats

##################################################################################################

def stats(raw_data, gait_data, offset):

    start_time = time.time()
    print("Starting Stats Calculation...")

    print("Initialization", time.time() - start_time)

    #############################################################################################
    
    stats_unprocess = [gaitcycle_stats(gait_data, wave, offset) for wave in range(len(gait_data[REF_POINT]))]

    #############################################################################################
    
    print("For Loop Complete", time.time() - start_time)

    stats = {
        "rawData": {"x": raw_data["time"], "y":[elem["x"] for elem in raw_data[REF_POINT]]},
        "rawGaitCycle": [gaitcycle["gaitCycle_list"] for gaitcycle in stats_unprocess],
        "superGaitCycle": [gaitcycle["superGaitCycle_list"] for gaitcycle in stats_unprocess], 
        "hipflex": [gaitcycle["hipflex_list"] for gaitcycle in stats_unprocess],
        "kneeflex": [gaitcycle["kneeflex_list"] for gaitcycle in stats_unprocess],
        "ankleflex": [gaitcycle["ankleflex_list"] for gaitcycle in stats_unprocess],
        "besthip": cam_math.average_fit([gaitcycle["hipflex_polylist"]*HIPFLEX_COEFF for gaitcycle in stats_unprocess], offset["hipflex"]),
        "bestknee": cam_math.average_fit([gaitcycle["kneeflex_polylist"]*KNEEFLEX_COEFF for gaitcycle in stats_unprocess], offset["kneeflex"]),
        "bestankle": cam_math.average_fit([gaitcycle["ankleflex_polylist"]*ANKLEFLEX_COEFF for gaitcycle in stats_unprocess], offset["ankleflex"]),
    }
    
    print("Stats Calculation Complete", time.time() - start_time,"\n")
    
    return stats

#################################################################################################

#  .\venv\Scripts\python.exe -m pylint .\Walk-E\gaitAnalysis.py