import matplotlib.pyplot as plt

def modified_gait(joint_data, new_jointdata, gait_jointdata):
    fig, axs = plt.subplots(2, 2, constrained_layout = True)
    
    for index in range(len(joint_data["ref_heel"])):
        ref_list = []

        for elem in joint_data["ref_heel"][index]:
            ref_list.append(elem["y"])
        
        axs[0,0].plot(joint_data["time"][index], ref_list)
    
    for index in range(len(new_jointdata["ref_heel"])):
        ref_list = []

        for elem in new_jointdata["ref_heel"][index]:
            ref_list.append(elem["y"])
        
        axs[0,1].plot(new_jointdata["time"][index], ref_list)

    for index in range(len(gait_jointdata["ref_heel"])):
        ref_list = []

        for elem in gait_jointdata["ref_heel"][index]:
            ref_list.append(elem["y"])
        
        axs[1,0].plot(gait_jointdata["time"][index], ref_list)

    plt.show()
