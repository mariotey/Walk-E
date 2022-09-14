import numpy as np
import cv2
import mediapipe as mp
import walkE_math

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
    cutoff_index = []

    # Add points between bodypart coordinates and time
    format_jointdata = modify_raw(joint_data, POINTS_SPACE)

    # Identify cutoff points in data
    for elem in format_jointdata["ref_heel"]:
        if round(elem["y"], 2) == round(heel_baseline, 2):
            cutoff_index.append(format_jointdata["ref_heel"].index(elem))

    ##############################################################################################

    # Slice data points based on identified cutoff points
    modified_jointdata = {
        "ref_heel": [format_jointdata["ref_heel"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "shoulder": [format_jointdata["shoulder"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "hip": [format_jointdata["hip"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "knee": [format_jointdata["knee"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "ankle": [format_jointdata["ankle"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "toe": [format_jointdata["toe"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "time": [format_jointdata["time"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)]
    }

    try:
        modified_jointdata["ref_heel"].append(format_jointdata["ref_heel"][cutoff_index[-1]::])
        modified_jointdata["shoulder"].append(format_jointdata["ref_heel"][cutoff_index[-1]::])
        modified_jointdata["hip"].append(format_jointdata["ref_heel"][cutoff_index[-1]::])
        modified_jointdata["knee"].append(format_jointdata["ref_heel"][cutoff_index[-1]::])
        modified_jointdata["ankle"].append(format_jointdata["ref_heel"][cutoff_index[-1]::])
        modified_jointdata["toe"].append(format_jointdata["ref_heel"][cutoff_index[-1]::])
        modified_jointdata["time"].append(format_jointdata["time"][cutoff_index[-1]::])
    except:
        return [], []

    ##############################################################################################

    # Remove data points that are too short in length
    filtered_jointdata = {
        "ref_heel": [data for data in modified_jointdata["ref_heel"] if len(data) > MIN_CHUNKSIZE],
        "shoulder": [data for data in modified_jointdata["shoulder"] if len(data) > MIN_CHUNKSIZE],
        "hip": [data for data in modified_jointdata["hip"] if len(data) > MIN_CHUNKSIZE],
        "knee": [data for data in modified_jointdata["knee"] if len(data) > MIN_CHUNKSIZE],
        "ankle": [data for data in modified_jointdata["ankle"] if len(data) > MIN_CHUNKSIZE],
        "toe": [data for data in modified_jointdata["toe"] if len(data) > MIN_CHUNKSIZE],
        "time": [data for data in modified_jointdata["time"] if len(data) > MIN_CHUNKSIZE]
    }

    ##############################################################################################

    # Combine upper and lower parts of heel waveform and remove wavelengths that are too long
    new_jointdata = {
        "ref_heel": [],
        "shoulder": [],
        "hip": [],
        "knee": [],
        "ankle": [],
        "toe": [],
        "time": []
    }

    for wave in range(len(filtered_jointdata["ref_heel"])):
        ref_list = [filtered_jointdata["ref_heel"][wave][data_index]["y"]
                    for data_index in range(len(filtered_jointdata["ref_heel"][wave]))]

        if max(ref_list) > heel_baseline:
            try:
                if (filtered_jointdata["time"][wave+1][-1] - filtered_jointdata["time"][wave][0]) < MIN_STRIDETIME:
                    new_jointdata["ref_heel"].append(filtered_jointdata["ref_heel"][wave] + filtered_jointdata["ref_heel"][wave + 1])
                    new_jointdata["shoulder"].append(filtered_jointdata["shoulder"][wave] + filtered_jointdata["shoulder"][wave + 1])
                    new_jointdata["hip"].append(filtered_jointdata["hip"][wave] + filtered_jointdata["hip"][wave + 1])
                    new_jointdata["knee"].append(filtered_jointdata["knee"][wave] + filtered_jointdata["knee"][wave + 1])
                    new_jointdata["ankle"].append(filtered_jointdata["ankle"][wave] + filtered_jointdata["ankle"][wave + 1])
                    new_jointdata["toe"].append(filtered_jointdata["toe"][wave] + filtered_jointdata["toe"][wave + 1])
                    new_jointdata["time"].append(filtered_jointdata["time"][wave] + filtered_jointdata["time"][wave+1])
            except:
                new_jointdata["ref_heel"].append(filtered_jointdata["ref_heel"][wave])
                new_jointdata["shoulder"].append(filtered_jointdata["shoulder"][wave])
                new_jointdata["hip"].append(filtered_jointdata["hip"][wave])
                new_jointdata["knee"].append(filtered_jointdata["knee"][wave])
                new_jointdata["ankle"].append(filtered_jointdata["ankle"][wave])
                new_jointdata["toe"].append(filtered_jointdata["toe"][wave])
                new_jointdata["time"].append(filtered_jointdata["time"][wave])

    gait_jointdata = {
        "ref_heel": [],
        "shoulder": [],
        "hip": [],
        "knee": [],
        "ankle": [],
        "time": [],
        "toe": [],
        "gait_cycle": []
    }

    for wave in range(len(new_jointdata["ref_heel"])):
        try:
            ref_list_first = [new_jointdata["ref_heel"][wave][data_index]["y"]
                              for data_index in range(len(new_jointdata["ref_heel"][wave]))]
            ref_list_second = [new_jointdata["ref_heel"][wave + 1][data_index]["y"]
                               for data_index in range(len(new_jointdata["ref_heel"][wave + 1]))]

            max_first_index = ref_list_first.index(max(ref_list_first))
            max_second_index = ref_list_second.index(max(ref_list_second))

            gait_jointdata["ref_heel"].append(new_jointdata["ref_heel"][wave][max_first_index::] + new_jointdata["ref_heel"][wave+1][0:max_second_index])
            gait_jointdata["shoulder"].append(new_jointdata["shoulder"][wave][max_first_index::] + new_jointdata["shoulder"][wave+1][0:max_second_index])
            gait_jointdata["hip"].append(new_jointdata["hip"][wave][max_first_index::] + new_jointdata["hip"][wave+1][0:max_second_index])
            gait_jointdata["knee"].append(new_jointdata["knee"][wave][max_first_index::] + new_jointdata["knee"][wave+1][0:max_second_index])
            gait_jointdata["ankle"].append(new_jointdata["ankle"][wave][max_first_index::] + new_jointdata["ankle"][wave+1][0:max_second_index])
            gait_jointdata["toe"].append(new_jointdata["toe"][wave][max_first_index::] + new_jointdata["toe"][wave+1][0:max_second_index])
            gait_jointdata["time"].append(new_jointdata["time"][wave][max_first_index::] + new_jointdata["time"][wave+1][0:max_second_index])

        except:
            pass

    for time in gait_jointdata["time"]:
        gait_jointdata["gait_cycle"].append(walkE_math.normalize_gait(time))

    return gait_jointdata   

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
