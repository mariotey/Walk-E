from flask import Flask, render_template, request

import gait_calibrate
import gait_statistics
import modify_data
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
    modify_data.cache_lm("calibration_data", request_data)

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
        modify_data.cache_lm("testjoint_data", request_data)
    
    # hardware.logic(move_stats)
    
    return render_template("main.html")

#################################################################################################

@app.route('/PlotStats', methods=["GET", "POST"])
def plot_stats():
    # Retrieve calibration data from server 
    calibrate_world_lm, calibrate_time = modify_data.get_lm("calibration_data")
    calibrate_data = modify_data.request_lm(calibrate_world_lm, calibrate_time)

    # Retrieve stats data from server
    joint_world_lm, joint_time = modify_data.get_lm("testjoint_data")
    joint_data = modify_data.request_lm(joint_world_lm, joint_time)   

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
