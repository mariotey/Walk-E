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

WEBCAM_RES = [640,480]

mp_pose = mp.solutions.pose # Pose Estimation Model

def get_bodypart_landmarks(bodypart, world_landmarks):
    body_part = mp_pose.PoseLandmark[bodypart].value

    body_world = [world_landmarks[body_part].x, world_landmarks[body_part].y, world_landmarks[body_part].z]

    print(bodypart,":", body_world, "\n")

    data_json = {
        "x": body_world[0], 
        "y": body_world[1], 
        "z": body_world[2]
    }

    return data_json

def modify_raw(joint_data, unit_space):
    new_joint_data = {
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
                new_time = np.linspace(joint_data[bodykey][index],
                                       joint_data[bodykey][index+1],
                                       num=unit_space)

                try:
                    new_time.append(joint_data[bodykey][-1])
                except:
                    pass

                for x in range(len(new_time)):
                    new_joint_data["time"].append(new_time[x])
        
        else:
            # For each data set of a component of joint_data 
            for index in range(len(joint_data[bodykey])-1):
                # Create a new list of x,y and z_coord
                new_x = np.linspace(joint_data[bodykey][index]["x"], 
                                    joint_data[bodykey][index+1]["x"], 
                                    num=unit_space)

                new_y = np.linspace(joint_data[bodykey][index]["y"], 
                                    joint_data[bodykey][index+1]["y"], 
                                    num=unit_space)

                new_z = np.linspace(joint_data[bodykey][index]["z"], 
                                    joint_data[bodykey][index+1]["z"], 
                                    num=unit_space)
                
                try:
                    new_x.append(joint_data[bodykey][-1]["x"])
                    new_y.append(joint_data[bodykey][-1]["y"])
                    new_z.append(joint_data[bodykey][-1]["z"])
                except:
                    pass

                # Append the new x,y and z_coord into new_join_data 
                for num in range(len(new_x)):
                    data = {
                        "x": new_x[num],
                        "y": new_y[num],
                        "z": new_z[num]
                    }
                    new_joint_data[bodykey].append(data)            

    print(len(new_joint_data["ref_heel"]),len(new_joint_data["shoulder"]),len(new_joint_data["hip"]),len(new_joint_data["knee"]),len(new_joint_data["ankle"]),len(new_joint_data["toe"]), len(new_joint_data["time"]))
    return new_joint_data

def get_raw_cycle(heel_baseline, joint_data):    
    cutoff_index = []
   
    # Add points between bodypart coordinates and time
    format_jointdata = modify_raw(joint_data, POINTS_SPACE)

    # Identify cutoff points in data    
    for elem in format_jointdata["ref_heel"]:
        if round(elem["y"],2) == round(heel_baseline,2):
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
        "time":[format_jointdata["time"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)]
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
        "time":[data for data in modified_jointdata["time"] if len(data) > MIN_CHUNKSIZE]
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
        "time":[]
    }

    for wave in range(len(filtered_jointdata["ref_heel"])):
        ref_list = [filtered_jointdata["ref_heel"][wave][data_index]["y"] for data_index in range(len(filtered_jointdata["ref_heel"][wave]))]
        
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

    return new_jointdata

def get_gait_cycle(raw_cycle):
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

    for wave in range(len(raw_cycle["ref_heel"])):
        try:
            ref_list_first = [raw_cycle["ref_heel"][wave][data_index]["y"] for data_index in range(len(raw_cycle["ref_heel"][wave]))]
            ref_list_second = [raw_cycle["ref_heel"][wave + 1][data_index]["y"] for data_index in range(len(raw_cycle["ref_heel"][wave + 1]))]

            max_first_index = ref_list_first.index(max(ref_list_first))
            max_second_index = ref_list_second.index(max(ref_list_second))

            gait_jointdata["ref_heel"].append(raw_cycle["ref_heel"][wave][max_first_index::] + raw_cycle["ref_heel"][wave+1][0:max_second_index])
            gait_jointdata["shoulder"].append(raw_cycle["shoulder"][wave][max_first_index::] + raw_cycle["shoulder"][wave+1][0:max_second_index])
            gait_jointdata["hip"].append(raw_cycle["hip"][wave][max_first_index::] + raw_cycle["hip"][wave+1][0:max_second_index])
            gait_jointdata["knee"].append(raw_cycle["knee"][wave][max_first_index::] + raw_cycle["knee"][wave+1][0:max_second_index])
            gait_jointdata["ankle"].append(raw_cycle["ankle"][wave][max_first_index::] + raw_cycle["ankle"][wave+1][0:max_second_index])
            gait_jointdata["toe"].append(raw_cycle["toe"][wave][max_first_index::] + raw_cycle["toe"][wave+1][0:max_second_index])
            gait_jointdata["time"].append(raw_cycle["time"][wave][max_first_index::] + raw_cycle["time"][wave+1][0:max_second_index])

        except:
            pass
    
    for time in gait_jointdata["time"]:
        gait_jointdata["gait_cycle"].append(walkE_math.normalize_gait(time))

    return gait_jointdata

