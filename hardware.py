import RPi.GPIO as GPIO
import mediapipe as mp
import cv2
import time

import rediscache
import walkE_math
import walkE_dict

EN1 = 32 #GPIO 12 (PWM0)
EN2 = 33 #GPIO 13 (PWM1)
IN1 = 13 #GPIO 27
IN2 = 15 #GPIO 22
IN3 = 16 #GPIO 23
IN4 = 18 #GPIO 24
OP_ENCODE_ONE = 11 #GPIO 17
OP_ENCODE_TWO = 36 #GPIO 16

DIST_PER_STEP = 0.2075/15 # 1 full rotation = 0.2075m, 15 state changes

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

#################################################################################################

# Right Motor Setup
GPIO.setup(EN1, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT) 
GPIO.setup(IN2, GPIO.OUT)

GPIO.output(IN1, 0)
GPIO.output(IN2, 0) 

pwm_right = GPIO.PWM(EN1, 1000)
pwm_right.start(0)

# Left Motor Setup
GPIO.setup(EN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

GPIO.output(IN3, 0)
GPIO.output(IN4, 0) 

pwm_left = GPIO.PWM(EN2, 1000)
pwm_left.start(0)

# Optical Encoder Setup
GPIO.setup(OP_ENCODE_ONE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(OP_ENCODE_TWO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
# cap = cv2.VideoCapture(0) 

#################################################################################################

def hip_detect(landmarks):
    
    right_hip = mp_pose.PoseLandmark.RIGHT_HIP.value
    left_hip = mp_pose.PoseLandmark.LEFT_HIP.value
    
    right_hip_camera = [landmarks[right_hip].x, landmarks[right_hip].y]
    left_hip_camera = [landmarks[left_hip].x, landmarks[left_hip].y]

    hip_dist = walkE_math.cal_twoD_dist(right_hip_camera, left_hip_camera)
    print("Hip Length:  ", hip_dist)
    
    return hip_dist

def proxy_detect(image, landmarks):
    hip_dist = hip_detect(landmarks)
    
    if hip_dist > 0.1:
    # cv2.putText(image, "Too Close! Walk-E will accelerate", (15,12),~~~
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
        print("TooClose")
        return "TooClose"
    elif hip_dist < 0.07:
        # cv2.putText(image, "Too Far! Walk-E will slow down", (15,12),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
        print("TooFar")
        return "TooFar"
    else:
        # cv2.putText(image, "Walk-E will maintain current speed", (15,12),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
        print("Nice")
        return "Nice"       
#################################################################################################

def motor_drive(duty_left, duty_right):
    GPIO.output(IN1, 0)
    GPIO.output(IN3, 0)

    if duty_left == 0 and duty_right == 0:
        GPIO.output(IN2, 0)
        GPIO.output(IN4, 0)

        print("Walk-E has stopped\n")
    else:
        GPIO.output(IN2, 1)
        GPIO.output(IN4, 1)
        
        pwm_right.ChangeDutyCycle(duty_right)
        pwm_left.ChangeDutyCycle(duty_left)

        print("Walk-E is moving. (", duty_left, ",", duty_right, ")\n")

#################################################################################################
def encoder_init():
    return [{
        "count_one": 0,
        "count_two": 0,
        # "current_one": GPIO.input(OP_ENCODE_ONE),
        # "current_two": GPIO.input(OP_ENCODE_TWO),
        "last_one": GPIO.input(OP_ENCODE_ONE),
        "last_two": GPIO.input(OP_ENCODE_TWO),
        "dist_status": "",
        "time": time.time()
    }]

def encoder_stateChange(encoder_json, dist_status):
    count_one = encoder_json["count_one"]
    count_two = encoder_json["count_two"]
    last_one = encoder_json["last_one"]    
    last_two = encoder_json["last_two"]

    current_one = GPIO.input(OP_ENCODE_ONE)
    current_two = GPIO.input(OP_ENCODE_TWO)

    if current_one != last_one:
        last_one = current_one
        count_one = count_one + 1

    if current_two != last_two:
        last_two = current_two
        count_two = count_two + 1
    
    return {
        "count_one": count_one,
        "count_two": count_two,
        # "current_one": current_one,
        # "current_two": current_two,
        "last_one": last_one,
        "last_two": last_two,
        "dist_status": dist_status,
        "time": time.time()
    }

def encoder_process(encoder_list):
    dist_one, dist_two = 0,0 
    encoder_one, encoder_two = [], []
    init_time, end_time = encoder_list[1]["time"], 0

    for count in range(max(data["count_one"] for data in encoder_list)):
        encoder_one.append(max(filter(lambda x: x["count_one"] == count, encoder_list), 
                                key=lambda x:x["time"]))

    for count in range(max(data["count_two"] for data in encoder_list)):
        encoder_two.append(max(filter(lambda x: x["count_two"] == count, encoder_list), 
                                key=lambda x:x["time"]))
    
    for idx in range(len(encoder_one)):
        try:
            if encoder_one[idx]["dist_status"] == encoder_one[idx+1]["dist_status"]:
                dist_one = dist_one + DIST_PER_STEP
        except:
            pass

    for idx in range(len(encoder_two)):
        try:
            if encoder_two[idx]["dist_status"] == encoder_two[idx+1]["dist_status"]:
                dist_two = dist_two + DIST_PER_STEP
        except:
            pass

    if encoder_one[-1]["time"] > encoder_two[-1]["time"]:
        end_time = encoder_one[-1]["time"]
    else:
        end_time = encoder_two[-1]["time"]

    stats = {
        "distance": (dist_one + dist_two)/2
    }
    stats["speed"] = stats["distance"]/(end_time - init_time)

    # rediscache.cache_hw("testjoint_data", "distance", stats["distance"])
    # rediscache.cache_hw("testjoint_data", "speed", stats["speed"])

    print("Encoder Processing Complete")

# def encoder_logic(stateCountOne, stateCountTwo, time):
#     if stateCountOne != 0:
#         # Statistical Calulation from Hardware
#         stats = {
#             "distance": DIST_PER_STEP * stateCountOne
#         }

#         stats["speed"] = stats["distance"] / time

#         # print(stats)

#         rediscache.cache_hw("testjoint_data", "hardware_one", stats)
    
#     if stateCountTwo != 0:
#         # Statistical Calulation from Hardware
#         stats = {
#             "distance": DIST_PER_STEP * stateCountTwo
#         }
        
#         stats["speed"] = stats["distance"] / time

#         # print(stats)

#         rediscache.cache_hw("testjoint_data", "hardware_two", stats)
