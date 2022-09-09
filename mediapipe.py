import cv2
import mediapipe as mp
import matplotlib.pyplot as plt
import time

import dist
import gaitAnalysis
import gaitAnalysis_new

mp_drawing = mp.solutions.drawing_utils # Drawing utilities for visualizing poses
mp_pose = mp.solutions.pose # Pose Estimation Model 

heel_left_x = []
heel_left_y = []
heel_left_z = []

joint_data = {
    "heel_left_x": [],
    "heel_left_y": [],
    "heel_left_z": [],
    "time": []
}

# joint_data = {
#     "pelvicRotate_right": [],
#     "pelvicRotate_left": [],
#     "pelvicOblique": [],
#     "shoulderRotate_right": [],
#     "shoulderRotate_left": [],
#     "shoulderOblique": [],
#     "hipFlex_right": [],
#     "hipFlex_left": [],
#     "kneeFlex_right": [], 
#     "kneeFlex_left": [], 
#     "ankleFlex_right": [],
#     "ankleFlex_left": [],
#     "time": []
# }

# Get Realtime Webcam Feed
cap = cv2.VideoCapture(1) # Get Video Capture Device

with mp_pose.Pose( #Setting up Pose Estimation Model
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    enable_segmentation=True,
    smooth_segmentation=True,
    smooth_landmarks=True) as pose:

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

            heel_x, heel_y, heel_z = gaitAnalysis_new.get_heel_data(image, camera_landmarks, world_landmarks)

            heel_left_x.append(heel_x)
            heel_left_y.append(heel_y)
            heel_left_z.append(heel_z)

            # hip_flex = gaitAnalysis_new.hipFlex(world_landmarks)
            # knee_flex = gaitAnalysis_new.kneeFlex(world_landmarks)
            # ankle_flex = gaitAnalysis_new.ankleFlex(world_landmarks)
            
            # pelvRot_right, pelvRot_left = gaitAnalysis.pelvicRotate(image, camera_landmarks, world_landmarks)
            # joint_data["pelvicRotate_right"].append(pelvRot_right)
            # joint_data["pelvicRotate_left"].append(pelvRot_left)

            # shldRot_right, shld_left = gaitAnalysis.shoulderRotate(image, camera_landmarks, world_landmarks)
            # joint_data["shoulderRotate_right"].append(shldRot_right)
            # joint_data["shoulderRotate_left"].append(shld_left)

            # joint_data["pelvicOblique"].append(gaitAnalysis.pelvicOblique(image, camera_landmarks, world_landmarks))
            # joint_data["shoulderOblique"].append(gaitAnalysis.shoulderOblique(image, camera_landmarks, world_landmarks))         

            # hipflex_right, hipflex_left = gaitAnalysis.hipFlex(image, camera_landmarks, world_landmarks)
            # joint_data["hipFlex_right"].append(hipflex_right)
            # joint_data["hipFlex_left"].append(hipflex_left)

            # kneeflex_right, kneeflex_left = gaitAnalysis.kneeFlex(image, camera_landmarks, world_landmarks)
            # joint_data["kneeFlex_right"].append(kneeflex_right)
            # joint_data["kneeFlex_left"].append(kneeflex_left)

            # ankleflex_right, ankleflex_left = gaitAnalysis.ankleFlex(image, camera_landmarks, world_landmarks)
            # joint_data["ankleFlex_right"].append(ankleflex_right)
            # joint_data["ankleFlex_left"].append(ankleflex_left)

            joint_data["time"].append(time.time() - start_time)
           
            dist.detect(image, camera_landmarks)           
            
        except:
            # print("Nothing / Errors detected")
            pass # Pass if there is no detection or error
        
        cv2.imshow("Mediapipe Feed", image) # Render image result on screen

        # If keyboard "q" is hit after 0.01 sec, break from while loop
        if cv2.waitKey(10) & 0xFF == ord("q"): 
            break

# format_heel, format_time = gaitAnalysis_new.modify_raw(heel_left_y, joint_data["time"], 2000)
format_heel, format_time = gaitAnalysis_new.get_gaitcycle_data(0.77, heel_left_y, joint_data["time"])

plt.figure(1)
plt.subplot(211)

for i in range(len(format_heel)):
   plt.plot(format_time[i], format_heel[i])

# for i in range(len(format_heel)):
#     if max(format_heel[i]) > 0.77:
#         try:
#             plt.plot(format_time[i] + format_time[i + 1], format_heel[i] + format_heel[i+1])
#         except:
#             plt.plot(format_time[i], format_heel[i])
#         print(i)
            
# plt.plot(joint_data["time"],joint_data["pelvicRotate_right"])
# plt.plot(joint_data["time"],joint_data["shoulderRotate_right"])
# plt.plot(joint_data["time"],joint_data["pelvicOblique"])
# plt.plot(joint_data["time"],joint_data["shoulderOblique"])
# plt.plot(joint_data["time"],joint_data["hipFlex_right"])
# plt.plot(joint_data["time"],joint_data["kneeFlex_right"])
# plt.plot(joint_data["time"],joint_data["ankleFlex_right"])
# plt.plot(joint_data["time"],heel_left_y)
# plt.plot(joint_data["time"],heel_left_x)
# plt.plot(joint_data["time"],heel_left_z)  

plt.subplot(212)
plt.plot(joint_data["time"],heel_left_y)

plt.show()

cap.release() # Release camera
cv2.destroyAllWindows() # Destroy all cv2 windows



# Create function that sets baseline results for normality
# Make a Gait Cycle Counter
# Import Time and get list of landmark data and time
# Create real-time graph plotting
# Create Python Flask