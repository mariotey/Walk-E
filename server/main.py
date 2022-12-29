from flask import Flask, render_template, request
import json
import redis

import gait_calibrate
import gait_statistics
import format_data
import motor

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
    redis_client = redis.Redis(host="localhost", port=6379)

    # Cache joint_data into server
    # redis_client.hset("testjoint_data", "pose_lm", request_data["poseLandmark"])
    # redis_client.hset("testjoint_data", "world_lm", request_data["worldLandmark"])
    # redis_client.hset("testjoint_data", "time", request_data["time"])

    if request_data["enable"] == 'true':
        if request_data["stats"] == 'true':
            motor.drive(10, 99.9, 100)
            print("Walk-E has moved.")
            
        else:
            motor.stop()
            print("Walk-E stopped.")
    else:
        print("Walk-E is not enabled")

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

    # Cache Statistics and Video Recording into Server with timestamp as key
    # redis_client.hset("testjoint_data", "stats", json.dumps(stats_data).encode("utf-8"))

    return render_template("statistics.html", stats_Info = stats_data)

#################################################################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context='adhoc')
