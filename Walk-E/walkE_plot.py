import matplotlib.pyplot as plt
import gaitAnalysis as ga
import numpy as np

HEEL_DOF = 5
HIPFLEX_DOF = 5
KNEEFLEX_DOF = 10
ANKLEFLEX_DOF = 10

def calibrate(calibrate_data):    
    fig, axs = plt.subplots(3, 3, constrained_layout = True)

    ref_list = []
    for elem in calibrate_data["ref_heel"]:
        ref_list.append(elem["y"])

    axs[0, 0].plot(calibrate_data["time"], ref_list)
    axs[0, 0].set(xlabel = "time (sec)", ylabel = "y-coordinate of heel",
                title = "Raw Data of Heel")

    heelX_list = [data_point["x"] for data_point in calibrate_data["ref_heel"]]
    heelY_list = [data_point["y"] for data_point in calibrate_data["ref_heel"]]
    heelZ_list = [data_point["z"] for data_point in calibrate_data["ref_heel"]]

    axs[1, 0].scatter(calibrate_data["time"], heelX_list,
                    c=["#808080"]*len(heelX_list),
                    s=[2]*len(heelX_list))
    axs[1, 0].set(xlabel="time (sec)", ylabel = "x-coordinate of Heel",
                title = "X Movement of Heel")

    axs[1, 1].scatter(calibrate_data["time"], heelY_list,
                    c=["#808080"]*len(heelY_list),
                    s=[2]*len(heelY_list))
    axs[1, 1].set(xlabel="time (sec)", ylabel = "y-coordinate of Heel",
                title = "Y Movement of Heel")

    axs[1, 2].scatter(calibrate_data["time"], heelZ_list,
                    c=["#808080"]*len(heelZ_list),
                    s=[2]*len(heelZ_list))
    axs[1, 2].set(xlabel="time (sec)", ylabel = "z-coordinate of Heel",
                title = "Z Movement of Heel")

#################################################################################################
    
    hipflex_data = ga.calibrate_flex(calibrate_data, "shoulder", "hip", "knee")
    kneeflex_data = ga.calibrate_flex(calibrate_data, "hip", "knee", "ankle")
    ankleflex_data = ga.calibrate_flex(calibrate_data, "knee", "ref_heel", "toe")

    axs[2, 0].scatter(hipflex_data["time"], hipflex_data["flex_data"],
                    c=["#808080"]*len(hipflex_data["flex_data"]),
                    s=[2]*len(hipflex_data["flex_data"]))
    axs[2, 0].set(xlabel="time (sec)", ylabel = "Hip Flex (Degree)",
                title = "Hip Flex")

    axs[2, 1].scatter(kneeflex_data["time"], kneeflex_data["flex_data"],
                    c=["#808080"]*len(kneeflex_data["flex_data"]),
                    s=[2]*len(kneeflex_data["flex_data"]))
    axs[2, 1].set(xlabel="time (sec)", ylabel = "Knee Flex (Degree)",
                title = "Knee Flex")

    axs[2, 2].scatter(ankleflex_data["time"], ankleflex_data["flex_data"],
                    c=["#808080"]*len(ankleflex_data["flex_data"]),
                    s=[2]*len(ankleflex_data["flex_data"]))
    axs[2, 2].set(xlabel="time (sec)", ylabel = "Ankle Flex (Degree)",
                title = "Ankle Flex")  

    offset_json = {
        "cut_off": np.mean(heelY_list),
        "hipflex": np.mean(hipflex_data["flex_data"]),
        "kneeflex": np.mean(kneeflex_data["flex_data"]),
        "ankleflex": np.mean(ankleflex_data["flex_data"])
    }

    plt.show()
    print("Complete")

    return offset_json

def modified_gait(joint_data, new_jointdata, gait_jointdata):
    fig, axs = plt.subplots(2, 2, constrained_layout = True)
    
    #############################################################################################
    
    for index in range(len(joint_data["ref_heel"])):
        ref_list = []

        for elem in joint_data["ref_heel"][index]:
            ref_list.append(elem["y"])
        
        axs[0,0].plot(joint_data["time"][index], ref_list)
    
    #############################################################################################

    for index in range(len(new_jointdata["ref_heel"])):
        ref_list = []

        for elem in new_jointdata["ref_heel"][index]:
            ref_list.append(elem["y"])
        
        axs[0,1].plot(new_jointdata["time"][index], ref_list)

    #############################################################################################

    for index in range(len(gait_jointdata["ref_heel"])):
        ref_list = []

        for elem in gait_jointdata["ref_heel"][index]:
            ref_list.append(elem["y"])
        
        axs[1,0].plot(gait_jointdata["time"][index], ref_list)

    #############################################################################################

    plt.show()
    print("Complete")

