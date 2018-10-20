"""
Simple script to turn an LED on and off via GPIO and to see how well it works in a object-oriented pattern

"""

import RPi.GPIO as GPIO
import time
import sys


class SimplePinOut:
	def __init__(self, pin_no):
		self.__pin_no = pin_no
		GPIO.setup(self.__pin_no, GPIO.OUT)

	def on(self):
		GPIO.output(self.__pin_no, GPIO.HIGH)

	def off(self):
		GPIO.output(self.__pin_no, GPIO.LOW)

class SimpleGPIO:

	def __init__(self, warnings=False):
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(warnings)

	def get_pin_out(self, pin_no):
		return SimplePinOut(pin_no)



if __name__ == "__main__":
	pin_no = 21
	if len(sys.argv) >= 2:
		pin_no = int(sys.argv[1])
	
	gpio = SimpleGPIO()
	pin = gpio.get_pin_out(pin_no)
	pin.on()
	time.sleep(1)
	pin.off()


