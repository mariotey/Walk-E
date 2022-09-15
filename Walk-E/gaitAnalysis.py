import numpy as np
import cv2
import mediapipe as mp
import walkE_math
import walkE_plot

FONT_STYLE = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.5
LINE_THICK = 1
LINE_TYPE = cv2.LINE_AA

MIN_CHUNKSIZE = 3
MIN_STRIDETIME = 3
POINTS_SPACE = 20

WEBCAM_RES = [640, 480]

mp_pose = mp.solutions.pose  # Pose Estimation Model

def get_body_lm(bodypart, world_landmarks):
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

def modify_raw(joint_data, unit_space):
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

    print(len(new_jointdata["ref_heel"]), len(new_jointdata["shoulder"]), len(new_jointdata["hip"]), len(
        new_jointdata["knee"]), len(new_jointdata["ankle"]), len(new_jointdata["toe"]), len(new_jointdata["time"]))
        
    return new_jointdata

def get_gait(heel_baseline, joint_data):
    cutoff_index, format_jointdata = [], modify_raw(joint_data, POINTS_SPACE)

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
        return [], []

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
        ref_list = [modified_joint["ref_heel"][wave][data_index]["y"]
                    for data_index in range(len(modified_joint["ref_heel"][wave]))]

        if max(ref_list) > heel_baseline:
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

    for wave in range(len(combined_joint["ref_heel"])):
        try:
            ref_list_first = [combined_joint["ref_heel"][wave][data_index]["y"]
                              for data_index in range(len(combined_joint["ref_heel"][wave]))]
            ref_list_second = [combined_joint["ref_heel"][wave + 1][data_index]["y"]
                               for data_index in range(len(combined_joint["ref_heel"][wave + 1]))]

            max_first_index = ref_list_first.index(max(ref_list_first))
            max_second_index = ref_list_second.index(max(ref_list_second))

            gait_joint["ref_heel"].append(combined_joint["ref_heel"][wave][max_first_index::] + combined_joint["ref_heel"][wave+1][0:max_second_index])
            gait_joint["shoulder"].append(combined_joint["shoulder"][wave][max_first_index::] + combined_joint["shoulder"][wave+1][0:max_second_index])
            gait_joint["hip"].append(combined_joint["hip"][wave][max_first_index::] + combined_joint["hip"][wave+1][0:max_second_index])
            gait_joint["knee"].append(combined_joint["knee"][wave][max_first_index::] + combined_joint["knee"][wave+1][0:max_second_index])
            gait_joint["ankle"].append(combined_joint["ankle"][wave][max_first_index::] + combined_joint["ankle"][wave+1][0:max_second_index])
            gait_joint["toe"].append(combined_joint["toe"][wave][max_first_index::] + combined_joint["toe"][wave+1][0:max_second_index])
            gait_joint["time"].append(combined_joint["time"][wave][max_first_index::] + combined_joint["time"][wave+1][0:max_second_index])

        except:
            pass

    for time in gait_joint["time"]:
        gait_joint["gait_cycle"].append(walkE_math.normalize_gait(time))
    
    ##############################################################################################
    
    walkE_plot.modified_gait(modified_joint, combined_joint, gait_joint)

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

#  .\venv\Scripts\python.exe -m pylint .\Walk-E\gaitAnalysis.py