def stats_result(joint_data, gait_jointdata, offset):
    
    hipflex_data = ga.get_flex(gait_jointdata, "shoulder", "hip", "knee")
    kneeflex_data = ga.get_flex(gait_jointdata, "hip", "knee", "ankle")
    ankleflex_data = ga.get_flex(gait_jointdata, "knee", "ref_heel", "toe")

    heelX_x, heelX_y, heelX_polyfit = ga.polyfit_heel(gait_jointdata, "x", HEEL_DOF)
    heelY_x, heelY_y, heelY_polyfit = ga.polyfit_heel(gait_jointdata, "y", HEEL_DOF)
    heelZ_x, heelZ_y, heelZ_polyfit = ga.polyfit_heel(gait_jointdata, "z", HEEL_DOF)
    hipflex_x, hipflex_y, hipflex_polyfit = ga.polyfit_flex(hipflex_data, HIPFLEX_DOF)
    kneeflex_x, kneeflex_y, kneeflex_polyfit = ga.polyfit_flex(kneeflex_data, KNEEFLEX_DOF)
    ankleflex_x, ankleflex_y, ankleflex_polyfit = ga.polyfit_flex(ankleflex_data, ANKLEFLEX_DOF)
    
    #############################################################################################
    
    fig, axs = plt.subplots(3, 3, constrained_layout = True)

    ref_list = []
    for elem in joint_data["ref_heel"]:
        ref_list.append(elem["y"])

    axs[0, 0].plot(joint_data["time"], ref_list)
    axs[0, 0].set(xlabel = "time (sec)", ylabel = "y-coordinate of heel",
                title = "Raw Data of Heel")

    for waveform in range(len(gait_jointdata["ref_heel"])):
        heelX_list, heelY_list, heelZ_list = [], [], []
        hipflex_list, kneeflex_list, ankleflex_list = [], [], []

        for data_point in gait_jointdata["ref_heel"][waveform]:
            heelX_list.append(data_point["x"])
            heelY_list.append(data_point["y"])
            heelZ_list.append(data_point["z"])
        for data_point in hipflex_data["flex_data"][waveform]:
            hipflex_list.append(data_point)
        for data_point in kneeflex_data["flex_data"][waveform]:
            kneeflex_list.append(data_point)
        for data_point in ankleflex_data["flex_data"][waveform]:
            ankleflex_list.append(data_point)

        axs[0, 1].plot(gait_jointdata["time"][waveform], heelY_list)
        axs[0, 1].set(xlabel = "time (sec)", ylabel = "y-coordinate of Heel", 
                    title= "Segregation of Gait Cycle")

        axs[0, 2].scatter(gait_jointdata["gait_cycle"][waveform], heelY_list,
                        s=[2 for i in range(len(heelY_list))])
        axs[0, 2].set(xlabel = "time (sec)", ylabel = "y-coordinate of Heel",
                    title = "Scatterplot of Identified Gait Cycles")

        axs[1, 0].scatter(gait_jointdata["gait_cycle"][waveform], heelX_list,
                        c=["#808080"]*len(heelX_list),
                        s=[2]*len(heelX_list))
        axs[1, 1].scatter(gait_jointdata["gait_cycle"][waveform], heelY_list,
                        c=["#808080"]*len(heelY_list),
                        s=[2]*len(heelY_list))
        axs[1, 2].scatter(gait_jointdata["gait_cycle"][waveform], heelZ_list,
                        c=["#808080"]*len(heelZ_list),
                        s=[2]*len(heelZ_list))

        axs[2, 0].scatter(gait_jointdata["gait_cycle"][waveform], hipflex_list,
                        c=["#808080"]*len(hipflex_list),
                        s=[2]*len(hipflex_list))
        axs[2, 1].scatter(gait_jointdata["gait_cycle"][waveform], kneeflex_list,
                        c=["#808080"]*len(kneeflex_list),
                        s=[2]*len(kneeflex_list))
        axs[2, 2].scatter(gait_jointdata["gait_cycle"][waveform], ankleflex_list,
                        c=["#808080"]*len(ankleflex_list),
                        s=[2]*len(ankleflex_list))

    axs[1, 0].plot(heelX_x, heelX_y, "r")
    axs[1, 0].set(xlabel="Gait Cycle", ylabel = "x-coordinate of Heel",
                title = "Best Fit Curve of X Movement of Heel")

    axs[1, 1].plot(heelY_x, heelY_y, "r")
    axs[1, 1].set(xlabel="Gait Cycle", ylabel = "y-coordinate of Heel",
                title = "Best Fit Curve of Y Movement of Heel")

    axs[1, 2].plot(heelZ_x, heelZ_y, "r")
    axs[1, 2].set(xlabel="Gait Cycle", ylabel = "z-coordinate of Heel",
                title = "Best Fit Curve of Z Movement of Heel")

    axs[2, 0].plot(hipflex_x, np.array(hipflex_y) - offset["hipflex"], "r")
    axs[2, 0].set(xlabel="Gait Cycle", ylabel = "Hip Flex (Degree)",
                title = "Best Fit Curve of Hip Flex")

    axs[2, 1].plot(kneeflex_x, np.array(kneeflex_y) - offset["kneeflex"], "r")
    axs[2, 1].set(xlabel="Gait Cycle", ylabel = "Knee Flex (Degree)",
                title = "Best Fit Curve of Knee Flex")

    axs[2, 2].plot(ankleflex_x, np.array(ankleflex_y) - offset["ankleflex"], "r")
    axs[2, 2].set(xlabel="Gait Cycle", ylabel = "Ankle Flex (Degree)",
                title = "Best Fit Curve of Ankle Flex")

    plt.show()
    print("Complete")
 