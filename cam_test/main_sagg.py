import cv2
import mediapipe as mp
import time

import lm_identify as lm_i
import gaitAnalysis_sagg as ga
import cam_plot
import cam_dict

WAIT_TIME = 5

record_flag = False
calibrate_flag = False

# Drawing utilities for visualizing poses
mp_drawing = mp.solutions.drawing_utils

# Pose Estimation Model
mp_pose = mp.solutions.pose  

joint_data = {item: [] for item in cam_dict.gaitkeys_list}
calibrate_data = {item: [] for item in cam_dict.gaitkeys_list}

# Get Realtime Webcam Feed from Video Capture Device
cap = cv2.VideoCapture(1)  
        
#################################################################################################

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
                                mp_drawing.DrawingSpec(color=(245, 66, 230),
                                                        thickness=0,
                                                        circle_radius=0),
                                mp_drawing.DrawingSpec(color=(245, 66, 230),
                                                        thickness=2,
                                                        circle_radius=0)
                                )

        try:
            camera_lm = results.pose_landmarks.landmark
            world_lm = results.pose_world_landmarks.landmark

            lm_i.gait_logic(image, camera_lm, world_lm)

            if record_flag == True:
                ga.get_lm(joint_data, world_lm, start_time)

            if calibrate_flag == True:
                ga.get_lm(calibrate_data, world_lm, start_time)

        except AttributeError:
            # print("Nothing / Errors detected")
            pass  # Pass if there is no detection or error   
         
        cv2.imshow("Mediapipe Feed", image)  # Render image result on screen

        # TBC when integrated with Walk-E
        if cv2.waitKey(WAIT_TIME) & 0xFF == ord("q"):
            break
        elif cv2.waitKey(WAIT_TIME) & 0xFF == ord("r"):
            print("Recording...")
            record_flag = True
            calibrate_flag = False
        elif cv2.waitKey(WAIT_TIME) & 0xFF == ord("c"):
            print("Calibrating...")
            record_flag = False
            calibrate_flag = True
        elif cv2.waitKey(WAIT_TIME) & 0xFF == ord("s"):
            print("Stopping...")
            record_flag = False
            calibrate_flag = False
        else:
            pass

offsetdata = ga.calibrate(calibrate_data)
gait_data = ga.get_gait(offsetdata["cut_off"], joint_data)
stats_data = ga.stats(joint_data, gait_data, offsetdata)

cam_plot.left_heel(joint_data)
cam_plot.stats(stats_data)

print("Complete")

###################################################################################################

cap.release()  # Release camera
cv2.destroyAllWindows()  # Destroy all cv2 windows

#.\venv\Scripts\python.exe -m pylint .\Walk-E\main_mediapipe.py