"""
A very simple Raspberry Pi implementation of a Thermal IR Camera.

This started as an experiment to see how many of the components I had could
I get working at once. Also, this makes use of a HAT form-factor component,
which, to see if I could, I wired through the breadboard along with the
other components.

Components used:
* Raspberry PI 3 Model B - https://www.raspberrypi.org/products/raspberry-pi-3-model-b/
* Pimoroni Unicorn HAT HD 16x16 RGB display - https://shop.pimoroni.com/products/unicorn-hat-hd
* Adafruit 8x8 IR Grideye (AMG8833) - https://www.adafruit.com/product/3538
* Adafruit PiOLED - 128x32 Monochrome OLED - https://www.adafruit.com/product/3527
* 9 LEDs (3x green, 3x yellow, 3x red)
* 9 330 ohm resistors
* A bunch of breadboard jumper wires

"""

import unicornhathd as uh
import busio
import board
import adafruit_amg88xx
import numpy as np
import math
from scipy.misc import imresize
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import sys
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import RPi.GPIO as GPIO

COLORS = np.array([
	[36, 0, 79],
	[125, 0, 255],
	[0, 0, 255],
	[0, 255, 255],
	[255, 255, 0],
	[255, 125, 0],
	[255, 0, 0],
	[79, 0, 0]
])


"""
A super-simple OOP way to access an output GPIO pin
"""
class SimplePinOut:
	def __init__(self, pin_no):
		self.__pin_no = pin_no
		GPIO.setup(self.__pin_no, GPIO.OUT)

	def on(self):
		GPIO.output(self.__pin_no, True)

	def off(self):
		GPIO.output(self.__pin_no, False)
"""
A super-simple OOP way to access GPIO outputs
"""
class SimpleGPIO:

	def __init__(self, warnings=False):
		self.__pins = {}
		GPIO.setmode(GPIO.BCM)
		#GPIO.setwarnings(warnings)

	def get_pin_out(self, pin_no):
		if pin_no not in self.__pins:
			self.__pins[pin_no] = SimplePinOut(pin_no)
		return self.__pins[pin_no]

"""
Utilizes the GPIO pins and attached LEDs to construct a simple scale graph
"""
class LedScale:

	def __init__(self, pins):
		self.__pins = pins
		self.__gpio = SimpleGPIO()

	def __set_pin(self, pin_no, on=True):
		pin = self.__gpio.get_pin_out(pin_no)
		if on is True:
			pin.on()
		else:
			pin.off()

	def __set_pins(self, pin_nos, on=True):
		for pin_no in pin_nos:
			self.__set_pin(pin_no, on)

	def clear(self):
		for pin_no in self.__pins:
			self.__set_pin(pin_no, False)

	def set(self, level):
		"""
		Sets the scale level (0.0 - 1.0)
		"""
		assert level >= 0.0 and level <= 1.0
		self.clear()

		num_leds_to_on = int(round(level * len(self.__pins)))
		set_pin_nos = self.__pins[:num_leds_to_on]
		self.__set_pins(set_pin_nos, True)

"""
A simple controller for the PiOLED from Adafruit
"""
class PiOLED:
	def __init__(self):
		RST = None
		DC = 23
		SPI_PORT = 0
		SPI_DEVICE = 0
		self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
		self.disp.begin()
		self.width = self.disp.width
		self.height = self.disp.height
		self.image = Image.new('1', (self.width, self.height))
		self.draw = ImageDraw.Draw(self.image)
		self.font = ImageFont.load_default()
		self.clear()

	def clear(self, disp=True):
		self.draw.rectangle((0,0,self.width,self.height), outline=0, fill=0)
		if disp == True:
			self.disp.clear()
			self.disp.display()

	def show(self):
		self.disp.image(self.image)
		self.disp.display()

	def text(self, str, xy):
		self.draw.text(xy, str, font=self.font, fill=255)

	def line(self, xy):
		self.draw.line(xy, fill=244, width=1)

