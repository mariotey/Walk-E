import mediapipe as mp
import numpy as np
import time

import walkE_math
import walkE_dict

#################################################################################################

REF_POINT = walkE_dict.ref_pt
MIN_CHUNKSIZE = 3
POINTS_SPACE = 20

mp_pose = mp.solutions.pose

#################################################################################################

def add_points(joint_data, unit_space):
    new_jointdata = {item: [] for item in walkE_dict.gaitkeys_list}

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
                new_jointdata[bodykey].extend([{"x": x, "y": y, "z": z} 
                                               for x, y, z in zip(new_x, new_y, new_z)])             
    
    return new_jointdata

def get_lm(world_lm, time):
    new_data = {item: [] for item in walkE_dict.gaitkeys_list}
    
    for idx, images in enumerate(world_lm):
        if images is not None:
            for bodypart in new_data.keys():
                new_data[bodypart].append(images[mp_pose.PoseLandmark[walkE_dict.mp_pose_dict[bodypart]].value]) if bodypart != "time" else None
        
            new_data["time"].append(time[idx] - time[0])

    if new_data != {item: [] for item in walkE_dict.gaitkeys_list}:
        return new_data
    else:
        print("No video coords recorded")

def get_gait(heel_baseline, raw_joint):
    start_time = time.time()
    last_time = time.time()
    print("Starting Data Slicing...")
    
    format_jointdata = add_points(raw_joint, POINTS_SPACE)

    ##############################################################################################

    # Identify cutoff points in data

    print(heel_baseline)

    # cutoff_index = [index for index, elem in enumerate(format_jointdata[REF_POINT]) 
    #                 if round(elem["y"], 2) == round(heel_baseline, 2)]

    # Configuration
    cutoff_index = [index for index, elem in enumerate(format_jointdata[REF_POINT]) 
                    if round(elem["y"], 2) == round(heel_baseline - 0.1 , 2)]
    
     ##############################################################################################

    # Slice data points based on identified cutoff points
    
    sine_joint = {}

    for item in walkE_dict.gaitkeys_list:
        sine_joint[item] = [format_jointdata[item][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)]

        sine_joint[item].append(format_jointdata[item][cutoff_index[-1]:]) if cutoff_index else None

        # Remove data points that are too short in length
        sine_joint[item] = [data for data in sine_joint[item] if len(data) > MIN_CHUNKSIZE]

    print("Sine Joint", time.time() - last_time)
    last_time = time.time()

    ##############################################################################################

    # Retrieve complete waveforms and remove wavelengths that are too long
    gait_joint = {item: [] for item in walkE_dict.gaitkeys_list}

    ref_first = [sine_joint[REF_POINT][0][data_index]["y"]
                        for data_index in range(len(sine_joint[REF_POINT][0]))]
    
    for wave in range(1 if max(ref_first) <= heel_baseline else 0, len(sine_joint[REF_POINT]),2):
        try:
            ref_list_first = [sine_joint[REF_POINT][wave][data_index]["y"]
                        for data_index in range(len(sine_joint[REF_POINT][wave]))]
            ref_list_third = [sine_joint[REF_POINT][wave + 2][data_index]["y"]
                        for data_index in range(len(sine_joint[REF_POINT][wave + 2]))]
            
            max_first_index = ref_list_first.index(max(ref_list_first))
            max_third_index = ref_list_third.index(max(ref_list_third))

            for item in walkE_dict.gaitkeys_list:
                gait_joint[item].append(sine_joint[item][wave][max_first_index:] + sine_joint[item][wave + 1] + sine_joint[item][wave + 2 ][:max_third_index])           
                        
        except IndexError:
            pass
    
    gait_joint["gait_cycle"] = [walkE_math.normalize_gait(time) for time in gait_joint["time"]]
    
    ##############################################################################################

    print(str(time.time() - last_time))
    print("Data Slicing Complete", time.time() - start_time, "\n")

    return gait_joint   

