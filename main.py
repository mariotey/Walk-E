import cv2
import mediapipe as mp
from flask import Flask, render_template, Response, request
from time import sleep
import json

import gaitAnalysis as ga
import motor
import pose_coord

# Drawing utilities for visualizing poses
mp_drawing = mp.solutions.drawing_utils
# Pose Estimation Model
mp_pose = mp.solutions.pose 

camera = cv2.VideoCapture(0)

app = Flask(__name__)

pose_data = {}

# Setting up Pose Estimation Model
pose =  mp_pose.Pose(min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
                enable_segmentation=False,
                smooth_segmentation=True,
                smooth_landmarks=True,
                static_image_mode=False)

#################################################################################################

def mediapipe_draw(frame):
    try:
        # Pass image feed to Pose Estimation model for processing
        results = pose.process(frame)
        
        # Draw Pose Estimation landmarks                                       
        mp_drawing.draw_landmarks(frame,
                                results.pose_landmarks,
                                mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245, 66, 230),
                                                        thickness=0,
                                                        circle_radius=0),
                                mp_drawing.DrawingSpec(color=(245, 66, 230),
                                                        thickness=2,
                                                        circle_radius=0)
                                )   
    except AttributeError:
        # print("Nothing / Errors detected")
        pass  # Pass if there is no detection or error  

    return frame

def get_landmark(frame):
    # Pass image feed to Pose Estimation model for processing
    results = pose.process(frame)

    try:
        # camera_lm = results.pose_landmarks.landmark
        world_lm = results.pose_world_landmarks.landmark
        
        return pose_coord.append_lm(world_lm)
        
    except AttributeError:
        # print("Nothing / Errors detected")
        pass  # Pass if there is no detection or error  

#################################################################################################

def video_stream():    
    while True:
        # Read camera frame
        ret, frame = camera.read()

        if not ret:
            break
        else:
            frame = mediapipe_draw(frame)

            ret, buffer = cv2.imencode('.jpeg', frame)    
            frame = buffer.tobytes()

        # "return" will only return one image
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
#################################################################################################

@app.route('/')
def index():   
    return render_template("main.html")
    # return Response(stream_template('scatterplot.html', data=landmark_stream()))
    
@app.route('/video')
def video():
    return Response(video_stream(), 
                mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/streamdata")
def streamdata():           
    def generate():
        while True:
            # Read camera frame
            ret, frame = camera.read()

            if not ret:
                break
            else:
                pose_data = get_landmark(frame)

                yield json.dumps(pose_data) + "\n"
                sleep(1)

    return app.response_class(generate(),  mimetype="application/json")

#################################################################################################

@app.route('/move', methods=["POST", "GET"])
def start():
    request_data = request.form

    if request_data["data"] == 'true':
        motor.drive(10, 99.9, 100)
        print("Walk-E has moved.")
    else:
        motor.stop()
        print("Walk-E stopped.")

    return render_template('main.html')

#################################################################################################

if __name__ == "__main__":
    app.run(port='5000', debug=False)
             