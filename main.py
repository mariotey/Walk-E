from flask import Flask, render_template, request
import mediapipe as mp
import cv2

import walkE_cache
import gait_statistics
import gait_process
import hardware
import walkE_admin

calibration_hiplen = []
hiplen_list = []

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
    try:
        ret, frame = cap.read()
        results = pose.process(frame)
        camera_lm = results.pose_landmarks.landmark
        calibration_hiplen.append(hardware.hip_detect(camera_lm))        

    except AttributeError:
        pass  # Pass if there is no detection or error 

    print(calibration_hiplen)

    return ('', 204)

@app.route('/CacheCalibrate', methods=["GET", "POST"])
def cache_calibrate():
    request_data = request.form

    walkE_cache.cache_lm("calibration_data", request_data)

    return render_template("main.html")

#################################################################################################

@app.route('/encode_dist', methods=["GET", "POST"])
def encode_req():
    global encoder_stat
    encoder_stat = True

    while encoder_stat:
        encoder_list.append(hardware.encoder_stateChange(encoder_list[-1], 1))    

    return ('', 204) 

@app.route('/walkE_move', methods=["GET", "POST"])
def walkE_move():     
    # if calibration_hiplen:
    #     avg_hiplen = np.mean(calibration_hiplen)
    # else:
    #     avg_hiplen = 0.15  
    
    # try:
    #     ret, frame = cap.read()
    #     results = pose.process(frame)

    #     hip_len, dist_stat = hardware.proxy_detect(frame, results.pose_landmarks.landmark, avg_hiplen)
  
    #     hiplen_list.append({"hiplen": hip_len, "time": time.time(), "dist_status": dist_stat})
    #     hardware.motor_drive(*walkE_dict.proxy_status[dist_stat])
       
    # except AttributeError:
    #     # Stops if user is not in frame
    #     hardware.motor_drive(*[0,0])

    # hardware.motor_drive(*[35,25])
    hardware.motor_drive(*[100,90])
    
    return ('', 204)

#################################################################################################

@app.route('/walkE_stop', methods=["GET", "POST"])
def walkE_stop():
    global encoder_stat
    encoder_stat = False

    print("Stop Motor")
    # Stop Motors
    hardware.motor_drive(*[0,0])
    encoder_stat = True

    return('', 204)

@app.route('/CacheStats', methods=["GET", "POST"])
def cache_stats():  
    # Cache Gait Data
    walkE_cache.cache_lm("testjoint_data", request.form)  

    # Cache Hip Len
    walkE_cache.cache_proxy("admin_data", hiplen_list)

    # Cache Optical Encoder Data
    walkE_cache.cache_encode("testjoint_data", encoder_list)
    
    return('', 204)

#################################################################################################

@app.route('/GetStats', methods=["GET", "POST"])
def plot_stats():
    # Retrieve calibration and stats data from server 
    joint_data = walkE_cache.request_lm("testjoint_data")

    if joint_data == []:
        return render_template("main.html")
    
    # Retrieve Calibration Data
    offsetdata = walkE_cache.request_lm("calibration_data")
    
    # Retrieve Optical Encoder Data
    encoderdata = hardware.encode_process(walkE_cache.request_encode("testjoint_data"))

    # Retrieve and Calculate Gait Statistics
    gait_data = gait_process.get_gait(offsetdata["cut_off"], joint_data)
    stats_data = gait_statistics.stats(joint_data, gait_data, encoderdata, offsetdata)

    return render_template("statistics.html", stats_Info = stats_data)

#################################################################################################

@app.route('/Admin', methods=["GET", "POST"])
def admin():
    # Retrieve Optical Encoder Data
    encoderdata = walkE_cache.request_encode("testjoint_data")

    # Retrieve data for Admin
    hiplendata = walkE_cache.request_proxy("admin_data")
    encode_data = walkE_admin.get_encoder(hiplendata, encoderdata)

    admin_data = {
        "encode_data": encode_data
    }

    return render_template("admin.html", admin_Info = admin_data)
#################################################################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context='adhoc')
