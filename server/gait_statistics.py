import numpy as np
import walkE_math
from sklearn.metrics import mean_squared_error as mse

#################################################################################################

MIN_CHUNKSIZE = 3
POINTS_SPACE = 20
MAX_MSE = 100
MAX_ITR = 10

HEEL_DOF = 5
HIPFLEX_DOF = 4
KNEEFLEX_DOF = 7
ANKLEFLEX_DOF = 7

#################################################################################################

def add_points(joint_data, unit_space):
    new_jointdata = {
        "ref_heel": [],
        "left_shoulder": [],
        "left_hip": [],
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
    
    return new_jointdata

def get_gait(heel_baseline, raw_joint):
    cutoff_index, format_jointdata = [], add_points(raw_joint, POINTS_SPACE)

    # Identify cutoff points in data
    for elem in format_jointdata["ref_heel"]:
        if round(elem["y"], 2) == round(heel_baseline, 2):
            cutoff_index.append(format_jointdata["ref_heel"].index(elem))

    ##############################################################################################

    # Slice data points based on identified cutoff points
    sine_joint = {
        "ref_heel": [format_jointdata["ref_heel"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "left_shoulder": [format_jointdata["left_shoulder"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "left_hip": [format_jointdata["left_hip"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "knee": [format_jointdata["knee"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "ankle": [format_jointdata["ankle"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "toe": [format_jointdata["toe"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)],
        "time": [format_jointdata["time"][cutoff_index[x]:cutoff_index[x+1]] for x in range(0, len(cutoff_index) - 1)]
    }

    try:
        sine_joint["ref_heel"].append(format_jointdata["ref_heel"][cutoff_index[-1]:])
        sine_joint["left_shoulder"].append(format_jointdata["ref_heel"][cutoff_index[-1]:])
        sine_joint["left_hip"].append(format_jointdata["ref_heel"][cutoff_index[-1]:])
        sine_joint["knee"].append(format_jointdata["ref_heel"][cutoff_index[-1]:])
        sine_joint["ankle"].append(format_jointdata["ref_heel"][cutoff_index[-1]:])
        sine_joint["toe"].append(format_jointdata["ref_heel"][cutoff_index[-1]:])
        sine_joint["time"].append(format_jointdata["time"][cutoff_index[-1]:])
    except:
        pass

    # Remove data points that are too short in length
    sine_joint = {
        "ref_heel": [data for data in sine_joint["ref_heel"] if len(data) > MIN_CHUNKSIZE],
        "left_shoulder": [data for data in sine_joint["left_shoulder"] if len(data) > MIN_CHUNKSIZE],
        "left_hip": [data for data in sine_joint["left_hip"] if len(data) > MIN_CHUNKSIZE],
        "knee": [data for data in sine_joint["knee"] if len(data) > MIN_CHUNKSIZE],
        "ankle": [data for data in sine_joint["ankle"] if len(data) > MIN_CHUNKSIZE],
        "toe": [data for data in sine_joint["toe"] if len(data) > MIN_CHUNKSIZE],
        "time": [data for data in sine_joint["time"] if len(data) > MIN_CHUNKSIZE]
    } 
            
    ##############################################################################################

    # Retrieve complete waveforms and remove wavelengths that are too long
    gait_joint = {
        "ref_heel": [],
        "left_shoulder": [],
        "left_hip": [],
        "knee": [],
        "ankle": [],
        "toe": [],
        "time": [],
        "gait_cycle": []
    }
    
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

            gait_joint["ref_heel"].append(sine_joint["ref_heel"][wave][max_first_index:] + sine_joint["ref_heel"][wave + 1] + sine_joint["ref_heel"][wave + 2 ][:max_third_index])       
            gait_joint["left_shoulder"].append(sine_joint["left_shoulder"][wave][max_first_index:] + sine_joint["left_shoulder"][wave + 1] + sine_joint["left_shoulder"][wave + 2][:max_third_index])
            gait_joint["left_hip"].append(sine_joint["left_hip"][wave][max_first_index:] + sine_joint["left_hip"][wave + 1] + sine_joint["left_hip"][wave + 2][:max_third_index])
            gait_joint["knee"].append(sine_joint["knee"][wave][max_first_index:] + sine_joint["knee"][wave + 1] + sine_joint["knee"][wave + 2][:max_third_index])
            gait_joint["ankle"].append(sine_joint["ankle"][wave][max_first_index:] + sine_joint["ankle"][wave + 1] + sine_joint["ankle"][wave + 2][:max_third_index])
            gait_joint["toe"].append(sine_joint["toe"][wave][max_first_index:] + sine_joint["toe"][wave + 1] + sine_joint["toe"][wave + 2][:max_third_index])
            gait_joint["time"].append(sine_joint["time"][wave][max_first_index:] + sine_joint["time"][wave + 1] + sine_joint["time"][wave + 2][:max_third_index])
            
        except:
            pass

    for time in gait_joint["time"]:
        gait_joint["gait_cycle"].append(walkE_math.normalize_gait(time))
    
    ##############################################################################################
    
    # walkE_plot.get_gait(raw_joint, sine_joint, gait_joint)

    print("Data Slicing Complete")

    return gait_joint   

#################################################################################################

def poly_fit(x,y):
    
    mse_dof, mean_square =  0, MAX_MSE

    def poly_func(x,y,dof):
        curve = np.polyfit(x, y, dof)
        poly = np.poly1d(curve)

        new_x = x
        new_x.sort()

        return new_x, [poly(data) for data in new_x]

    for dof_itera in range(1, MAX_ITR):
        try:
            msq = mse(y, poly_func(x,y,dof_itera)[1]) 

            if msq < mean_square:
                mean_square = msq
                mse_dof = dof_itera

        except:
            pass
    
    return poly_func(x,y,mse_dof)

def get_heel(gait_data, waveform, axis):
    x, y = [], []

    x += [gait_data["gait_cycle"][waveform][index]
                for index in range(len(gait_data["gait_cycle"][waveform]))]
    y += [gait_data["ref_heel"][waveform][index][axis]
                for index in range(len(gait_data["ref_heel"][waveform]))]
   
    new_x, new_y = poly_fit(x, y)
    
    return new_x, new_y, y

def get_planeangle(gait_data, waveform, first, secnd):
    pass

def get_flex(gait_data, waveform, first, secnd, third):
    x, y = [], []

    for index in range(len(gait_data[first][waveform])):
        first_pt = gait_data[first][waveform][index]
        secnd_pt = gait_data[secnd][waveform][index]
        third_pt = gait_data[third][waveform][index]

        x.append(gait_data["gait_cycle"][waveform][index])
        y.append(180 - walkE_math.cal_threeD_angle(first_pt, secnd_pt, third_pt)) 
        
    new_x, new_y = poly_fit(x,y)

    return new_x, new_y, y

def best_fit(json, dof):
    x, y = json["x"], json["y"]
    
    curve = np.polyfit(x, y, dof)
    poly = np.poly1d(curve)

    x.sort()
    new_y = [poly(data) for data in x]
    
    return {"x": x, "y": new_y}

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
    oldHeelX_list, oldHeelY_list, oldHeelZ_list = [], [], []
    
    hipflex_list, kneeflex_list, ankleflex_list = [], [], []
    besthip_list, bestknee_list, bestankle_list = { "x": [], "y": [] }, { "x": [], "y": [] }, { "x": [], "y": [] }
    oldHipFlex_list, oldKneeFlex_list, oldAnkleFlex_list = [], [], []

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

        heelX_x, heelX_y, old_heelX_y = get_heel(gait_data, wave, "x")
        heelY_x, heelY_y, old_heelY_y = get_heel(gait_data, wave, "y")
        heelZ_x, heelZ_y, old_heelZ_y = get_heel(gait_data, wave, "z")

        heelX_list.append({"x": heelX_x, "y": heelX_y})
        heelY_list.append({"x": heelY_x, "y": heelY_y})
        heelZ_list.append({"x": heelZ_x, "y": heelZ_y})

        oldHeelX_list.append({"x": heelX_x, "y": old_heelX_y})
        oldHeelY_list.append({"x": heelY_x, "y": old_heelY_y})
        oldHeelZ_list.append({"x": heelZ_x, "y": old_heelZ_y})

        #########################################################################################

        shoulder_x, shoulder_y = get_planeangle(gait_data, wave)

        #########################################################################################

        hipflex_x, hipflex_y, old_hipflex_y = get_flex(gait_data, wave, "left_shoulder", "left_hip", "knee")
        kneeflex_x, kneeflex_y, old_kneeflex_y= get_flex(gait_data, wave, "left_hip", "knee", "ankle")
        ankleflex_x, ankleflex_y, old_ankleflex_y = get_flex(gait_data, wave, "knee", "ankle", "toe")

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

    stats = {
        "rawData": {"x": raw_data["time"], "y":[elem["y"] for elem in raw_data["ref_heel"]]},
        "rawGaitCycle": gaitCycle_list,
        "superGaitCycle": superGaitCycle_list,
        "heelX": heelX_list, 
        "heelY": heelY_list, 
        "heelZ": heelZ_list, 
        # "pelvic_obliq": "",
        # "shoulder": "",
        "hipflex": hipflex_list,
        "kneeflex": kneeflex_list,
        "ankleflex": ankleflex_list,
        # "bestpevlic":"",
        # "bestshoulder": "",
        "besthip": best_fit(besthip_list, HIPFLEX_DOF),
        "bestknee": best_fit(bestknee_list, KNEEFLEX_DOF),
        "bestankle": best_fit(bestankle_list, ANKLEFLEX_DOF),
        "cadence": get_cadence(gait_data),
        "speed": "-",
        "dist": "-",
        "stride_len": "-"
    }
    
    print("Stats Calculation Complete")

    return stats

#################################################################################################

#  .\venv\Scripts\python.exe -m pylint .\Walk-E\gaitAnalysis.py