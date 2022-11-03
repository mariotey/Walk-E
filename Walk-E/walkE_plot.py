import matplotlib.pyplot as plt
import gaitAnalysis as ga
import numpy as np
from matplotlib.widgets import Slider

HEEL_DOF = 5
HIPFLEX_DOF = 4
KNEEFLEX_DOF = 7
ANKLEFLEX_DOF = 7

def calibrate(ref_list, heelX, heelY, heelZ, hipflex, kneeflex, ankleflex, time):    
    fig, axs = plt.subplots(3, 3, constrained_layout = True)

    axs[0, 0].plot(time, ref_list)
    axs[0, 0].set(xlabel = "time (sec)", ylabel = "y-coordinate of heel",
                title = "Raw Data of Heel")

    axs[1, 0].scatter(time, heelX,
                    c=["#808080"]*len(heelX),
                    s=[2]*len(heelX))
    axs[1, 0].set(xlabel="time (sec)", ylabel = "x-coordinate of Heel",
                title = "X Movement of Heel")

    axs[1, 1].scatter(time, heelY,
                    c=["#808080"]*len(heelY),
                    s=[2]*len(heelY))
    axs[1, 1].set(xlabel="time (sec)", ylabel = "y-coordinate of Heel",
                title = "Y Movement of Heel")

    axs[1, 2].scatter(time, heelZ,
                    c=["#808080"]*len(heelZ),
                    s=[2]*len(heelZ))
    axs[1, 2].set(xlabel="time (sec)", ylabel = "z-coordinate of Heel",
                title = "Z Movement of Heel")

#################################################################################################

    axs[2, 0].scatter(hipflex["time"], hipflex["flex_data"],
                    c=["#808080"]*len(hipflex["flex_data"]),
                    s=[2]*len(hipflex["flex_data"]))
    axs[2, 0].set(xlabel="time (sec)", ylabel = "Hip Flex (Degree)",
                title = "Hip Flex")

    axs[2, 1].scatter(kneeflex["time"], kneeflex["flex_data"],
                    c=["#808080"]*len(kneeflex["flex_data"]),
                    s=[2]*len(kneeflex["flex_data"]))
    axs[2, 1].set(xlabel="time (sec)", ylabel = "Knee Flex (Degree)",
                title = "Knee Flex")

    axs[2, 2].scatter(ankleflex["time"], ankleflex["flex_data"],
                    c=["#808080"]*len(ankleflex["flex_data"]),
                    s=[2]*len(ankleflex["flex_data"]))
    axs[2, 2].set(xlabel="time (sec)", ylabel = "Ankle Flex (Degree)",
                title = "Ankle Flex")  

    plt.show()
    print("Complete")

#################################################################################################

def get_gait(raw_data, joint_data, new_jointdata):
    fig, axs = plt.subplots(2, 2, constrained_layout = True)
    
    for index in range(len(raw_data["ref_heel"])):
        ref_list = []

        for elem in raw_data["ref_heel"]:
            ref_list.append(elem["y"])
        
        axs[0,0].plot(raw_data["time"], ref_list)
    
    axs[0, 0].set(xlabel = "time (sec)", ylabel = "y-coordinate of heel",
                title = "Raw Data")


    #############################################################################################
    
    for index in range(len(joint_data["ref_heel"])):
        ref_list = []

        for elem in joint_data["ref_heel"][index]:
            ref_list.append(elem["y"])
        
        axs[0,1].plot(joint_data["time"][index], ref_list)
    
    axs[0, 1].set(xlabel = "time (sec)", ylabel = "y-coordinate of heel",
                title = "Upper & Lower Sinewaves of Heel")
    
    #############################################################################################

    for index in range(len(new_jointdata["ref_heel"])):
        ref_list = []

        for elem in new_jointdata["ref_heel"][index]:
            ref_list.append(elem["y"])
        
        axs[1, 0].plot(new_jointdata["time"][index], ref_list)
    
    axs[1, 0].set(xlabel = "time (sec)", ylabel = "y-coordinate of heel",
                title = "Gait Waveform of Heel")

    #############################################################################################

    for wave in range(len(new_jointdata["ref_heel"])):
        x = [new_jointdata["time"][wave][index]
                     for index in range(len(new_jointdata["time"][wave]))]
        y = [new_jointdata["ref_heel"][wave][index]["y"]
                    for index in range(len(new_jointdata["ref_heel"][wave]))]
        
        axs[1, 1].scatter(x,y,
                c=["#808080"]*len(y),
                s=[2]*len(y))

        curve = np.polyfit(x, y, 4)
        poly = np.poly1d(curve)

        x.sort()
        
        # new_y = [test_func(elem, params[0], params[1]) for elem in x]
        new_y = [poly(data) for data in x]
        
        axs[1,1].plot(x, new_y)
    
    axs[1, 1].set(xlabel = "time (sec)", ylabel = "y-coordinate of heel",
                title = "Best Fit Curve Waveform of Heel")

    plt.show()
    print("Complete")

