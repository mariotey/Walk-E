import RPi.GPIO as GPIO

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

def drive(duty_left, duty_right):
    GPIO.output(IN1, 0)
    GPIO.output(IN3, 0)

    GPIO.output(IN2, 1)
    GPIO.output(IN4, 1)
    
    pwm_right.ChangeDutyCycle(duty_right)
    pwm_left.ChangeDutyCycle(duty_left)

    print("Walk-E is moving. (", duty_left, ",", duty_right, ")\n")

def stop():
    GPIO.output(IN1, 0)
    GPIO.output(IN3, 0)

    GPIO.output(IN2, 0)
    GPIO.output(IN4, 0)

    print("Walk-E has stopped\n")

# Go Straight
# drive(10, 99.9, 100)

# Turn Left
# drive(0.55, 0, 100)
# drive(1, 0, 0)
# drive(0.55, 0, 100)

# Go Straight
# drive(3, 99.9, 100)

# Turn Right
# drive(0.45, 100, 0)
# drive(1, 0, 0)
# drive(0.45, 100, 0)

print("Complete")

