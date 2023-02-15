from flask import Flask, render_template, request
import time
import mediapipe as mp
import cv2

import rediscache
import gait_statistics
import gait_process
import hardware
import walkE_dict

calibration_hiplen = []

encoder_list = hardware.encoder_init()

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
        calibration_hiplen.append(hardware.hip_detect(camera_lm))        

    except AttributeError:
        pass  # Pass if there is no detection or error 

    return ('', 204)

@app.route('/CacheCalibrate', methods=["GET", "POST"])
def cache_calibrate():
    request_data = request.form
    rediscache.cache_lm("calibration_data", request_data)

    return render_template("main.html")

#################################################################################################

@app.route('/walkE_move', methods=["GET", "POST"])
def walkE_move():  
    ret, frame = cap.read()
    results = pose.process(frame)

    try:
        # camera_lm = results.pose_landmarks.landmark
        # dist_status = hardware.proxy_detect(frame, camera_lm)
        # hardware.motor_drive(*walkE_dict.proxy_status[dist_status])

        hardware.motor_drive(*[25,25])
        
        encoder_list.append(hardware.encoder_stateChange(encoder_list[-1], "Nice"))

    except AttributeError:
        # Stops if user is not in frame
        hardware.motor_drive(*[0,0])

    return ('', 204)

@app.route('/walkE_stop', methods=["GET", "POST"])
def walkE_stop():
    hardware.motor_drive(*[0,0])
    hardware.encoder_process(encoder_list)
    
    return('', 204)

@app.route('/CacheStats', methods=["GET", "POST"])
def cache_stats():  
    request_data = request.form   
    rediscache.cache_lm("testjoint_data", request_data)   
    
    return render_template("main.html")

#################################################################################################

@app.route('/GetStats', methods=["GET", "POST"])
def plot_stats():
    # Retrieve calibration and stats data from server 
    joint_data = rediscache.request_lm("testjoint_data")

    if joint_data == []:
        return render_template("main.html")
    
    offsetdata = rediscache.request_lm("calibration_data")

    hardware_data = rediscache.request_hw("testjoint_data")
        
    # Calculation of Gait Statistics
    gait_data = gait_process.get_gait(offsetdata["cut_off"], joint_data)
    stats_data = gait_statistics.stats(joint_data, gait_data, hardware_data, offsetdata)

    return render_template("statistics.html", stats_Info = stats_data)

#################################################################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context='adhoc')
