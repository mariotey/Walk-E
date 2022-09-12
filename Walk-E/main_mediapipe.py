import cv2
import mediapipe as mp
import matplotlib.pyplot as plt
import time

import dist
import gaitAnalysis

HEEL_DOF = 6
HIPFLEX_DOF = 6
KNEEFLEX_DOF = 20
ANKLEFLEX_DOF = 8

mp_drawing = mp.solutions.drawing_utils # Drawing utilities for visualizing poses
mp_pose = mp.solutions.pose # Pose Estimation Model 

joint_data = {
    "ref_heel": [],
    "shoulder": [],
    "hip": [],
    "knee": [],
    "ankle": [],
    "toe":[],
    "time":[]
}

# Get Realtime Webcam Feed
cap = cv2.VideoCapture(1) # Get Video Capture Device

with mp_pose.Pose( #Setting up Pose Estimation Model
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    enable_segmentation=True,
    smooth_segmentation=True,
    smooth_landmarks=True,
    static_image_mode=False) as pose:

    start_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read() # Reads feed from Webcam

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Recolour Image feed (from openCV) from BGR to RGB
        image.flags.writeable = False # Save memory by setting writeable attribute as false; improves performance

        results = pose.process(image) # Pass recoloured image feed to Pose Estimation model for processing

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # Recolour Image back to BGR for openCV to process, Make Detection

        # Draw Pose Estimation landmarks
        mp_drawing.draw_landmarks(image, 
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2))

        # Extract landmarks
        try:
            camera_landmarks = results.pose_landmarks.landmark
            world_landmarks = results.pose_world_landmarks.landmark

            joint_data["ref_heel"].append(gaitAnalysis.get_bodypart_landmarks("LEFT_HEEL", world_landmarks)) # Heel Reference 
            joint_data["shoulder"].append(gaitAnalysis.get_bodypart_landmarks("LEFT_SHOULDER", world_landmarks)) # Shoulder Info
            joint_data["hip"].append(gaitAnalysis.get_bodypart_landmarks("LEFT_HIP", world_landmarks)) # Hip Info
            joint_data["knee"].append(gaitAnalysis.get_bodypart_landmarks("LEFT_KNEE", world_landmarks)) # Knee Info
            joint_data["ankle"].append(gaitAnalysis.get_bodypart_landmarks("LEFT_ANKLE", world_landmarks)) # Ankle Info
            joint_data["toe"].append(gaitAnalysis.get_bodypart_landmarks("LEFT_FOOT_INDEX", world_landmarks)) # Toe Info
            joint_data["time"].append(time.time() - start_time) # Time Info
           
            dist.detect(image, camera_landmarks)           
            
        except:
            # print("Nothing / Errors detected")
            pass # Pass if there is no detection or error
        
        cv2.imshow("Mediapipe Feed", image) # Render image result on screen

        # If keyboard "q" is hit after 0.01 sec, break from while loop
        if cv2.waitKey(10) & 0xFF == ord("q"): 
            break

format_jointdata = gaitAnalysis.get_raw_cycle(0.80, joint_data)
gait_jointdata = gaitAnalysis.get_gait_cycle(format_jointdata)

hipflex_data = gaitAnalysis.get_flex_data(gait_jointdata, "shoulder", "hip", "knee")
kneeflex_data= gaitAnalysis.get_flex_data(gait_jointdata, "hip", "knee", "ankle")
ankleflex_data = gaitAnalysis.get_flex_data(gait_jointdata, "knee", "ref_heel", "toe")

