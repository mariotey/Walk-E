from flask import Flask, render_template, request
import numpy as np
import mediapipe as mp
import cv2

import walkE_cache
import gait_statistics
import gait_process
# import hardware
import walkE_dict

calibration_hiplen = []

#################################################################################################

# Pose Estimation Model
mp_pose = mp.solutions.pose  
pose = mp.solutions.pose.Pose(min_detection_confidence=0.5,
                    min_tracking_confidence=0.5,
                    enable_segmentation=True,
                    smooth_segmentation=True,
                    smooth_landmarks=True,
                    static_image_mode=False)

# Get Realtime Webcam Feed
cap = cv2.VideoCapture(0) 

app = Flask(__name__)

#################################################################################################

@app.route('/')
def home():
    return render_template("main.html")

#################################################################################################
@app.route('/calibrate_hiplen', methods =["GET", "POST"])
def calibrate_hiplen():
    ret, frame = cap.read()
    results = pose.process(frame)

    try:
        camera_lm = results.pose_landmarks.landmark   

    except AttributeError:
        pass  # Pass if there is no detection or error 

    return ('', 204)

@app.route('/CacheCalibrate', methods=["GET", "POST"])
def cache_calibrate():
    request_data = request.form

    walkE_cache.cache_lm("calibration_data", request_data)

    return render_template("main.html")

#################################################################################################

@app.route('/walkE_move', methods=["GET", "POST"])
def walkE_move():  
    ret, frame = cap.read()
    results = pose.process(frame)

    if calibration_hiplen:
        avg_hiplen = np.mean(calibration_hiplen)
    else:
        avg_hiplen = 0.015

    try:
        camera_lm = results.pose_landmarks.landmark
    except AttributeError:
        pass

    return ('', 204)

@app.route('/walkE_stop', methods=["GET", "POST"])
def walkE_stop():
    return('', 204)

@app.route('/CacheStats', methods=["GET", "POST"])
def cache_stats():  
    request_data = request.form   
    walkE_cache.cache_lm("testjoint_data", request_data)   
    
    return render_template("main.html")

#################################################################################################

@app.route('/GetStats', methods=["GET", "POST"])
def plot_stats():
    # Retrieve calibration and stats data from server 
    joint_data = walkE_cache.request_lm("testjoint_data")

    if joint_data == []:
        return render_template("main.html")
    
    offsetdata = walkE_cache.request_lm("calibration_data")

    hardware_data = walkE_cache.request_hw("testjoint_data")
        
    # Calculation of Gait Statistics
    gait_data = gait_process.get_gait(offsetdata["cut_off"], joint_data)
    stats_data = gait_statistics.stats(joint_data, gait_data, hardware_data, offsetdata)

    return render_template("statistics.html", stats_Info = stats_data)

#################################################################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context='adhoc')