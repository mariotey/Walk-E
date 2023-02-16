import numpy as np
import time
import asyncio

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
    # print(cadence, "steps/min")

    return cadence

def get_stridelen(gait_data, dist):
    try:
        steps = len(gait_data["time"]) * 2
        stride_len = dist / steps
    
        # print(stride_len, "m/step")

        return round(stride_len,3)
    except:
        return "-" 

#################################################################################################
def stats(raw_data, gait_data, hardware_data, offset):

    start_time = time.time()
    last_time = time.time()
    print("Starting Stats Calculation...")

    gaitCycle_list, superGaitCycle_list = [], []

    hipflex_list, kneeflex_list, ankleflex_list = [], [], []
    # besthip_list, bestknee_list, bestankle_list = { "x": [], "y": [] }, { "x": [], "y": [] }, { "x": [], "y": [] }
    hipflex_polylist, kneeflex_polylist, ankleflex_polylist = [], [], []

    shoulder_angle_list, hip_angle_list = [], []
    # bestshoulder_list, bestpelvic_list = { "x": [], "y": [] }, { "x": [], "y": [] }
    shoulder_polylist, pelvic_polylist = [], []

    print("Initialization", time.time() - last_time)
    last_time = time.time()

################################################################################################## 

    async def process_gaitcycle(gaitcycle_num):   
        gaitCycle_list.append({"x": [gait_data["time"][gaitcycle_num][index] 
                                    for index in range(len(gait_data["time"][gaitcycle_num]))], 
                            "y": [gait_data[REF_POINT][gaitcycle_num][index]["y"]
                                    for index in range(len(gait_data[REF_POINT][gaitcycle_num]))]})

        #########################################################################################
                
        superGaitCycle_list.append({"x": [gait_data["gait_cycle"][gaitcycle_num][index]
                                        for index in range(len(gait_data["gait_cycle"][gaitcycle_num]))],
                                    "y": [gait_data[REF_POINT][gaitcycle_num][index]["y"]
                                        for index in range(len(gait_data[REF_POINT][gaitcycle_num]))]})

        #########################################################################################

        print("Gait cycles complete")

        hipflex_x, hipflex_y, hipflex_poly = get_data(gait_data, gaitcycle_num, walkE_dict.hipflex_joints)
        kneeflex_x, kneeflex_y, kneeflex_poly= get_data(gait_data, gaitcycle_num, walkE_dict.kneeflex_joints)
        ankleflex_x, ankleflex_y, ankleflex_poly = get_data(gait_data, gaitcycle_num, walkE_dict.ankleflex_joints)

        hipflex_list.append({"x": hipflex_x, "y": list(np.array(hipflex_y) - offset["hipflex"])})
        kneeflex_list.append({"x": kneeflex_x, "y": list(np.array(kneeflex_y) - offset["kneeflex"])})
        ankleflex_list.append({"x": ankleflex_x, "y": list(np.array(ankleflex_y) - offset["ankleflex"])})
        
        hipflex_polylist.append(hipflex_poly)
        kneeflex_polylist.append(kneeflex_poly)
        ankleflex_polylist.append(ankleflex_poly)
        
        #########################################################################################

        shoulder_x, shoulder_y, shoulder_poly = get_data(gait_data, gaitcycle_num, walkE_dict.shoulderplane_joints)
        hip_x, hip_y, pelvic_poly = get_data(gait_data, gaitcycle_num, walkE_dict.hipplane_joints)

        shoulder_angle_list.append({"x": shoulder_x, "y": list(np.array(shoulder_y) - offset["shoulder"])})
        hip_angle_list.append({"x": hip_x, "y": list(np.array(hip_y) - offset["hip"])})

        shoulder_polylist.append(shoulder_poly)
        pelvic_polylist.append(pelvic_poly)

        print(gaitcycle_num, "Gait Cycle Complete", time.time() - last_time)

        #########################################################################################
    
    async def process_stats():
        print("Starting Loop Cycle...")

        task_list = []

        for wave in range(len(gait_data[REF_POINT])):
            task_list.append(asyncio.ensure_future(process_gaitcycle(wave)))

        await asyncio.gather(*task_list)
    
    asyncio.run(process_stats())

