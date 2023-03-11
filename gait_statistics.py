import numpy as np
import time

import walkE_math
import walkE_dict

REF_POINT = walkE_dict.ref_pt

HIPFLEX_COEFF = 8/3
KNEEFLEX_COEFF = 5/2 * 1.5
ANKLEFLEX_COEFF = 1.5
SHOULDER_COEFF = 2
PELVIC_COEFF = 1

#################################################################################################

def get_heel(gait_data, waveform, axis):
    x, y = [], []

    x += [gait_data["gait_cycle"][waveform][index]
                for index in range(len(gait_data["gait_cycle"][waveform]))]
    y += [gait_data[REF_POINT][waveform][index][axis]
                for index in range(len(gait_data[REF_POINT][waveform]))]
    
    return walkE_math.poly_fit(x, y)

def get_data(gait_data, waveform, joint_list):
    x, y = [], []

    for index in range(len(gait_data[joint_list[0]][waveform])):
        coords = [gait_data[joint][waveform][index] for joint in joint_list]

        x.append(gait_data["gait_cycle"][waveform][index])
        
        if len(coords) == 3:
            y.append(180 - walkE_math.threePt_threeD_angle(*coords)) 
        else:
            y.append((walkE_math.cal_twopt_angle(*coords)))

    return walkE_math.poly_fit(x,y)

#################################################################################################

def get_cadence(gait_data):
    steps = len(gait_data["time"]) * 2
    time = (gait_data["time"][-1][-1])/60

    cadence = round((steps/time),3)
    return cadence

def get_stridelen(gait_data, dist):
    try:
        steps = len(gait_data["time"]) * 2
        stride_len = dist / steps
        return round(stride_len,3)
    except:
        return "-" 

#################################################################################################

def gaitcycle_stats(gait_data, gaitcycle_num, offset):   
    start_time = time.time()
    
    raw_stats = {}
    
    raw_stats["gaitCycle_list"] = {"x": [gait_data["time"][gaitcycle_num][index] 
                                for index in range(len(gait_data["time"][gaitcycle_num]))], 
                        "y": [gait_data[REF_POINT][gaitcycle_num][index]["y"]
                                for index in range(len(gait_data[REF_POINT][gaitcycle_num]))]}

    #########################################################################################
            
    raw_stats["superGaitCycle_list"] = {"x": [gait_data["gait_cycle"][gaitcycle_num][index]
                                    for index in range(len(gait_data["gait_cycle"][gaitcycle_num]))],
                                "y": [gait_data[REF_POINT][gaitcycle_num][index]["y"]
                                    for index in range(len(gait_data[REF_POINT][gaitcycle_num]))]}

    #########################################################################################

    hipflex_x, hipflex_y, raw_stats["hipflex_polylist"] = get_data(gait_data, gaitcycle_num, walkE_dict.hipflex_joints)
    kneeflex_x, kneeflex_y, raw_stats["kneeflex_polylist"]= get_data(gait_data, gaitcycle_num, walkE_dict.kneeflex_joints)
    ankleflex_x, ankleflex_y, raw_stats["ankleflex_polylist"] = get_data(gait_data, gaitcycle_num, walkE_dict.ankleflex_joints)

    raw_stats["hipflex_list"] = {"x": hipflex_x, "y": list(np.array(hipflex_y)*HIPFLEX_COEFF - offset["hipflex"])}
    raw_stats["kneeflex_list"] = {"x": kneeflex_x, "y": list(np.array(kneeflex_y)*KNEEFLEX_COEFF - offset["kneeflex"])}
    raw_stats["ankleflex_list"] = {"x": ankleflex_x, "y": list(np.array(ankleflex_y)*ANKLEFLEX_COEFF - offset["ankleflex"])}
    
    #########################################################################################

    shoulder_x, shoulder_y, raw_stats["shoulder_polylist"] = get_data(gait_data, gaitcycle_num, walkE_dict.shoulderplane_joints)
    hip_x, hip_y, raw_stats["pelvic_polylist"] = get_data(gait_data, gaitcycle_num, walkE_dict.hipplane_joints)

    raw_stats["shoulder_angle_list"] = {"x": shoulder_x, "y": list(np.array(shoulder_y)*SHOULDER_COEFF - offset["shoulder"])}
    raw_stats["hip_angle_list"] = {"x": hip_x, "y": list(np.array(hip_y)*PELVIC_COEFF - offset["hip"])}

    print("#", gaitcycle_num, "Gait Cycle Complete", time.time() - start_time)

    return raw_stats

################################################################################################## 
    
def stats(raw_data, gait_data, hardware_data, offset):

    start_time = time.time()
    print("Starting Stats Calculation...")

    print("Initialization", time.time() - start_time)

    #############################################################################################
    
    stats_unprocess = [gaitcycle_stats(gait_data, wave, offset) for wave in range(len(gait_data[REF_POINT]))]

    #############################################################################################
    
    print("For Loop Complete", time.time() - start_time)

    stats = {
        "rawData": {"x": raw_data["time"], "y":[elem["y"] for elem in raw_data[REF_POINT]]},
        "rawGaitCycle": [gaitcycle["gaitCycle_list"] for gaitcycle in stats_unprocess],
        "superGaitCycle": [gaitcycle["superGaitCycle_list"] for gaitcycle in stats_unprocess], 
        "shoulder": [gaitcycle["shoulder_angle_list"] for gaitcycle in stats_unprocess],
        "hip_obliq": [gaitcycle["hip_angle_list"] for gaitcycle in stats_unprocess],       
        "hipflex": [gaitcycle["hipflex_list"] for gaitcycle in stats_unprocess],
        "kneeflex": [gaitcycle["kneeflex_list"] for gaitcycle in stats_unprocess],
        "ankleflex": [gaitcycle["ankleflex_list"] for gaitcycle in stats_unprocess],
        "bestshoulder": walkE_math.average_fit([gaitcycle["shoulder_polylist"]*SHOULDER_COEFF for gaitcycle in stats_unprocess], offset["shoulder"]),
        "bestpelvic": walkE_math.average_fit([gaitcycle["pelvic_polylist"]*PELVIC_COEFF for gaitcycle in stats_unprocess], offset["hip"]),
        "besthip": walkE_math.average_fit([gaitcycle["hipflex_polylist"]*HIPFLEX_COEFF for gaitcycle in stats_unprocess], offset["hipflex"]),
        "bestknee": walkE_math.average_fit([gaitcycle["kneeflex_polylist"]*KNEEFLEX_COEFF for gaitcycle in stats_unprocess], offset["kneeflex"]),
        "bestankle": walkE_math.average_fit([gaitcycle["ankleflex_polylist"]*ANKLEFLEX_COEFF for gaitcycle in stats_unprocess], offset["ankleflex"]),
        "cadence": get_cadence(gait_data),
    }

    stats["dist"] = hardware_data["dist"] if hardware_data["dist"] == "-" else round(hardware_data["dist"], 3)
    stats["speed"] = hardware_data["speed"] if hardware_data["speed"] == "-" else round(hardware_data["speed"], 3)        
    stats["stride_len"] = "-" if hardware_data["speed"] == "-" else get_stridelen(gait_data, hardware_data["dist"])
    
    print("Stats Calculation Complete", time.time() - start_time,"\n")
    return stats

################################################################################################
#  .\venv\Scripts\python.exe -m pylint .\Walk-E\gaitAnalysis.py