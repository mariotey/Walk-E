import numpy as np
import walkE_math
import dictkeys
import modify_data

#################################################################################################

MIN_CHUNKSIZE = 3
POINTS_SPACE = 20

#################################################################################################

def get_gait(heel_baseline, raw_joint):
    cutoff_index, format_jointdata = [], modify_data.add_points(raw_joint, POINTS_SPACE)

    # Identify cutoff points in data
    for elem in format_jointdata["ref_heel"]:
        if round(elem["y"], 2) == round(heel_baseline, 2):
            cutoff_index.append(format_jointdata["ref_heel"].index(elem))

    ##############################################################################################

    # Slice data points based on identified cutoff points
    sine_joint = {}

    for item in dictkeys.gait_list:
        sine_joint[item] = [format_jointdata[item][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)]

        try:
            sine_joint[item].append(format_jointdata[item][cutoff_index[-1]:])
        except:
            pass

        # Remove data points that are too short in length
        sine_joint[item] = [data for data in sine_joint[item] if len(data) > MIN_CHUNKSIZE]

    ##############################################################################################

    # Retrieve complete waveforms and remove wavelengths that are too long
    gait_joint = {item: [] for item in dictkeys.gait_list}
    gait_joint["gait_cycle"] = []

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

            for item in dictkeys.gait_list:
                gait_joint[item].append(sine_joint[item][wave][max_first_index:] + sine_joint[item][wave + 1] + sine_joint[item][wave + 2 ][:max_third_index])           
                        
        except:
            pass
    
    for time in gait_joint["time"]:
        gait_joint["gait_cycle"].append(walkE_math.normalize_gait(time))
    
    ##############################################################################################

    print("Data Slicing Complete")

    return gait_joint   

#################################################################################################

def get_heel(gait_data, waveform, axis):
    x, y = [], []

    x += [gait_data["gait_cycle"][waveform][index]
                for index in range(len(gait_data["gait_cycle"][waveform]))]
    y += [gait_data["ref_heel"][waveform][index][axis]
                for index in range(len(gait_data["ref_heel"][waveform]))]
    
    return walkE_math.poly_fit(x, y)

def get_flex(gait_data, waveform, first, secnd, third):
    x, y = [], []

    for index in range(len(gait_data[first][waveform])):
        first_pt = gait_data[first][waveform][index]
        secnd_pt = gait_data[secnd][waveform][index]
        third_pt = gait_data[third][waveform][index]

        x.append(gait_data["gait_cycle"][waveform][index])
        y.append(180 - walkE_math.cal_threeD_angle(first_pt, secnd_pt, third_pt)) 

    return walkE_math.poly_fit(x,y)

def get_angle(gait_data, waveform, first, secnd):
    x, y = [], []

    for index in range(len(gait_data[first][waveform])):
        first_pt = gait_data[first][waveform][index]
        secnd_pt = gait_data[secnd][waveform][index]

        x.append(gait_data["gait_cycle"][waveform][index])
        y.append((walkE_math.cal_twopt_angle(first_pt, secnd_pt)))
        
    return walkE_math.poly_fit(x,y)

#################################################################################################

def get_cadence(gait_data):
    steps = len(gait_data["time"]) * 2
    time = (gait_data["time"][-1][-1])/60

    cadence = round((steps/time),3)

    # print(cadence, "steps/min")

    return cadence

#################################################################################################