#################################################################################################

    # for wave in range(len(gait_data[REF_POINT])):
    #     ###############################q##########################################################
       
    #     gaitCycle_list.append({"x": [gait_data["time"][wave][index] 
    #                                 for index in range(len(gait_data["time"][wave]))], 
    #                         "y": [gait_data[REF_POINT][wave][index]["y"]
    #                                 for index in range(len(gait_data[REF_POINT][wave]))]})

    #     #########################################################################################
                
    #     superGaitCycle_list.append({"x": [gait_data["gait_cycle"][wave][index]
    #                                     for index in range(len(gait_data["gait_cycle"][wave]))],
    #                                 "y": [gait_data[REF_POINT][wave][index]["y"]
    #                                     for index in range(len(gait_data[REF_POINT][wave]))]})

    #     #########################################################################################

    #     hipflex_x, hipflex_y, hipflex_poly = get_data(gait_data, wave, walkE_dict.hipflex_joints)
    #     kneeflex_x, kneeflex_y, kneeflex_poly= get_data(gait_data, wave, walkE_dict.kneeflex_joints)
    #     ankleflex_x, ankleflex_y, ankleflex_poly = get_data(gait_data, wave, walkE_dict.ankleflex_joints)

    #     hipflex_list.append({"x": hipflex_x, "y": list(np.array(hipflex_y) - offset["hipflex"])})
    #     kneeflex_list.append({"x": kneeflex_x, "y": list(np.array(kneeflex_y) - offset["kneeflex"])})
    #     ankleflex_list.append({"x": ankleflex_x, "y": list(np.array(ankleflex_y) - offset["ankleflex"])})

    #     hipflex_polylist.append(hipflex_poly)
    #     kneeflex_polylist.append(kneeflex_poly)
    #     ankleflex_polylist.append(ankleflex_poly)

    #     #########################################################################################

    #     shoulder_x, shoulder_y, shoulder_poly = get_data(gait_data, wave, walkE_dict.shoulderplane_joints)
    #     hip_x, hip_y, pelvic_poly = get_data(gait_data, wave, walkE_dict.hipplane_joints)

    #     shoulder_angle_list.append({"x": shoulder_x, "y": list(np.array(shoulder_y) - offset["shoulder"])})
    #     hip_angle_list.append({"x": hip_x, "y": list(np.array(hip_y) - offset["hip"])})

    #     shoulder_polylist.append(shoulder_poly)
    #     pelvic_polylist.append(pelvic_poly)

    #     print(wave, "Gait Cycle Complete", time.time() - last_time)

#########################################################################################
    
    print("For Loop Complete", time.time() - last_time)
    last_time = time.time()

    stats = {
        "rawData": {"x": raw_data["time"], "y":[elem["y"] for elem in raw_data[REF_POINT]]},
        "rawGaitCycle": gaitCycle_list,
        "superGaitCycle": superGaitCycle_list, 
        "shoulder": shoulder_angle_list,
        "hip_obliq": hip_angle_list,       
        "hipflex": hipflex_list,
        "kneeflex": kneeflex_list,
        "ankleflex": ankleflex_list,
        "bestshoulder": walkE_math.average_fit(shoulder_polylist, offset["shoulder"]),
        "bestpelvic": walkE_math.average_fit(pelvic_polylist, offset["hip"]),
        "besthip": walkE_math.average_fit(hipflex_polylist, offset["hipflex"]),
        "bestknee": walkE_math.average_fit(kneeflex_polylist, offset["kneeflex"]),
        "bestankle": walkE_math.average_fit(ankleflex_polylist, offset["ankleflex"]),
        "cadence": get_cadence(gait_data),
        "dist": round(hardware_data["dist"],3),
        "speed": round(hardware_data["speed"],3),
        "stride_len": get_stridelen(gait_data, hardware_data["dist"])
    }
    
    print(time.time() - last_time)
    print("Stats Calculation Complete", time.time() - start_time,"\n")

    return stats

################################################################################################
#  .\venv\Scripts\python.exe -m pylint .\Walk-E\gaitAnalysis.py