#################################################################################################

def stats(raw_data, gait_data):
    fig, axs = plt.subplots(3, 3, constrained_layout = True)

    #############################################################################################

    axs[0, 0].plot(raw_data["rawData"]["x"], raw_data["rawData"]["y"])
    axs[0, 0].set(xlabel = "time (sec)", ylabel = "y-coordinate of heel",
                title = "Raw Data of Heel")
   
    #############################################################################################

    for waveform in gait_data["rawGaitCycle"]:
        axs[0, 1].plot(waveform["x"], waveform["y"])
    
    axs[0, 1].set(xlabel = "time (sec)", ylabel = "y-coordinate of Heel", 
                    title= "Segregation of Gait Cycle")
    
    #############################################################################################

    for waveform in gait_data["superGaitCycle"]:
        axs[0, 2].scatter(waveform["x"], waveform["y"],
                        c=["#808080"]*len(waveform["y"]),
                        s=[2]*len(waveform["y"]))
        
        poly_x, poly_y = ga.best_fit(waveform, HEEL_DOF)
        axs[0, 2].plot(poly_x, poly_y)

    axs[0, 2].set(xlabel = "Gait Cycle (%)", ylabel = "y-coordinate of Heel",
                    title = "Scatterplot of Identified Gait Cycles")

    #############################################################################################
    
    heelX_list = { "x": [], "y": [] }

    for waveform in gait_data["heelX"]:
        axs[1, 0].plot(waveform["x"], waveform["y"], color = "gray")
        
        heelX_list["x"] += waveform["x"]
        heelX_list["y"] += waveform["y"]

    # for waveform in raw_data["heelX"]:
    #     axs[1, 0].scatter(waveform["x"], waveform["y"],
    #                 c=["#FF0000"]*len(waveform["y"]),
    #                 s=[2]*len(waveform["y"]))

    poly_heelX_x, poly_heelX_y = ga.best_fit(heelX_list, HEEL_DOF)
    axs[1, 0].plot(poly_heelX_x, poly_heelX_y, "r")

    axs[1, 0].set(xlabel="Gait Cycle (%)", ylabel = "x-coordinate of Heel",
                title = "Best Fit Curve of X Movement of Heel")

    #############################################################################################

    heelY_list = { "x": [], "y": [] }

    for waveform in gait_data["heelY"]:
        axs[1, 1].plot(waveform["x"], waveform["y"], color = "gray")

        heelY_list["x"] += waveform["x"]
        heelY_list["y"] += waveform["y"]

    # for waveform in raw_data["heelY"]:
    #     axs[1, 1].scatter(waveform["x"], waveform["y"],
    #                 c=["#FF0000"]*len(waveform["y"]),
    #                 s=[2]*len(waveform["y"]))

    poly_heelY_x, poly_heelY_y = ga.best_fit(heelY_list, HEEL_DOF)
    axs[1, 1].plot(poly_heelY_x, poly_heelY_y, "r")
    
    axs[1, 1].set(xlabel="Gait Cycle (%)", ylabel = "y-coordinate of Heel",
                title = "Best Fit Curve of Y Movement of Heel")

    #############################################################################################

    heelZ_list = { "x": [], "y": [] }

    for waveform in gait_data["heelZ"]:
        axs[1, 2].plot(waveform["x"], waveform["y"], color = "gray")

        heelZ_list["x"] += waveform["x"]
        heelZ_list["y"] += waveform["y"]

    # for waveform in raw_data["heelZ"]:
    #     axs[1, 2].scatter(waveform["x"], waveform["y"],
    #                 c=["#FF0000"]*len(waveform["y"]),
    #                 s=[2]*len(waveform["y"]))

    poly_heelZ_x, poly_heelZ_y = ga.best_fit(heelZ_list, HEEL_DOF)
    axs[1, 2].plot(poly_heelZ_x, poly_heelZ_y, "r")
    
    axs[1, 2].set(xlabel="Gait Cycle (%)", ylabel = "z-coordinate of Heel",
                title = "Best Fit Curve of Z Movement of Heel")   

    #############################################################################################

    hipflex_list = { "x": [], "y": [] }

    for waveform in gait_data["hipflex"]:
        axs[2, 0].plot(waveform["x"], waveform["y"], color = "gray")

        hipflex_list["x"] += waveform["x"]
        hipflex_list["y"] += waveform["y"]

    # for waveform in raw_data["hipflex"]:
    #     axs[2, 0].scatter(waveform["x"], waveform["y"],
    #                 c=["#FF0000"]*len(waveform["y"]),
    #                 s=[2]*len(waveform["y"]))

    poly_hipflex_x, poly_hipflex_y = ga.best_fit(hipflex_list, HIPFLEX_DOF)
    axs[2, 0].plot(poly_hipflex_x, poly_hipflex_y, "r")

    axs[2, 0].set(xlabel="Gait Cycle (%)", ylabel = "Hip Flex (Degree)",
                title = "Best Fit Curve of Hip Flex")

    #############################################################################################
    
    kneeflex_list = { "x": [], "y": [] }
    
    for waveform in gait_data["kneeflex"]:
        axs[2, 1].plot(waveform["x"], waveform["y"], color = "gray")

        kneeflex_list["x"] += waveform["x"]
        kneeflex_list["y"] += waveform["y"]
    
    # for waveform in raw_data["kneeflex"]:
    #     axs[2, 1].scatter(waveform["x"], waveform["y"],
    #                 c=["#FF0000"]*len(waveform["y"]),
    #                 s=[2]*len(waveform["y"]))

    poly_kneeflex_x, poly_kneeflex_y = ga.best_fit(kneeflex_list, KNEEFLEX_DOF)
    axs[2, 1].plot(poly_kneeflex_x, poly_kneeflex_y, "r")

    axs[2, 1].set(xlabel="Gait Cycle (%)", ylabel = "Knee Flex (Degree)",
                title = "Best Fit Curve of Knee Flex")

    #############################################################################################
    
    ankleflex_list = { "x": [], "y": [] }

    for waveform in gait_data["ankleflex"]:
        axs[2, 2].plot(waveform["x"], waveform["y"], color = "gray")

        ankleflex_list["x"] += waveform["x"]
        ankleflex_list["y"] += waveform["y"]
    
    # for waveform in raw_data["ankleflex"]:
    #     axs[2, 2].scatter(waveform["x"], waveform["y"],
    #                 c=["#FF0000"]*len(waveform["y"]),
    #                 s=[2]*len(waveform["y"]))

    poly_ankleflex_x, poly_ankleflex_y = ga.best_fit(ankleflex_list, ANKLEFLEX_DOF)
    axs[2, 2].plot(poly_ankleflex_x, poly_ankleflex_y, "r")

    axs[2, 2].set(xlabel="Gait Cycle (%)", ylabel = "Ankle Flex (Degree)",
                title = "Best Fit Curve of Ankle Flex")  

    #############################################################################################   
       
    plt.show()
    print("Complete")
    
#################################################################################################
 