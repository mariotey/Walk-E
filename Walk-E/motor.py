import RPi.GPIO as GPIO
from time import sleep

#Right Motor
EN1 = 32 #GPIO 12 (PWM0)
IN1 = 13 #GPIO 27
IN2 = 15 #GPIO 22

#Left Motor
EN2 = 33 #GPIO 13 (PWM1)
IN3 = 16 #GPIO 23
IN4 = 18 #GPIO 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

#Set up for Motors
GPIO.setup(EN1, GPIO.OUT)
GPIO.setup(EN2, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT) 
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

GPIO.output(IN1, 0)
GPIO.output(IN2, 0) 
GPIO.output(IN3, 0)
GPIO.output(IN4, 0) 

pwm_right = GPIO.PWM(EN1, 1000)
pwm_left = GPIO.PWM(EN2, 1000)
pwm_right.start(0)
pwm_left.start(0)

def goStraight(delay, duty_left, duty_right):
    GPIO.output(IN1, 0)
    GPIO.output(IN3, 0)

    GPIO.output(IN2, 1)
    GPIO.output(IN4, 1)
    
    pwm_right.ChangeDutyCycle(duty_right)
    pwm_left.ChangeDutyCycle(duty_left)

    sleep(delay)

    print("Left Motor:", duty_left, ", Right Motor:", duty_right)

goStraight(0.5, 37, 40)

# try:       
#     while True:
#         duty_right = 40
#         duty_left = 37    
#         goStraight(0.5, duty_left, duty_right)
    
# finally:
#     GPIO.cleanup()