"""
The main controller for the TermCam experiment
"""
class ThermCam:

	def __init__(self, colors=COLORS, led_pins=[5, 6, 12, 13, 16, 19, 20, 21, 26]):
		self.__colors = colors
		self.__led_scale = LedScale(led_pins)
		self.__led_scale.clear()

		i2c = busio.I2C(board.SCL, board.SDA)
		self.__amg = adafruit_amg88xx.AMG88XX(i2c)

		self.__led_disp = PiOLED()

		mean_list_len = int(self.__led_disp.width / 2)
		self.__means = np.zeros((mean_list_len,))
		self.__means[:] = np.nan

		self.__min_sampled_mean = 1000000
		self.__max_sampled_mean = -1000000

	"""
	Appends a value to the the end of the list and shifts existing values up by one
	"""
	def __add_mean(self, m):
		for i in range(len(self.__means) - 1):
			self.__means[i] = self.__means[i+1]
		self.__means[len(self.__means)-1] = m

	"""
	Draws a line graph on the PiOLED display following the 'means' list of values
	"""
	def __draw_means_line(self):
		min = np.nanmin(self.__means)
		max = np.nanmax(self.__means)
		for i in range(len(self.__means) - 1):
			x = int(self.__led_disp.width / 2) + i
			m0 = self.__means[i]
			m1 = self.__means[i+1]
			y0 = (1.0 - ((m0 - min) / (max - min))) * self.__led_disp.height
			y1 = (1.0 - ((m1 - min) / (max - min))) * self.__led_disp.height
			self.__led_disp.line(((x, y0), (x+1, y1)))


	"""
	Fetches the color gradient relative to the fraction ('f') of 0-1.0
	"""
	def __get_color(self, f):
		if np.isnan(f):
			return (0, 0, 0)
		i = f * (len(self.__colors) - 1.0)
		low = int(math.floor(i))
		high = int(math.ceil(i))
		f = i - low
		low_color = self.__colors[low]
		high_color = self.__colors[high]
		rgb = high_color * f + low_color * (1.0 - f)
		return np.array(rgb, dtype=np.uint8)


	"""
	Displays the AMG8833 8x8 pixel values to the Unicorn HAT HD 16x16 display
	"""
	def __display_to_uh(self, arr):
		arr = imresize(arr, (16, 16), interp='lanczos')
		for y in range(arr.shape[0]):
			for x in range(arr.shape[1]):
				f = (arr[y][x] - arr.min()) / (arr.max() - arr.min())
				rgb = self.__get_color(f)
				uh.set_pixel(x, y, rgb[0], rgb[1], rgb[2])
		uh.show()

	def __update_led_scale(self, amg_pixels):
		mean = amg_pixels.mean()
		self.__min_sampled_mean = np.nanmin(self.__means)
		self.__max_sampled_mean = np.nanmax(self.__means)
		if self.__max_sampled_mean > self.__min_sampled_mean:
			level = (mean - self.__min_sampled_mean) / (self.__max_sampled_mean - self.__min_sampled_mean)
		else:
			level = 1.0
		self.__led_scale.set(level)

	def __display_to_pioled(self, amg_pixels):
		min = amg_pixels.min()
		max = amg_pixels.max()
		mean = amg_pixels.mean()

		self.__add_mean(mean)
		self.__led_disp.clear(disp=False)
		self.__led_disp.text("Min: %.1f"%min, (0, 2))
		self.__led_disp.text("Max: %.1f"%max, (0, 10))
		self.__led_disp.text("Mean: %.1f"%mean, (0, 18))
		self.__draw_means_line()
		self.__led_disp.show()

	"""
	Continually refreshes the AMG8833 pixel values and redisplays
	"""
	def loop_display(self):
		while True:
			pixels = np.array(self.__amg.pixels)
			self.__display_to_uh(pixels)
			self.__display_to_pioled(pixels)
			self.__update_led_scale(pixels)

if __name__ == "__main__":

	thermcam = ThermCam(colors=COLORS, led_pins=[5, 6, 12, 13, 16, 19, 20, 21, 26])

	try:
		thermcam.loop_display()
	finally:
		uh.off()
