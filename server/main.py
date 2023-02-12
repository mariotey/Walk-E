from flask import Flask, render_template, request

import rediscache
import gait_calibrate
import gait_statistics
import gait_process
# import hardware

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
    
    # hardware_data = hardware.logic(move_stats)
    # rediscache.cache_hw("hardware_data", hardware_data)
    
    return render_template("main.html")

#################################################################################################

@app.route('/PlotStats', methods=["GET", "POST"])
def plot_stats():
    # Retrieve calibration and stats data from server 
    calibrate_world_lm, calibrate_time = rediscache.request_lm("calibration_data")
    joint_world_lm, joint_time = rediscache.request_lm("testjoint_data")
    # hardware_data = rediscache.request_hw("hardware_data")
    
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
