from flask import Flask, render_template, request
import json
import redis

import gaitAnalysis as ga
import process_request as pro

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
    # redis_client.hset("calibration_data", "video_image", request_data["video_image"])

    return render_template("main.html")

#################################################################################################

@app.route('/GetStats', methods=["GET", "POST"])
def get_stats():
    request_data = request.form
    redis_client = redis.Redis(host="localhost", port=6379)

    print("\njoint_data\n")
    joint_pose_lm = json.loads(request_data["poseLandmark"])
    joint_world_lm = json.loads(request_data["worldLandmark"])
    joint_time = json.loads(request_data["time"])
    
    # Retrieve calibration data from server 
    print("\ncalibrate_data\n")
    calibrate_pose_lm = json.loads(redis_client.hget("calibration_data", "pose_lm").decode("utf-8"))
    calibrate_world_lm = json.loads(redis_client.hget("calibration_data", "world_lm").decode("utf-8"))
    calibrate_time = json.loads(redis_client.hget("calibration_data", "time").decode("utf-8"))
    
    joint_data = pro.format_data(joint_world_lm, joint_time)
    calibrate_data = pro.format_data(calibrate_world_lm, calibrate_time)
    
    # Calculation of Gait Statistics
    offsetdata = ga.calibrate(calibrate_data)
    gait_data = ga.get_gait(offsetdata["cut_off"], joint_data)
    stats_data = ga.stats(joint_data, gait_data, offsetdata)

    # Cache Statistics and Video Recording into Server with timestamp as key

    return render_template("main.html")

#################################################################################################

if __name__ == "__main__":
    app.run(port=5000, debug=False)
