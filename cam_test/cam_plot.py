import matplotlib.pyplot as plt
import cam_dict
import numpy as np

HEEL_DOF = 5
HIPFLEX_DOF = 4
KNEEFLEX_DOF = 7
ANKLEFLEX_DOF = 7

REF_POINT = cam_dict.ref_pt

def left_heel(joint_data):
    fig, axs = plt.subplots(2, 2, constrained_layout = True)
    axs[0, 0].plot(joint_data["time"], 
                   [data["y"] for data in joint_data["left_heel"]])
    axs[0, 1].plot(joint_data["time"], 
                   [data["x"] for data in joint_data["left_heel"]])
    
    axs[0, 0].set(xlabel = "time (sec)", ylabel = "y-coordinate of left heel",
            title = "Raw Data of Heel")
    axs[0, 1].set(xlabel = "time (sec)", ylabel = "x-coordinate of left heel",
            title = "Raw Data of Heel")
    
    plt.show()
    
#################################################################################################

def get_gait(raw_data, joint_data, new_jointdata):
    fig, axs = plt.subplots(2, 2, constrained_layout = True)
    
    for index in range(len(raw_data["ref_heel"])):
        ref_list = []

        for elem in raw_data["ref_heel"]:
            ref_list.append(elem["x"])
        
        axs[0,0].plot(raw_data["time"], ref_list)
    
    axs[0, 0].set(xlabel = "time (sec)", ylabel = "x-coordinate of heel",
                title = "Raw Data")
    
    #############################################################################################
    
    for index in range(len(joint_data["ref_heel"])):
        ref_list = []

        for elem in joint_data["ref_heel"][index]:
            ref_list.append(elem["x"])
        
        axs[0,1].plot(joint_data["time"][index], ref_list)
    
    axs[0, 1].set(xlabel = "time (sec)", ylabel = "x-coordinate of heel",
                title = "Upper & Lower Sinewaves of Heel")
    
    #############################################################################################

    for index in range(len(new_jointdata["ref_heel"])):
        ref_list = []

        for elem in new_jointdata["ref_heel"][index]:
            ref_list.append(elem["x"])
        
        axs[1, 0].plot(new_jointdata["time"][index], ref_list)
    
    axs[1, 0].set(xlabel = "time (sec)", ylabel = "x-coordinate of heel",
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
        
        new_y = [poly(data) for data in x]
        
        axs[1,1].plot(x, new_y)
    
    axs[1, 1].set(xlabel = "time (sec)", ylabel = "x-coordinate of heel",
                title = "Best Fit Curve Waveform of Heel")

    plt.show()
    print("Complete")

#################################################################################################

def stats(stats_data):
    fig, axs = plt.subplots(3, 3, constrained_layout = True)

    #############################################################################################

    axs[0, 0].plot(stats_data["rawData"]["x"], stats_data["rawData"]["y"])
    axs[0, 0].set(xlabel = "time (sec)", ylabel = "x-coordinate of heel",
                title = "Raw Data of Heel")
   
    #############################################################################################

    for waveform in stats_data["rawGaitCycle"]:
        axs[0, 1].plot(waveform["x"], waveform["y"])
    
    axs[0, 1].set(xlabel = "time (sec)", ylabel = "x-coordinate of Heel", 
                    title= "Segregation of Gait Cycle")
    
    #############################################################################################

    for waveform in stats_data["superGaitCycle"]:
        axs[0, 2].scatter(waveform["x"], waveform["y"],
                        c=["#808080"]*len(waveform["y"]),
                        s=[2]*len(waveform["y"]))

    axs[0, 2].set(xlabel = "Gait Cycle (%)", ylabel = "x-coordinate of Heel",
                    title = "Scatterplot of Identified Gait Cycles")

    #############################################################################################
    
    for waveform in stats_data["hipflex"]:
        axs[1, 0].scatter(waveform["x"], waveform["y"],
                        c=["#808080"]*len(waveform["y"]),
                        s=[2]*len(waveform["y"]))

    axs[1, 0].set(xlabel = "Gait Cycle (%)", ylabel = "Angle (Degree)",
                    title = "Hip Flex")
    
    axs[2, 0].plot(stats_data["besthip"]["x"], stats_data["besthip"]["y"])
    axs[2, 0].set(xlabel = "time (sec)", ylabel = "Angle (Degree)",
                title = "Best Fit Curve of Hip Flex")
    
    #############################################################################################

    for waveform in stats_data["kneeflex"]:
        axs[1, 1].scatter(waveform["x"], waveform["y"],
                        c=["#808080"]*len(waveform["y"]),
                        s=[2]*len(waveform["y"]))

    axs[1, 1].set(xlabel = "Gait Cycle (%)", ylabel = "Angle (Degree)",
                    title = "Knee Flex")
    
    axs[2, 1].plot(stats_data["bestknee"]["x"], stats_data["bestknee"]["y"])
    axs[2, 1].set(xlabel = "time (sec)", ylabel = "Angle (Degree)",
                title = "Best Fit Curve of Knee Flex")
    
    #############################################################################################

    for waveform in stats_data["ankleflex"]:
        axs[1, 2].scatter(waveform["x"], waveform["y"],
                        c=["#808080"]*len(waveform["y"]),
                        s=[2]*len(waveform["y"]))

    axs[1, 2].set(xlabel = "Gait Cycle (%)", ylabel = "Angle (Degree)",
                    title = "Ankle Flex")
    
    axs[2, 2].plot(stats_data["bestankle"]["x"], stats_data["bestankle"]["y"])
    axs[2, 2].set(xlabel = "time (sec)", ylabel = "Angle (Degree)",
                title = "Best Fit Curve of Ankle Flex")
    
    #############################################################################################
       
    plt.show()
    print("Complete")
    
#################################################################################################
