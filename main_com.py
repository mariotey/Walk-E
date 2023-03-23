from flask import Flask, render_template, request
import numpy as np
import mediapipe as mp
import cv2

import walkE_cache
import gait_statistics
import gait_process

DIST = 0.25/40 # Circumference of Wheel = 0.22m

def encode_process(encoder_data):
    print("Processing Encoder Data...")

    if encoder_data != "":
        def process_data(encode):
            max_count = max(encode["count"])

            endtime = encode["time"][encode["count"].index(max_count)]
            dist_x = DIST * max_count

            return encode["time"][0], endtime, dist_x

        inittime_one, endtime_one, dist_one = process_data(encoder_data["encoder_one"])
        inittime_two, endtime_two, dist_two = process_data(encoder_data["encoder_two"])

        init_time, end_time = min(inittime_one, inittime_two), max(endtime_one, endtime_two)

        stats = {"dist": (dist_one + dist_two)/2}
        stats["speed"] = stats["dist"]/(end_time - init_time) if end_time != init_time else "-" 
        
        print("Distance:", stats["dist"], "m")
        print("Speed:", stats["speed"], "m/s")

        print("Encoder Data Retrieved\n")

        return stats

    return {
        "dist":"-",
        "speed":"-"
    }

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
    try:
        ret, frame = cap.read()
        results = pose.process(frame)
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
    if calibration_hiplen:
        avg_hiplen = np.mean(calibration_hiplen)
    else:
        avg_hiplen = 0.015

    try:
        ret, frame = cap.read()
        results = pose.process(frame)
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

   # Retrieve Optical Encoder Data
    encoderdata = encode_process(walkE_cache.request_encode("testjoint_data"))
        
    # Calculation of Gait Statistics
    gait_data = gait_process.get_gait(offsetdata["cut_off"], joint_data)
    stats_data = gait_statistics.stats(joint_data, gait_data, encoderdata, offsetdata)

    return render_template("statistics.html", stats_Info = stats_data)

#################################################################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context='adhoc')
