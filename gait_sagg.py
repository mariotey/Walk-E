import numpy as np
import time

import gait_process
import walkE_math
import walkE_dict

REF_POINT = walkE_dict.ref_pt
MIN_CHUNKSIZE = 3
POINTS_SPACE = 20


def get_gait(heel_baseline, raw_joint):
    start_time = time.time()
    last_time = time.time()
    print("Starting Data Slicing...")
    
    format_jointdata = gait_process.add_points(raw_joint, POINTS_SPACE)

    # Identify cutoff points in data
    cutoff_index = [index for index, elem in enumerate(format_jointdata[REF_POINT]) 
                    if round(elem["y"], 2) == round(heel_baseline, 2)]

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

