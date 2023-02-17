import numpy as np
import time

import walkE_math
import walkE_dict

REF_POINT = walkE_dict.ref_pt

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

    raw_stats["hipflex_list"] = {"x": hipflex_x, "y": list(np.array(hipflex_y) - offset["hipflex"])}
    raw_stats["kneeflex_list"] = {"x": kneeflex_x, "y": list(np.array(kneeflex_y) - offset["kneeflex"])}
    raw_stats["ankleflex_list"] = {"x": ankleflex_x, "y": list(np.array(ankleflex_y) - offset["ankleflex"])}
    
    #########################################################################################

    shoulder_x, shoulder_y, raw_stats["shoulder_polylist"] = get_data(gait_data, gaitcycle_num, walkE_dict.shoulderplane_joints)
    hip_x, hip_y, raw_stats["pelvic_polylist"] = get_data(gait_data, gaitcycle_num, walkE_dict.hipplane_joints)

    raw_stats["shoulder_angle_list"] = {"x": shoulder_x, "y": list(np.array(shoulder_y) - offset["shoulder"])}
    raw_stats["hip_angle_list"] = {"x": hip_x, "y": list(np.array(hip_y) - offset["hip"])}

    # print(gaitcycle_num, "Gait Cycle Complete", time.time() - start_time)

    return raw_stats

################################################################################################## 
    
def stats(raw_data, gait_data, hardware_data, offset):

    start_time = time.time()
    print("Starting Stats Calculation...")

    print("Initialization", time.time() - start_time)

    ################################################################################################## 
    
    # async def process_stats():
    #     print("Starting Loop Cycle...")

    #     task_list = []

    #     for wave in range(len(gait_data[REF_POINT])):
    #         task_list.append(asyncio.ensure_future(gaitcycle_stats(gait_data, wave, offset)))

    #     await asyncio.gather(*task_list)

    #     return [task.result() for task in task_list]
    
    # stats_unprocessed = asyncio.run(process_stats())

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
        "bestshoulder": walkE_math.average_fit([gaitcycle["shoulder_polylist"] for gaitcycle in stats_unprocess], offset["shoulder"]),
        "bestpelvic": walkE_math.average_fit([gaitcycle["pelvic_polylist"] for gaitcycle in stats_unprocess], offset["hip"]),
        "besthip": walkE_math.average_fit([gaitcycle["hipflex_polylist"] for gaitcycle in stats_unprocess], offset["hipflex"]),
        "bestknee": walkE_math.average_fit([gaitcycle["kneeflex_polylist"] for gaitcycle in stats_unprocess], offset["kneeflex"]),
        "bestankle": walkE_math.average_fit([gaitcycle["ankleflex_polylist"] for gaitcycle in stats_unprocess], offset["ankleflex"]),
        "cadence": get_cadence(gait_data),
    }

    if hardware_data["dist"] == "-":
        stats["dist"] = hardware_data["dist"]
        stats["speed"] = hardware_data["speed"]
        stats["stride_len"] = "-"
    else:
        stats["dist"] == round(hardware_data["dist"],3)
        stats["speed"] = round(hardware_data["speed"],3),
        stats["stride_len"] = get_stridelen(gait_data, hardware_data["dist"])
    
    print("Stats Calculation Complete", time.time() - start_time,"\n")

    return stats

################################################################################################
#  .\venv\Scripts\python.exe -m pylint .\Walk-E\gaitAnalysis.py