polyfit_heelX_x, polyfit_heelX_y, polyfit_heelX_curve = gaitAnalysis.polyfit_heel_curve(gait_jointdata, "x", HEEL_DOF)
polyfit_heelY_x, polyfit_heelY_y, polyfit_heelY_curve = gaitAnalysis.polyfit_heel_curve(gait_jointdata, "y", HEEL_DOF)
polyfit_heelZ_x, polyfit_heelZ_y, polyfit_heelZ_curve = gaitAnalysis.polyfit_heel_curve(gait_jointdata, "z", HEEL_DOF)
polyfit_hip_x, polyfit_hip_y, polyfit_hip_curve = gaitAnalysis.polyfit_flex_curve(hipflex_data, HIPFLEX_DOF)
polyfit_knee_x, polyfit_knee_y, polyfit_knee_curve = gaitAnalysis.polyfit_flex_curve(kneeflex_data, KNEEFLEX_DOF)
polyfit_ankle_x, polyfit_ankle_y, polyfit_ankle_curve = gaitAnalysis.polyfit_flex_curve(ankleflex_data, ANKLEFLEX_DOF)

###################################################################################################
fig, axs = plt.subplots(3,3, figsize=(4, 4), constrained_layout=True)

ref_list = []
for elem in joint_data["ref_heel"]:
    ref_list.append(elem["y"])

axs[0,0].plot(joint_data["time"], ref_list)

for waveform in range(len(gait_jointdata["ref_heel"])):
    heelX_list = []
    heelY_list = []
    heelZ_list = []

    hipflex_list = []
    kneeflex_list = []
    ankleflex_list = []

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

    axs[0,1].plot(gait_jointdata["time"][waveform], heelY_list)
    axs[0,2].scatter(gait_jointdata["gait_cycle"][waveform], heelY_list, 
                    s = [2 for i in range(len(heelY_list))])

    axs[1,0].scatter(gait_jointdata["gait_cycle"][waveform], heelX_list, 
                    c = ["#808080" for i in range(len(heelX_list))],
                    s = [2 for i in range(len(heelX_list))])
    axs[1,1].scatter(gait_jointdata["gait_cycle"][waveform], heelY_list, 
                    c = ["#808080" for i in range(len(heelY_list))],
                    s = [2 for i in range(len(heelY_list))])
    axs[1,2].scatter(gait_jointdata["gait_cycle"][waveform], heelZ_list, 
                    c = ["#808080" for i in range(len(heelZ_list))],
                    s = [2 for i in range(len(heelZ_list))])

    axs[2,0].scatter(gait_jointdata["gait_cycle"][waveform], hipflex_list, 
                    c = ["#808080" for i in range(len(hipflex_list))],
                    s = [2 for i in range(len(hipflex_list))])
    axs[2,1].scatter(gait_jointdata["gait_cycle"][waveform], kneeflex_list, 
                    c = ["#808080" for i in range(len(kneeflex_list))],
                    s = [2 for i in range(len(kneeflex_list))])
    axs[2,2].scatter(gait_jointdata["gait_cycle"][waveform], ankleflex_list, 
                    c = ["#808080" for i in range(len(ankleflex_list))],
                    s = [2 for i in range(len(ankleflex_list))])

axs[1,0].plot(polyfit_heelX_x, polyfit_heelX_y,"r")
axs[1,1].plot(polyfit_heelY_x, polyfit_heelY_y,"r")
axs[1,2].plot(polyfit_heelZ_x, polyfit_heelZ_y,"r")

axs[2,0].plot(polyfit_hip_x, polyfit_hip_y,"r")
axs[2,1].plot(polyfit_knee_x, polyfit_knee_y,"r")
axs[2,2].plot(polyfit_ankle_x, polyfit_ankle_y,"r")

axs[0,0].set_title("Raw Data")
axs[0,1].set_title("Segregation of Gait Cycle")
axs[0,2].set_title("Scatterplot of Raw Data of Gait Cycles")

axs[1,0].set_title("Best Fit Curve of X Movement of Heel")
axs[1,1].set_title("Best Fit Curve of Y Movement of Heel")
axs[1,2].set_title("Best Fit Curve of Z Movement of Heel")

axs[2,0].set_title("Best Fit Curve of Hip Flex")
axs[2,1].set_title("Best Fit Curve of Knee Flex")
axs[2,2].set_title("Best Fit Curve of Ankle Flex")
 
plt.show()

###################################################################################################

cap.release() # Release camera
cv2.destroyAllWindows() # Destroy all cv2 windows
