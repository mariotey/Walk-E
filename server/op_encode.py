import RPi.GPIO as GPIO
import time

DIST_PER_STEP = 0.2075/15 # 1 full rotation = 0.2075m, 15 state changes

# Declare GPIO port
SENSOR_ONE = 11

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

def setup():
    # Set up GPIO port
    GPIO.setup(SENSOR_ONE, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    stateCount = 0
    stateLast = GPIO.input(SENSOR_ONE)

    return stateCount, stateLast

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

print("Complete")