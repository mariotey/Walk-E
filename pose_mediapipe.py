import cv2
import mediapipe as mp
import numpy as np
import logging

logging.basicConfig(level=logging.DEBUG)

mp_drawing = mp.solutions.drawing_utils # Drawing utilities for visualizing poses
mp_pose = mp.solutions.pose # Pose Estimation Model

# Curl Counter Variables
counter = 0 # Bicep Curl Count
stage = None # Whether Curl is up or down

def calculateAngle(a,b,c):
    a = np.array(a) # First 
    b = np.array(b) # Mid
    c = np.array(c) # End

    radians = np.arctan2(c[1] - b[1], c[0]-b[0]) - np.arctan2(a[1] - b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0/np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

# Get Realtime Webcam Feed
cap = cv2.VideoCapture(1) # Get Video Capture Device

with mp_pose.Pose( #Setting up Pose Estimation Model
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as pose:

    while cap.isOpened():
        ret, frame = cap.read() # Reads feed from Webcam

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Recolour Image feed (from openCV) from BGR to RGB
        image.flags.writeable = False # Save memory by setting writeable attribute as false; improves performance

        results = pose.process(image) # Pass recoloured image feed to Pose Estimation model for processing

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # Recolour Image back to BGR for openCV to process, Make Detection

        # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark # Hold actual landmark results

            # Get Coordinates
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

            # Calculate Angle
            angle = calculateAngle(shoulder, elbow, wrist)

            # Visualization
            cv2.putText(image, str(angle),
                tuple(np.multiply(elbow, [640, 480]).astype(int)), # [640, 480] is resolution dimension of WebCam used
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Curl Count Logic
            if angle > 160:
                stage = "down"
            
            if angle < 30 and stage == "down":
                stage = "up"
                counter = counter + 1
                print("Curl Count:", counter)

        except Exception:
            # print("Nothing / Errors detected")
            pass # Pass if there is no detection or error

        # Curl Counter Status Box
        cv2.rectangle(image, (0,0), (225, 73), (245,117,16), -1)
        cv2.putText(image, "REPS: ", (15,12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(image, str(counter), (10,60),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        cv2.putText(image, "STAGE: ", (105,12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(image, stage, (100,60),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)

        # Draw Pose Estimation landmarks
        mp_drawing.draw_landmarks(image, 
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2),)

        cv2.imshow("Mediapipe Feed", image) # Render image result on screen

        # If keyboard "q" is hit after 0.01 sec, break from while loop
        if cv2.waitKey(10) & 0xFF == ord("q"): 
            break

cap.release() # Release camera
cv2.destroyAllWindows() # Destroy all cv2 windows