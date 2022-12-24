import cv2
import mediapipe as mp
from flask import Flask, render_template, Response, request, stream_with_context
from time import sleep
from math import sqrt
import json
import gaitAnalysis as ga
import motor

# Drawing utilities for visualizing poses
mp_drawing = mp.solutions.drawing_utils
# Pose Estimation Model
mp_pose = mp.solutions.pose 

camera = cv2.VideoCapture(0)

app = Flask(__name__)

pose_data = {
    "nose": [],
    "left_eye_inner": [],
    "left_eye": [],
    "left_eye_outer": [],
    "right_eye_inner": [],
    "right_eye": [],
    "right_eye_outer": [],
    "left_ear": [],
    "right_ear": [],
    "mouth_left": [],
    "mouth_right": [],
    "left_shoulder": [{"x": 23, "y": 50, "z": 60}]
}

# Setting up Pose Estimation Model
pose =  mp_pose.Pose(min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
                enable_segmentation=False,
                smooth_segmentation=True,
                smooth_landmarks=True,
                static_image_mode=False)

#################################################################################################

def mediapipe_draw(frame):
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
    return frame, results

def get_landmark(frame):
    # Pass image feed to Pose Estimation model for processing
    results = pose.process(frame)

    try:
        camera_lm = results.pose_landmarks.landmark
        world_lm = results.pose_world_landmarks.landmark

        return camera_lm, world_lm
        
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
            frame, results = mediapipe_draw(frame)
            # camera_lm, world_lm = get_landmark(frame)

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
        yield json.dumps(pose_data) + "\n"
        sleep(0.5)

    return Response(generate(),  mimetype="application/json")

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
             