def stats(raw_data, gait_data, offset):

    gaitCycle_list, superGaitCycle_list = [], []
    
    heelX_list, heelY_list, heelZ_list = [], [], []

    hipflex_list, kneeflex_list, ankleflex_list = [], [], []
    besthip_list, bestknee_list, bestankle_list = { "x": [], "y": [] }, { "x": [], "y": [] }, { "x": [], "y": [] }

    shoulder_angle_list, hip_angle_list = [], []
    bestshoulder_list, bestpelvic_list = { "x": [], "y": [] }, { "x": [], "y": [] }

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

        heelX_x, heelX_y, heelX_dof = get_heel(gait_data, wave, "x")
        heelY_x, heelY_y, heelY_dof = get_heel(gait_data, wave, "y")
        heelZ_x, heelZ_y, heelZ_dof = get_heel(gait_data, wave, "z")

        heelX_list.append({"x": heelX_x, "y": heelX_y})
        heelY_list.append({"x": heelY_x, "y": heelY_y})
        heelZ_list.append({"x": heelZ_x, "y": heelZ_y})

        #########################################################################################

        hipflex_x, hipflex_y, hipflex_dof = get_flex(gait_data, wave, "left_shoulder", "left_hip", "knee")
        kneeflex_x, kneeflex_y, kneeflex_dof= get_flex(gait_data, wave, "left_hip", "knee", "ankle")
        ankleflex_x, ankleflex_y, ankleflex_dof = get_flex(gait_data, wave, "knee", "ankle", "toe")

        hipflex_list.append({"x": hipflex_x, "y": list(np.array(hipflex_y) - offset["hipflex"])})
        kneeflex_list.append({"x": kneeflex_x, "y": list(np.array(kneeflex_y) - offset["kneeflex"])})
        ankleflex_list.append({"x": ankleflex_x, "y": list(np.array(ankleflex_y) - offset["ankleflex"])})

        besthip_list["x"] += hipflex_x
        besthip_list["y"] += list(np.array(hipflex_y) - offset["hipflex"])
        bestknee_list["x"] += kneeflex_x
        bestknee_list["y"] += list(np.array(kneeflex_y) - offset["kneeflex"])
        bestankle_list["x"] += ankleflex_x
        bestankle_list["y"] += list(np.array(ankleflex_y) - offset["ankleflex"])
        
        #########################################################################################

        shoulder_x, shoulder_y, shoulder_dof = get_angle(gait_data, wave, "left_shoulder", "right_shoulder")
        hip_x, hip_y, hip_dof = get_angle(gait_data, wave, "left_hip", "right_hip")

        shoulder_angle_list.append({"x": shoulder_x, "y": list(np.array(shoulder_y) - offset["shoulder"])})
        hip_angle_list.append({"x": hip_x, "y": list(np.array(hip_y) - offset["hip"])})

        bestshoulder_list["x"] += shoulder_x
        bestshoulder_list["y"] += list(np.array(shoulder_y) - offset["shoulder"])
        bestpelvic_list["x"] += hip_x
        bestpelvic_list["y"] += list(np.array(hip_y) - offset["hip"])

        #########################################################################################

    stats = {
        "rawData": {"x": raw_data["time"], "y":[elem["y"] for elem in raw_data["ref_heel"]]},
        "rawGaitCycle": gaitCycle_list,
        "superGaitCycle": superGaitCycle_list,
        "heelX": heelX_list, 
        "heelY": heelY_list, 
        "heelZ": heelZ_list, 
        "shoulder": shoulder_angle_list,
        "hip_obliq": hip_angle_list,       
        "hipflex": hipflex_list,
        "kneeflex": kneeflex_list,
        "ankleflex": ankleflex_list,
        "bestshoulder": walkE_math.best_fit(bestshoulder_list, shoulder_dof),
        "besthip": walkE_math.best_fit(bestpelvic_list, hip_dof),
        "besthip": walkE_math.best_fit(besthip_list, hipflex_dof),
        "bestknee": walkE_math.best_fit(bestknee_list, kneeflex_dof),
        "bestankle": walkE_math.best_fit(bestankle_list, ankleflex_dof),
        "cadence": get_cadence(gait_data),
        "speed": "-",
        "dist": "-",
        "stride_len": "-"
    }
    
    print("Stats Calculation Complete")

    return stats

#################################################################################################
#  .\venv\Scripts\python.exe -m pylint .\Walk-E\gaitAnalysis.py