import RPi.GPIO as GPIO
import mediapipe as mp
import cv2

import walkE_math
# import motor
# import dist
# import op_encode

EN1 = 32 #GPIO 12 (PWM0)
EN2 = 33 #GPIO 13 (PWM1)
IN1 = 13 #GPIO 27
IN2 = 15 #GPIO 22
IN3 = 16 #GPIO 23
IN4 = 18 #GPIO 24
SENSOR_ONE = 11 #GPIO 17
SENSOR_TWO = 36 #GPIO 16

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

# Optical Encoder 1 Setup
GPIO.setup(SENSOR_ONE, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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

#################################################################################################

def proxy_detect(image, landmarks):
    
    right_hip = mp_pose.PoseLandmark.RIGHT_HIP.value
    left_hip = mp_pose.PoseLandmark.LEFT_HIP.value
    
    right_hip_camera = [landmarks[right_hip].x, landmarks[right_hip].y]
    left_hip_camera = [landmarks[left_hip].x, landmarks[left_hip].y]

    hip_dist = walkE_math.cal_twoD_dist(right_hip_camera, left_hip_camera)
    print("Hip Length:", hip_dist)
    
    cv2.rectangle(image, (0,0), (300, 25), (245,117,16), -1)
            
    if hip_dist > 0.1:
        cv2.putText(image, "Too Close! Walk-E will accelerate", (15,12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
    elif hip_dist < 0.07:
        cv2.putText(image, "Too Far! Walk-E will slow down", (15,12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
    else:
        cv2.putText(image, "Walk-E will maintain current speed", (15,12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
        
#################################################################################################

def motor_drive(duty_left, duty_right):
    GPIO.output(IN1, 0)
    GPIO.output(IN3, 0)

    GPIO.output(IN2, 1)
    GPIO.output(IN4, 1)
    
    pwm_right.ChangeDutyCycle(duty_right)
    pwm_left.ChangeDutyCycle(duty_left)

    print("Walk-E is moving. (", duty_left, ",", duty_right, ")\n")

def motor_stop():
    GPIO.output(IN1, 0)
    GPIO.output(IN3, 0)

    GPIO.output(IN2, 0)
    GPIO.output(IN4, 0)

    print("Walk-E has stopped\n")

#################################################################################################

def get_stateChange(stateCount, stateLast):

    stateCurrent = GPIO.input(SENSOR_ONE)

    if stateCurrent != stateLast:
        print("stateCurrent:", stateCurrent)
        print("stateLast:", stateLast,"\n")
        
        stateLast = stateCurrent
        stateCount = stateCount + 1

    return stateCount, stateLast
            
    # except KeyboardInterrupt:
    #     last_time = time.time()
    #     print("\n###########################################")
    #     print("stateCount:", stateCount)
    #     print("Distance:", DIST_PER_STEP*stateCount, "m")
    #     print("Time Taken:", last_time - start_time, "sec")
    #     print("Speed:", (DIST_PER_STEP*stateCount)/(last_time - start_time), "m/sec")
    #     print("\n###########################################")

#################################################################################################

def logic(move_stats):
    stateCount = 0
    stateLast = GPIO.input(SENSOR_ONE)
    
    # Logic for Proximity Detection
    while move_stats: 
        ret, frame = cap.read()
        results = pose.process(frame)

        try:
            print("Walk-E moves")
            camera_lm = results.pose_landmarks.landmark

            proxy_detect(frame, camera_lm)
            stateCount, stateLast = get_stateChange(stateCount, stateLast)
            motor_drive(30, 30)
            
        except AttributeError:
            # print("Nothing / Errors detected")
            pass  # Pass if there is no detection or error   

    motor_stop()
    print("Walk-E stops")

    if stateCount != 0:
        print("StateCount:", stateCount,"\n")