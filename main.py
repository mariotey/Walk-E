import cv2
import mediapipe as mp
from flask import Flask, render_template, Response, stream_with_context, request
import time
import motor

# Drawing utilities for visualizing poses
mp_drawing = mp.solutions.drawing_utils
# Pose Estimation Model
mp_pose = mp.solutions.pose 

camera = cv2.VideoCapture(0)
app = Flask("__name__")

def video_stream():    
    while True:
        # Setting up Pose Estimation Model
        with mp_pose.Pose(min_detection_confidence=0.5,
                        min_tracking_confidence=0.5,
                        enable_segmentation=False,
                        smooth_segmentation=True,
                        smooth_landmarks=True,
                        static_image_mode=False) as pose:
        
            # Read camera frame
            ret, frame = camera.read()
            if not ret:
                ret, buffer = cv2.imencode('.jpeg', frame)
            else:
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

                ret, buffer = cv2.imencode('.jpeg', image)
                
            frame = buffer.tobytes()
            # "return" will only return one image
            yield (b'--frame\r\n' 
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/video')
def video():
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

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

app.run(port='5000', debug=False)


                    