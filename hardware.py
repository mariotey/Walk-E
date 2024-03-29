import RPi.GPIO as GPIO
import mediapipe as mp
import time

import walkE_math

EN1 = 32 #GPIO 12 (PWM0)
EN2 = 33 #GPIO 13 (PWM1)
IN1 = 13 #GPIO 27, input pin for Right Motor
IN2 = 15 #GPIO 22, input pin for Right Motor
IN3 = 16 #GPIO 23, input pin for Left Motor
IN4 = 18 #GPIO 24, input pin for Left Motor
OP_ENCODE_ONE = 11 #GPIO 17
OP_ENCODE_TWO = 36 #GPIO 16

DIST = 0.25/40 # Circumference of Wheel = 0.22m

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

#################################################################################################

# Right Motor Setup
GPIO.setup(EN1, GPIO.OUT)
# GPIO.setup(IN1, GPIO.OUT) 
GPIO.setup(IN2, GPIO.OUT)

# GPIO.output(IN1, 0)
    
pwm_right = GPIO.PWM(EN1, 1000)
pwm_right.start(0)

# Left Motor Setup
GPIO.setup(EN2, GPIO.OUT)
# GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# GPIO.output(IN3, 0)

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

#################################################################################################

def hip_detect(landmarks):
    
    right_hip = mp_pose.PoseLandmark.RIGHT_HIP.value
    left_hip = mp_pose.PoseLandmark.LEFT_HIP.value
    
    right_hip_camera = [landmarks[right_hip].x, landmarks[right_hip].y]
    left_hip_camera = [landmarks[left_hip].x, landmarks[left_hip].y]

    hip_dist = walkE_math.cal_twoD_dist(right_hip_camera, left_hip_camera)
    print("Hip Length:  ", hip_dist)
    
    return hip_dist

def proxy_detect(image, landmarks, thres):
    hip_dist = hip_detect(landmarks)

    if hip_dist > (thres * 1.05):
    # cv2.putText(image, "Too Close! Walk-E will accelerate", (15,12),~~~
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
        print(f"TooClose. {hip_dist} \n")
        return hip_dist, 2
    elif hip_dist < (thres * 0.8):
        # cv2.putText(image, "Too Far! Walk-E will slow down", (15,12),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
        print(f"TooFar. {hip_dist} \n")
        return hip_dist, 0
    else:
        # cv2.putText(image, "Walk-E will maintain current speed", (15,12),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
        print(f"Nice. {hip_dist} \n")
        return hip_dist, 1       
#################################################################################################

def motor_drive(duty_left, duty_right):
    if duty_left == 0 and duty_right == 0:
        GPIO.output(IN2, 0)
        GPIO.output(IN4, 0)

        # print("Walk-E has stopped\n")
    else:
        GPIO.output(IN2, 1)
        GPIO.output(IN4, 1)
        
        pwm_right.ChangeDutyCycle(duty_right)
        pwm_left.ChangeDutyCycle(duty_left)

        #print("Walk-E is moving. (", duty_left, ",", duty_right, ")\n")

#################################################################################################

def encoder_init():
    return [{
        "count_one": 0,
        "count_two": 0,
        "last_one": GPIO.input(OP_ENCODE_ONE),
        "last_two": GPIO.input(OP_ENCODE_TWO),
        "dist_status": "",
        "time": time.time()
    }]

def encoder_stateChange(encoder_json, dist_status):    
    def process_logic(count, last, current):
        if current != last:
            last = current
            count = count + 1
    
        return count, last
    
    count_one, last_one = process_logic(encoder_json["count_one"],
                                        encoder_json["last_one"],
                                        GPIO.input(OP_ENCODE_ONE))
    
    count_two, last_two = process_logic(encoder_json["count_two"],
                                        encoder_json["last_two"],
                                        GPIO.input(OP_ENCODE_TWO))

    return {
        "count_one": count_one, # Right Motor
        "count_two": count_two, # Left Motor
        "last_one": last_one,
        "last_two": last_two,
        "dist_status": dist_status,
        "time": time.time()
    }

def encode_process(encoder_data):
    print("Processing Encoder Data...")

    if encoder_data != "":
        def process_data(encode):
            max_count = max(encode["count"])

            endtime = encode["time"][encode["count"].index(max_count)]
            dist_x = DIST * max_count

            return encode["time"][0], endtime, dist_x

        inittime_one, endtime_one, dist_one = process_data(encoder_data["encoder_one"])
        inittime_two, endtime_two, dist_two = process_data(encoder_data["encoder_two"])

        init_time, end_time = min(inittime_one, inittime_two), max(endtime_one, endtime_two)

        stats = {"dist": (dist_one + dist_two)/2}
        stats["speed"] = stats["dist"]/(end_time - init_time) if end_time != init_time else "-" 
        
        print("Distance:", stats["dist"], "m")
        print("Speed:", stats["speed"], "m/s")

        print("Encoder Data Retrieved\n")

        return stats

    return {
        "dist":"-",
        "speed":"-"
    }
