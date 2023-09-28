import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

def turn_on(pin_number):
	GPIO.setup(pin_number, GPIO.OUT)
	GPIO.output(pin_number, GPIO.HIGH)
	
def turn_off(pin_number):
	GPIO.setup(pin_number, GPIO.OUT)
	GPIO.output(pin_number, GPIO.LOW)

