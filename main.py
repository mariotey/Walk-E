from flask import Flask, render_template, request
import time
# import RPi.GPIO as GPIO
import mediapipe as mp
import cv2

import rediscache
import gait_statistics
import gait_process
# import hardware

# OP_ENCODE_ONE = 11 #GPIO 17
# OP_ENCODE_TWO = 36 #GPIO 16

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

calibration_hiplen = []
# stateCount_one, stateCount_two = 0, 0
# stateLast_one, stateLast_two = GPIO.input(OP_ENCODE_ONE), GPIO.input(OP_ENCODE_TWO)  

#################################################################################################

@app.route('/')
def home():
    return render_template("main.html")

#################################################################################################
@app.route('/calibrate_hiplen', methods =["GET", "POST"])
def calibrate_hiplen():
    ret, frame = cap.read()
    results = pose.process(frame)

    # try:
    #     camera_lm = results.pose_landmarks.landmark
    #     calibration_hiplen.append(hardware.hip_detect(camera_lm))        

    # except AttributeError:
    #     # print("Nothing / Errors detected")
    #     pass  # Pass if there is no detection or error 

    return ('', 204)

@app.route('/CacheCalibrate', methods=["GET", "POST"])
def cache_calibrate():
    request_data = request.form
    rediscache.cache_lm("calibration_data", request_data)

    return render_template("main.html")

#################################################################################################

@app.route('/walkE_move', methods=["GET", "POST"])
def walkE_move():
    # stateCount_one, stateCount_two = 0, 0
    # stateLast_one, stateLast_two = GPIO.input(OP_ENCODE_ONE), GPIO.input(OP_ENCODE_TWO)
    
    # start_time = time.time()
    
    # ret, frame = cap.read()
    # results = pose.process(frame)

    # try:
    #     # camera_lm = results.pose_landmarks.landmark
    #     # dist_status = hardware.proxy_detect(frame, camera_lm)
        
    #     # hardware.motor_drive(*walkE_dict.proxy_status[dist_status])
    #     hardware.motor_drive(*[25,25])
                    
    #     # stateCount_one, stateLast_one = hardware.encoder_stateChange(OP_ENCODE_ONE, stateCount_one, stateLast_one)
    #     # stateCount_two, stateLast_two = hardware.encoder_stateChange(OP_ENCODE_TWO, stateCount_two, stateLast_two)
        
    # except AttributeError:
    #     # print("Nothing / Errors detected")
    #     pass  # Pass if there is no detection or error 

    # end_time = time.time()

    # print("Walk-E stops")

    # hardware.encoder_logic(stateCount_one, stateCount_two, end_time - start_time)

    return ('', 204)

@app.route('/walkE_stop', methods=["GET", "POST"])
def walkE_stop():
    # hardware.motor_drive(*[0,0])
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

    hardware_one_data = rediscache.request_hw("testjoint_data", "hardware_one")
    hardware_two_data = rediscache.request_hw("testjoint_data", "hardware_two")

    print(hardware_one_data, hardware_two_data)
        
    # Calculation of Gait Statistics
    gait_data = gait_process.get_gait(offsetdata["cut_off"], joint_data)
    stats_data = gait_statistics.stats(joint_data, gait_data, offsetdata)
    # stats_data = gait_statistics.stats(joint_data, gait_data, hardware_data, offsetdata)

    return render_template("statistics.html", stats_Info = stats_data)

#################################################################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context='adhoc')
