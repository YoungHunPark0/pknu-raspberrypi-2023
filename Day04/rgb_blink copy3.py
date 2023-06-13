# LED RGB 깜빡이기
import RPi.GPIO as GPIO
import time

red = 17 # Ground 역할
green = 27
blue = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(red, GPIO.OUT)
GPIO.setup(green, GPIO.OUT)
GPIO.setup(blue, GPIO.OUT)

GPIO.output(red, False)
GPIO.output(green, False)
GPIO.output(blue, False) # 여기까지 초기화

try:
    while True:
        # RED+GREEN = YELLOW / RED+BLUE = PINK / GREEN+BLUE = SKY / RED+GREEN+BLUE = WHITE

        GPIO.output(red, False) # RED 켜짐
        GPIO.output(green, True)
        GPIO.output(blue, True)
        time.sleep(1)
        GPIO.output(red, True)
        GPIO.output(green, False) # Green 켜짐
        GPIO.output(blue, True)
        time.sleep(1)
        GPIO.output(red, True)
        GPIO.output(green, True)
        GPIO.output(blue, GPIO.LOW) # Blue 켜짐
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.output(red, GPIO.HIGH) # GPIO.HIGH = True / GPIO.LOW = False
    GPIO.output(green, GPIO.HIGH)
    GPIO.output(blue, GPIO.HIGH)
    GPIO.cleanup() # 잘못되면 클린업으로 종료