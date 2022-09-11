import cv2
import mediapipe as mp
import matplotlib.pyplot as plt
import time

import dist
import gaitAnalysis_new

HEEL_DOF = 7

mp_drawing = mp.solutions.drawing_utils # Drawing utilities for visualizing poses
mp_pose = mp.solutions.pose # Pose Estimation Model 

joint_data = {
    "ref_heel": [],
    "shoulder": [],
    "hip": [],
    "knee": [],
    "ankle": [],
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

            # Heel Reference Info
            heel_x, heel_y, heel_z = gaitAnalysis_new.get_bodypart_landmarks("LEFT_HEEL", world_landmarks)
            joint_data["ref_heel"].append(gaitAnalysis_new.append_bodypart_landmarks(heel_x, heel_y, heel_z))

            # Shoulder Info
            shoulder_x, shoulder_y, shoulder_z = gaitAnalysis_new.get_bodypart_landmarks("LEFT_SHOULDER", world_landmarks)
            joint_data["shoulder"].append(gaitAnalysis_new.append_bodypart_landmarks(shoulder_x, shoulder_y, shoulder_z))

            # Hip Info
            hip_x, hip_y, hip_z = gaitAnalysis_new.get_bodypart_landmarks("LEFT_HIP", world_landmarks)
            joint_data["hip"].append(gaitAnalysis_new.append_bodypart_landmarks(hip_x, hip_y, hip_z))

            # Knee Info
            knee_x, knee_y, knee_z = gaitAnalysis_new.get_bodypart_landmarks("LEFT_KNEE", world_landmarks)
            joint_data["knee"].append(gaitAnalysis_new.append_bodypart_landmarks(knee_x, knee_y, knee_z))

            # Ankle Info
            ankle_x, ankle_y, ankle_z = gaitAnalysis_new.get_bodypart_landmarks("LEFT_ANKLE", world_landmarks)
            joint_data["ankle"].append(gaitAnalysis_new.append_bodypart_landmarks(ankle_x, ankle_y, ankle_z))

            # Time Info
            joint_data["time"].append(time.time() - start_time)
           
            dist.detect(image, camera_landmarks)           
            
        except:
            # print("Nothing / Errors detected")
            pass # Pass if there is no detection or error
        
        cv2.imshow("Mediapipe Feed", image) # Render image result on screen

        # If keyboard "q" is hit after 0.01 sec, break from while loop
        if cv2.waitKey(10) & 0xFF == ord("q"): 
            break

format_jointdata = gaitAnalysis_new.get_raw_cycle(0.80, joint_data)
gait_jointdata = gaitAnalysis_new.get_gait_cycle(format_jointdata)
polyfit_x, polyfit_y, polyfit_curve = gaitAnalysis_new.polyfit_curve(gait_jointdata, HEEL_DOF)

###################################################################################################
fig, axs = plt.subplots(2,2, figsize=(4, 4), constrained_layout=True)

heel_list = []
for elem in joint_data["ref_heel"]:
    heel_list.append(elem["y"])
axs[0,0].plot(joint_data["time"], heel_list)

for waveform in range(len(gait_jointdata["ref_heel"])):
    ref_list = []
    for data_point in gait_jointdata["ref_heel"][waveform]:
        ref_list.append(data_point["y"])
    axs[0,1].plot(gait_jointdata["time"][waveform], ref_list)
    axs[1,0].scatter(gait_jointdata["gait_cycle"][waveform], ref_list, 
                    s = [2 for i in range(len(ref_list))])
    axs[1,1].scatter(gait_jointdata["gait_cycle"][waveform], ref_list, 
                    c = ["#808080" for i in range(len(ref_list))],
                    s = [2 for i in range(len(ref_list))])

axs[1,1].plot(polyfit_x, polyfit_y,"r")

axs[0,0].set_title("Raw Data")
axs[0,1].set_title("Segregation of Gait Cycle")
axs[1,0].set_title("Scatterplot of Raw Data of Gait Cycles")
axs[1,1].set_title("Best Fit Curve of Gait Cycle")
 
plt.show()

###################################################################################################

cap.release() # Release camera
cv2.destroyAllWindows() # Destroy all cv2 windows

# Create function that sets baseline results for normality
# Create Python Flask