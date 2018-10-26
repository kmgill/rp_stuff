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
		GPIO.output(self.__pin_no, True)

	def off(self):
		GPIO.output(self.__pin_no, False)

class SimpleGPIO:

	def __init__(self, warnings=False):
		self.__pins = {}
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(warnings)

	def get_pin_out(self, pin_no):
		if pin_no not in self.__pins:
			self.__pins[pin_no] = SimplePinOut(pin_no)
		return self.__pins[pin_no]



def light_pin(gpio, pin_no, do_sleep=True):
	pin = gpio.get_pin_out(pin_no)
	pin.on()
	if do_sleep is True:
		time.sleep(1)
		pin.off()

def light_pins(gpio, pin_nos, do_sleep):
	for pin_no in pin_nos:
		light_pin(gpio, pin_no, do_sleep)

if __name__ == "__main__":
	pin_nos = (21,)
	if len(sys.argv) >= 2:
		pin_nos = map(int, sys.argv[1:])

	gpio = SimpleGPIO()
	#light_pins(gpio, pin_nos, True)
	light_pins(gpio, pin_nos, False)
	time.sleep(2)
	#light_pins(gpio, pin_nos, True)
	#GPIO.cleanup()
