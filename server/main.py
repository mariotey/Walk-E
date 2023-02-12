from flask import Flask, render_template, request
import time
import RPi.GPIO as GPIO

import rediscache
import gait_calibrate
import gait_statistics
import gait_process
import hardware

OP_ENCODE_ONE = 11 #GPIO 17
OP_ENCODE_TWO = 36 #GPIO 16

DIST_PER_STEP = 0.2075/15 # 1 full rotation = 0.2075m, 15 state changes

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(OP_ENCODE_ONE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(OP_ENCODE_TWO, GPIO.IN, pull_up_down=GPIO.PUD_UP)


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
    rediscache.cache_lm("calibration_data", request_data)

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
        rediscache.cache_lm("testjoint_data", request_data)
    
    stateCount_one, stateCount_two = 0, 0
    stateLast_one, stateLast_two = GPIO.input(OP_ENCODE_ONE), GPIO.input(OP_ENCODE_TWO)
    
    start_time = time.time()

    while move_stats: 
        # ret, frame = cap.read()
        # results = pose.process(frame)

        try:
            print("Walk-E moves")

            # camera_lm = results.pose_landmarks.landmark
            # dist_status = proxy_detect(frame, camera_lm)

            # motor_drive(*walkE_dict.proxy_status[dist_status])

            hardware.motor_drive(*[25,25])
                        
            stateCount_one, stateLast_one = hardware.encoder_stateChange(OP_ENCODE_ONE, stateCount_one, stateLast_one)
            stateCount_two, stateLast_two = hardware.encoder_stateChange(OP_ENCODE_TWO, stateCount_two, stateLast_two)
            
        except AttributeError:
            # print("Nothing / Errors detected")
            pass  # Pass if there is no detection or error   

    hardware.motor_drive(0, 0)
    end_time = time.time()

    print("Walk-E stops")

    if stateCount_one != 0:
        # Statistical Calulation from Hardware
        # print("StateCount_one:", stateCount_one,"\n")
        
        stats = {}

        stats["distance"] = DIST_PER_STEP * stateCount_one
        stats["speed"] = stats["distance"] / (end_time - start_time)

        print(stats)

        rediscache.cache_hw("testjoint_data", "hardware_one", stats)
    
    if stateCount_two != 0:
        # Statistical Calulation from Hardware
        # print("StateCount_two:", stateCount_two,"\n")
        
        stats = {}

        stats["distance"] = DIST_PER_STEP * stateCount_two
        stats["speed"] = stats["distance"] / (end_time - start_time)

        print(stats)

        rediscache.cache_hw("testjoint_data", "hardware_two", stats)
    
    return render_template("main.html")

#################################################################################################

@app.route('/PlotStats', methods=["GET", "POST"])
def plot_stats():
    # Retrieve calibration and stats data from server 
    calibrate_world_lm, calibrate_time = rediscache.request_lm("calibration_data")
    joint_world_lm, joint_time = rediscache.request_lm("testjoint_data")
    hardware_one_data = rediscache.request_hw("testjoint_data", "hardware_one")
    hardware_two_data = rediscache.request_hw("testjoint_data", "hardware_two")

    print(hardware_one_data)
    print(hardware_two_data)
    
    calibrate_data = gait_process.get_lm(calibrate_world_lm, calibrate_time)
    joint_data = gait_process.get_lm(joint_world_lm, joint_time)   

    if joint_data == []:
        return render_template("main.html")

    # Calculation of Gait Statistics
    offsetdata = gait_calibrate.calibrate(calibrate_data)
    gait_data = gait_process.get_gait(offsetdata["cut_off"], joint_data)
    stats_data = gait_statistics.stats(joint_data, gait_data, offsetdata)
    # stats_data = gait_statistics.stats(joint_data, gait_data, hardware_data, offsetdata)

    return render_template("statistics.html", stats_Info = stats_data)

#################################################################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context='adhoc')
