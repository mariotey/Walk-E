import time
import cv2
import mediapipe as mp
import matplotlib.pyplot as plt

import dist
import gaitAnalysis

HEEL_DOF = 6
HIPFLEX_DOF = 6
KNEEFLEX_DOF = 12
ANKLEFLEX_DOF = 10

# Drawing utilities for visualizing poses
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose  # Pose Estimation Model

joint_data = {
    "ref_heel": [],
    "shoulder": [],
    "hip": [],
    "knee": [],
    "ankle": [],
    "toe": [],
    "time": []
}

# Get Realtime Webcam Feed
cap = cv2.VideoCapture(1)  # Get Video Capture Device

with mp_pose.Pose(  # Setting up Pose Estimation Model
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        enable_segmentation=True,
        smooth_segmentation=True,
        smooth_landmarks=True,
        static_image_mode=False) as pose:

    start_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read()  # Reads feed from Webcam

        # Recolour Image feed (from openCV) from BGR to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Save memory by setting writeable attribute as false; improves performance
        image.flags.writeable = False

        # Pass recoloured image feed to Pose Estimation model for processing
        results = pose.process(image)

        image.flags.writeable = True
        # Recolour Image back to BGR for openCV to process, Make Detection
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Draw Pose Estimation landmarks
        mp_drawing.draw_landmarks(image,
                                  results.pose_landmarks,
                                  mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(245, 117, 66),
                                                         thickness=2,
                                                         circle_radius=2),
                                  mp_drawing.DrawingSpec(color=(245, 66, 230),
                                                         thickness=2,
                                                         circle_radius=2))

        # Extract landmarks
        try:
            camera_landmarks = results.pose_landmarks.landmark
            world_landmarks = results.pose_world_landmarks.landmark

            joint_data["ref_heel"].append(gaitAnalysis.get_body_lm(
                "LEFT_HEEL", world_landmarks))  # Heel Reference
            joint_data["shoulder"].append(gaitAnalysis.get_body_lm(
                "LEFT_SHOULDER", world_landmarks))  # Shoulder Info
            joint_data["hip"].append(gaitAnalysis.get_body_lm(
                "LEFT_HIP", world_landmarks))  # Hip Info
            joint_data["knee"].append(gaitAnalysis.get_body_lm(
                "LEFT_KNEE", world_landmarks))  # Knee Info
            joint_data["ankle"].append(gaitAnalysis.get_body_lm(
                "LEFT_ANKLE", world_landmarks))  # Ankle Info
            joint_data["toe"].append(gaitAnalysis.get_body_lm(
                "LEFT_FOOT_INDEX", world_landmarks))  # Toe Info
            joint_data["time"].append(time.time() - start_time)  # Time Info

            dist.detect(image, camera_landmarks)

        except AttributeError:
            # print("Nothing / Errors detected")
            pass  # Pass if there is no detection or error

        cv2.imshow("Mediapipe Feed", image)  # Render image result on screen

        # If keyboard "q" is hit after 0.01 sec, break from while loop
        if cv2.waitKey(10) & 0xFF == ord("q"):
            break

gait_jointdata = gaitAnalysis.get_gait(0.80, joint_data)

hipflex_data = gaitAnalysis.get_flex(gait_jointdata, "shoulder", "hip", "knee")
kneeflex_data = gaitAnalysis.get_flex(gait_jointdata, "hip", "knee", "ankle")
ankleflex_data = gaitAnalysis.get_flex(gait_jointdata, "knee", "ref_heel", "toe")

heelX_x, heelX_y, heelX_polyfit = gaitAnalysis.polyfit_heel(gait_jointdata, "x", 
                                                            HEEL_DOF)
heelY_x, heelY_y, heelY_polyfit = gaitAnalysis.polyfit_heel(gait_jointdata, "y", 
                                                            HEEL_DOF)
heelZ_x, heelZ_y, heelZ_polyfit = gaitAnalysis.polyfit_heel(gait_jointdata, "z", 
                                                            HEEL_DOF)
hipflex_x, hipflex_y, hipflex_polyfit = gaitAnalysis.polyfit_flex(hipflex_data, 
                                                                HIPFLEX_DOF)
kneeflex_x, kneeflex_y, kneeflex_polyfit = gaitAnalysis.polyfit_flex(kneeflex_data, 
                                                                KNEEFLEX_DOF)
ankleflex_x, ankleflex_y, ankleflex_polyfit = gaitAnalysis.polyfit_flex(ankleflex_data, 
                                                                    ANKLEFLEX_DOF)

###################################################################################################
fig, axs = plt.subplots(3, 3, constrained_layout = True)

ref_list = []
for elem in joint_data["ref_heel"]:
    ref_list.append(elem["y"])

axs[0, 0].plot(joint_data["time"], ref_list)
axs[0, 0].set(xlabel = "time (sec)", ylabel = "y-coordinate of heel",
            title = "Raw Data of Heel")

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

axs[2, 0].plot(hipflex_x, hipflex_y, "r")
axs[2, 0].set(xlabel="Gait Cycle", ylabel = "Hip Flex (Degree)",
            title = "Best Fit Curve of Hip Flex")

axs[2, 1].plot(kneeflex_x, kneeflex_y, "r")
axs[2, 1].set(xlabel="Gait Cycle", ylabel = "Knee Flex (Degree)",
            title = "Best Fit Curve of Knee Flex")

axs[2, 2].plot(ankleflex_x, ankleflex_y, "r")
axs[2, 2].set(xlabel="Gait Cycle", ylabel = "Ankle Flex (Degree)",
            title = "Best Fit Curve of Ankle Flex")

plt.show()

###################################################################################################

cap.release()  # Release camera
cv2.destroyAllWindows()  # Destroy all cv2 windows

#.\venv\Scripts\python.exe -m pylint .\Walk-E\main_mediapipe.py