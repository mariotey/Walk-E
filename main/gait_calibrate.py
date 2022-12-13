import numpy as np
import walkE_math
import walkE_plot

#################################################################################################

def calibrate_flex(joint_data, first, sec, third):
    flex_data = {
        "flex_data": [],
        "time": []
    }

    for data_point in range(len(joint_data[first])):
        flex_list, time_list = [], []
        
        first_pt = joint_data[first][data_point]
        sec_pt = joint_data[sec][data_point]
        third_pt = joint_data[third][data_point]

        flex_list.append(180 - walkE_math.cal_threeD_angle(first_pt, sec_pt, third_pt))
        time_list.append(joint_data["time"][data_point])

        flex_data["flex_data"].append(flex_list)
        flex_data["time"].append(time_list)

    return flex_data

def calibrate(calibrate_data):        
    ref_list = []
    for elem in calibrate_data["ref_heel"]:
        ref_list.append(elem["y"])

    heelX_list = [data_point["x"] for data_point in calibrate_data["ref_heel"]]
    heelY_list = [data_point["y"] for data_point in calibrate_data["ref_heel"]]
    heelZ_list = [data_point["z"] for data_point in calibrate_data["ref_heel"]]
    
    hipflex_data = calibrate_flex(calibrate_data, "shoulder", "hip", "knee")
    kneeflex_data = calibrate_flex(calibrate_data, "hip", "knee", "ankle")
    ankleflex_data = calibrate_flex(calibrate_data, "knee", "ref_heel", "toe")

    walkE_plot.calibrate(ref_list, heelX_list, heelY_list, heelZ_list, 
                        hipflex_data, kneeflex_data, ankleflex_data,
                        calibrate_data["time"])

    offset_json = {
        "cut_off": np.mean(heelY_list),
        "hipflex": np.mean(hipflex_data["flex_data"]),
        "kneeflex": np.mean(kneeflex_data["flex_data"]),
        "ankleflex": np.mean(ankleflex_data["flex_data"])
    }

    print("Complete")

    return offset_json

#################################################################################################

#  .\venv\Scripts\python.exe -m pylint .\Walk-E\gaitAnalysis.py