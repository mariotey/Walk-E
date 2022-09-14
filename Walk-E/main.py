from datetime import datetime 
from flask import Flask, Response, render_template, request

import cv2
import mediapipe as mp
import gaitAnalysis

app = Flask(__name__)

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

cap = cv2.VideoCapture(0) # Get Video Capture Device

@app.route("/")
def main_page():
    """
    Renders the Main Page upon startup
    """
    return render_template("main.html", message="")

@app.route("/Start")
def start_page():
    """
    Renders the Statistics Page for Walk-E after recording is complete
    """

    with mp_pose.Pose( #Setting up Pose Estimation Model
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    enable_segmentation=True,
    smooth_segmentation=True,
    smooth_landmarks=True) as pose:

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
            
            try:
                camera_landmarks = results.pose_landmarks.landmark
                world_landmarks = results.pose_world_landmarks.landmark

                heel_x, heel_y, heel_z = gaitAnalysis.get_heel_data(image, camera_landmarks, world_landmarks)      
                
            except:
                # print("Nothing / Errors detected")
                pass # Pass if there is no detection or error

            cv2.imshow("Mediapipe Feed", image) # Render image result on screen

    return render_template("main.html", message="Recording...")

@app.route("/Stop")
def stop_page():
    """
    Renders the Statistics Page for Walk-E after recording is complete
    """
    cap.release() # Release camera
    cv2.destroyAllWindows() # Destroy all cv2 windows

    return render_template("main.html", message = "Recording has stopped")

@app.route("/Statistics")
def statistics_page():
    """
    Renders the Statistics Page for Walk-E after recording is complete
    """
    
    return "This page will render the statistics page"

if __name__ == "__main__":
    app.run(debug=True)

# .\venv\Scripts\python.exe -m pylint .\Walk-E\main.py