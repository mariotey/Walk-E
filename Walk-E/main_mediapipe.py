import time
import cv2
import mediapipe as mp

import dist
import gaitAnalysis as ga
import walkE_plot

CUT_OFF = 0.78
WAIT_TIME = 5

record_flag = False
calibrate_flag = False

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

calibrate_data = {
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
        try:
            camera_lm = results.pose_landmarks.landmark
            world_lm = results.pose_world_landmarks.landmark

            dist.detect(image, camera_lm)

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

# gait_data = ga.get_gait(CUT_OFF, joint_data)
walkE_plot.calibrate(calibrate_data)

# walkE_plot.stats_result(calibrate_data, gait_data)
# walkE_plot.stats_result(joint_data, gait_data)

###################################################################################################

cap.release()  # Release camera
cv2.destroyAllWindows()  # Destroy all cv2 windows

#.\venv\Scripts\python.exe -m pylint .\Walk-E\main_mediapipe.py