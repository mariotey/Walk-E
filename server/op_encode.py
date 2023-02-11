import RPi.GPIO as GPIO
import time

DIST_PER_STEP = 0.2075/15 # 1 full rotation = 0.2075m, 15 state changes

# Declare GPIO port
sensor_one = 11

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# Set up GPIO port
GPIO.setup(sensor_one, GPIO.IN, pull_up_down=GPIO.PUD_UP)

stateLast = GPIO.input(sensor_one)

def get_stateChange():
    stateCount = 0
    start_time = time.time()
    try:
        while True:
            stateCurrent = GPIO.input(sensor_one)

            if stateCurrent != stateLast:
                print("stateCurrent:", stateCurrent)
                print("stateLast:", stateLast,"\n")
                
                stateLast = stateCurrent
                stateCount += 1
            else:
                print("stateCurrent:", stateCurrent)
                print("stateLast:", stateLast,"\n")
        
            
    except KeyboardInterrupt:
        last_time = time.time()
        print("\n###########################################")
        print("stateCount:", stateCount)
        print("Distance:", DIST_PER_STEP*stateCount, "m")
        print("Time Taken:", last_time - start_time, "sec")
        print("Speed:", (DIST_PER_STEP*stateCount)/(last_time - start_time), "m/sec")
        print("\n###########################################")

    print("Complete")