def polyfit_flex_curve(joint_data, dof):
    x = []
    y = []

    for wave in range(len(joint_data["flex_data"])):
        flex_list = [joint_data["flex_data"][wave][data_index] for data_index in range(len(joint_data["flex_data"][wave]))]
        gait_list = [joint_data["gait_cycle"][wave][data_index] for data_index in range(len(joint_data["gait_cycle"][wave]))]

        x = x + gait_list
        y = y + flex_list

    curve = np.polyfit(x,y,dof)
    poly = np.poly1d(curve)

    new_x = [data for data in x]
    new_x.sort()
    
    new_y = [poly(data) for data in new_x]

    return new_x, new_y, poly

def polyfit_heel_curve(joint_data, axis, dof):
    x = []
    y = []

    for wave in range(len(joint_data["ref_heel"])):
        ref_list = [joint_data["ref_heel"][wave][data_index][axis] for data_index in range(len(joint_data["ref_heel"][wave]))]
        gait_list = [joint_data["gait_cycle"][wave][data_index] for data_index in range(len(joint_data["gait_cycle"][wave]))]

        x = x + gait_list
        y = y + ref_list

    curve = np.polyfit(x,y,dof)
    poly = np.poly1d(curve)

    new_x = [data for data in x]
    new_x.sort()
    
    new_y = [poly(data) for data in new_x]

    return new_x, new_y, poly

def get_flex_data(joint_data, first, sec, third):
    flex_data = {
        "flex_data": [],
        "gait_cycle": []
    }

    for wave in range(len(joint_data[first])):
        flex_list = []
        gait_list = []

        for data_point in range(len(joint_data[first][wave])):
            first_point = joint_data[first][wave][data_point]
            sec_point = joint_data[sec][wave][data_point]
            third_point = joint_data[third][wave][data_point]

            flex_list.append(180 - walkE_math.cal_threeD_angle(first_point, sec_point, third_point))
            gait_list.append(joint_data["gait_cycle"][wave][data_point])
        
        flex_data["flex_data"].append(flex_list)
        flex_data["gait_cycle"].append(gait_list)

    return flex_data

def get_hipFlex(joint_data):      
    hipflex_data = {
        "flex_data": [],
        "gait_cycle": []
    }

    for wave in range(len(joint_data["shoulder"])):
        hipflex_wave = []
        gait_list = []

        for data_point in range(len(joint_data["shoulder"][wave])):
            shoulder = joint_data["shoulder"][wave][data_point]
            hip = joint_data["hip"][wave][data_point]
            knee = joint_data["knee"][wave][data_point]

            hipflex_wave.append(180 - walkE_math.cal_threeD_angle(shoulder, hip, knee))
            gait_list.append(joint_data["gait_cycle"][wave][data_point])
        
        hipflex_data["flex_data"].append(hipflex_wave)
        hipflex_data["gait_cycle"].append(gait_list)

    return hipflex_data

def get_kneeFlex(joint_data):          
    kneeflex_data = {
        "flex_data": [],
        "gait_cycle": []
    }

    for wave in range(len(joint_data["hip"])):
        kneeflex_wave = []
        gait_list = []

        for data_point in range(len(joint_data["hip"][wave])):
            hip = joint_data["hip"][wave][data_point]
            knee = joint_data["knee"][wave][data_point]
            ankle = joint_data["ankle"][wave][data_point]

            kneeflex_wave.append(180 - walkE_math.cal_threeD_angle(hip, knee, ankle))
            gait_list.append(joint_data["gait_cycle"][wave][data_point])
        
        kneeflex_data["flex_data"].append(kneeflex_wave)
        kneeflex_data["gait_cycle"].append(gait_list)

    return kneeflex_data

# def ankleFlex(world_landmarks):
#     knee_world_right = [world_landmarks[knee_right].x, world_landmarks[knee_right].y, world_landmarks[knee_right].z]
#     knee_world_left = [world_landmarks[knee_left].x, world_landmarks[knee_left].y, world_landmarks[knee_left].z]
#     ankle_world_right = [world_landmarks[ankle_right].x, world_landmarks[ankle_right].y, world_landmarks[ankle_right].z]
#     ankle_world_left = [world_landmarks[ankle_left].x, world_landmarks[ankle_left].y, world_landmarks[ankle_left].z]
#     heel_world_right = [world_landmarks[heel_right].x, world_landmarks[heel_right].y, world_landmarks[heel_right].z]
#     heel_world_left = [world_landmarks[heel_left].x, world_landmarks[heel_left].y, world_landmarks[heel_left].z]

#     ankle_flex_right = 180 - vectorMath.cal_threeD_angle(knee_world_right, ankle_world_right, heel_world_right)
#     ankle_flex_left = 180 - vectorMath.cal_threeD_angle(knee_world_left, ankle_world_left, heel_world_left)
    
#     print("Ankle R:", ankle_flex_right, " ", "Ankle L:", ankle_flex_left, "\n")

#     return ankle_flex_right, ankle_flex_left
