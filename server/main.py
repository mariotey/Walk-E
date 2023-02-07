from flask import Flask, render_template, request
import mediapipe as mp
import cv2
import json
import redis

import gait_calibrate
import gait_statistics
import format_data
# import motor
import dist

# Drawing utilities for visualizing poses
mp_drawing = mp.solutions.drawing_utils

# Pose Estimation Model
mp_pose = mp.solutions.pose  

pose = mp_pose.Pose(min_detection_confidence=0.5,
                    min_tracking_confidence=0.5,
                    enable_segmentation=True,
                    smooth_segmentation=True,
                    smooth_landmarks=True,
                    static_image_mode=False)

# Get Realtime Webcam Feed
# cap = cv2.VideoCapture(0) 

app = Flask(__name__)

#################################################################################################

@app.route('/')
def home():
    return render_template("main.html")

#################################################################################################

@app.route('/Recalibrate', methods=["GET", "POST"])
def recalibrate():
    request_data = request.form

    # Cache new calibration data into server 
    redis_client = redis.Redis(host="localhost", port=6379)
    redis_client.hset("calibration_data", "pose_lm", request_data["poseLandmark"])
    redis_client.hset("calibration_data", "world_lm", request_data["worldLandmark"])
    redis_client.hset("calibration_data", "time", request_data["time"])

    return render_template("main.html")

#################################################################################################

@app.route('/GetStats', methods=["GET", "POST"])
def get_stats():  
    request_data = request.form   

    global move_stats
    
    if request_data["stats"] == "true": 
        move_stats = True
    else:
        move_stats = False
        
        # Cache joint_data into server
        redis_client = redis.Redis(host="localhost", port=6379)
        redis_client.hset("testjoint_data", "pose_lm", request_data["poseLandmark"])
        redis_client.hset("testjoint_data", "world_lm", request_data["worldLandmark"])
        redis_client.hset("testjoint_data", "time", request_data["time"])

        # Cache joint_data into server
        redis_client = redis.Redis(host="localhost", port=6379)
        redis_client.hset("testjoint_data", "pose_lm", request_data["poseLandmark"])
        redis_client.hset("testjoint_data", "world_lm", request_data["worldLandmark"])
        redis_client.hset("testjoint_data", "time", request_data["time"])

    # Logic for Proximity Detection
    # while move_stats: 
    #     ret, frame = cap.read()
    #     results = pose.process(frame)

    #     try:
    #         camera_lm = results.pose_landmarks.landmark
    #         dist.detect(frame, camera_lm)
    #         print("Walk-E moves")
    #         motor.drive(30, 30)
            
    #     except AttributeError:
    #         # print("Nothing / Errors detected")
    #         pass  # Pass if there is no detection or error   

    # # motor.stop()
    # print("Walk-E stops")
    
    return render_template("main.html")

#################################################################################################

@app.route('/PlotStats', methods=["GET", "POST"])
def plot_stats():
    redis_client = redis.Redis(host="localhost", port=6379)

    # Retrieve calibration data from server 
    # calibrate_pose_lm = json.loads(redis_client.hget("calibration_data", "pose_lm").decode("utf-8"))
    calibrate_world_lm = json.loads(redis_client.hget("calibration_data", "world_lm").decode("utf-8"))
    calibrate_time = json.loads(redis_client.hget("calibration_data", "time").decode("utf-8"))
    calibrate_data = format_data.request_lm(calibrate_world_lm, calibrate_time)

    # Retrieve stats data from server
    joint_world_lm = json.loads(redis_client.hget("testjoint_data", "world_lm").decode("utf-8"))
    joint_time = json.loads(redis_client.hget("testjoint_data", "time").decode("utf-8"))
    joint_data = format_data.request_lm(joint_world_lm, joint_time)   

    if joint_data == []:
        return render_template("main.html")

    # Calculation of Gait Statistics
    offsetdata = gait_calibrate.calibrate(calibrate_data)
    gait_data = gait_statistics.get_gait(offsetdata["cut_off"], joint_data)
    stats_data = gait_statistics.stats(joint_data, gait_data, offsetdata)

    return render_template("statistics.html", stats_Info = stats_data)

#################################################################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context='adhoc')
