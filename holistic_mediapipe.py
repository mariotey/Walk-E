import mediapipe as mp
import cv2
import logging

logging.basicConfig(level=logging.DEBUG)

mp_drawing = mp.solutions.drawing_utils # Drawing utilities for various detections of holistic model to openCV
mp_holistic = mp.solutions.holistic # Holistic Model

# Get Realtime Webcam Feed
cap = cv2.VideoCapture(1) # Get Video Capture Device

with mp_holistic.Holistic( #Setting up Holistic Model
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as holistic:

    while cap.isOpened():
        ret, frame = cap.read() # Reads feed from Webcam
        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Recolour Image feed (from openCV) from BGR to RGB
        results = holistic.process(image) # Pass recoloured image feed to Holistic Model for processing
        # print(results.pose_landmarks) # face_landmarks, pose_landmarks, left_hand_landmarks, right_hand_landmarks
        
        image =cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # Recolour Image back to BGR for openCV to process

        # Draw face landmarks
        # mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS) 
        
        # Draw right hand landmarks
        mp_drawing.draw_landmarks(image, 
                        results.right_hand_landmarks, 
                        mp_holistic.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(255,0,0),thickness=1,circle_radius=5),
                        mp_drawing.DrawingSpec(color=(0,0,255),thickness=2,circle_radius=2)) 

        # Draw left hand landmarks
        mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS) 

        # Draw pose detection landmarks
        # mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS) 

        cv2.imshow("Holistic Model Detection", image) # Render image result on screen

        # If keyboard "q" is hit after 0.01 sec, break from while loop
        if cv2.waitKey(10) & 0xFF == ord("q"): 
            break

cap.release() # Release camera
cv2.destroyAllWindows() # Destroy all cv2 windows