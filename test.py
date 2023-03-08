import RPi.GPIO as GPIO
import mediapipe as mp
import time

import walkE_cache
import walkE_math

EN1 = 32 #GPIO 12 (PWM0)
EN2 = 33 #GPIO 13 (PWM1)
IN1 = 13 #GPIO 27
IN2 = 15 #GPIO 22
IN3 = 16 #GPIO 23
IN4 = 18 #GPIO 24
OP_ENCODE_ONE = 11 #GPIO 17
OP_ENCODE_TWO = 36 #GPIO 16

DIST_ONE = 0.2075/1.2 # Circumference of Wheel = 0.2075m
DIST_TWO = 0.2075/2

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# Optical Encoder Setup
GPIO.setup(OP_ENCODE_ONE, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(OP_ENCODE_TWO, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

current, last, count = 0, 0, 0
while 1:
    current = GPIO.input(OP_ENCODE_ONE)
    if current != last:
        last = current
        count = count + 1
    
    print(current, count)