import cv2
import mediapipe as mp
from flask import Flask, render_template, Response, request, stream_template
import time
import json
import gaitAnalysis as ga
# import motor

# Drawing utilities for visualizing poses
mp_drawing = mp.solutions.drawing_utils
# Pose Estimation Model
mp_pose = mp.solutions.pose 

app = Flask(__name__)
camera = cv2.VideoCapture(0)

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

render_data = {
    "ref_heel": [],
    "shoulder": [],
    "hip": [],
    "knee": [],
    "ankle": [],
    "toe": [],
    "time": []
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

        ret, buffer = cv2.imencode('.jpeg', frame)    
        frame = buffer.tobytes()

        # "return" will only return one image
        yield (b'--frame\r\n' 
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def landmark_stream(template_name, **context):    
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    return rv

#################################################################################################

@app.route('/')
def index():
    def landmark_stream():
        start_time = time.time()

        while True:
            # Read camera frame
            ret, frame = camera.read()

            if not ret:
                break
            else:
                frame, results = mediapipe_draw(frame)
                camera_lm, world_lm = get_landmark(frame)

                ga.get_lm(render_data, world_lm, start_time)

                yield_data = json.dumps(render_data)
                yield yield_data

    return Response(stream_template('scatterplot.html', data=landmark_stream()))
    
@app.route('/video')
def video():
    res_obg = Response(video_stream(), 
                mimetype='multipart/x-mixed-replace; boundary=frame')
    return res_obg

#################################################################################################

@app.route('/move', methods=["POST", "GET"])
def start():
    request_data = request.form

    if request_data["data"] == 'true':
        # motor.drive(10, 99.9, 100)
        print("Walk-E has moved.")
    else:
        # motor.stop()
        print("Walk-E stopped.")

    return render_template('main.html')

#################################################################################################

if __name__ == "__main__":
    app.run(port='5000', debug=False)

# def landmark_stream():
#         while True:
#             # Read camera frame
#             ret, frame = camera.read()

#             if not ret:
#                 break
#             else:
#                 frame, results = mediapipe_draw(frame)
#                 camera_lm, world_lm = get_landmark(frame)

#                 yield '{"camera_lm": [' + camera_lm + '], "world_lm": [' + world_lm + ']}'                    