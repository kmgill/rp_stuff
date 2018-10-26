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

colors = np.array([
	[36, 0, 79],
	[125, 0, 255],
	[0, 0, 255],
	[0, 255, 255],
	[255, 255, 0],
	[255, 125, 0],
	[255, 0, 0],
	[79, 0, 0]
])

means = None

min_sampled_mean = 1000000
max_sampled_mean = -1000000


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
		#GPIO.setwarnings(warnings)

	def get_pin_out(self, pin_no):
		if pin_no not in self.__pins:
			self.__pins[pin_no] = SimplePinOut(pin_no)
		return self.__pins[pin_no]

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

		#y = self.height / 2
		#self.draw.line(((self.width/2, y), (self.width, y)), fill=255, width=1)
		#self.show()

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

def add_mean(m):
	for i in range(len(means) - 1):
		means[i] = means[i+1]
	means[len(means)-1] = m


def draw_means_line():
	min = np.nanmin(means)
	max = np.nanmax(means)
	for i in range(len(means) - 1):
		x = int(led_disp.width / 2) + i
		m0 = means[i]
		m1 = means[i+1]
		y0 = (1.0 - ((m0 - min) / (max - min))) * led_disp.height
		y1 = (1.0 - ((m1 - min) / (max - min))) * led_disp.height
		led_disp.line(((x, y0), (x+1, y1)))


"""
Fetches the color gradient relative to the fraction ('f') of 0-1.0
"""
def get_color(f):
	if np.isnan(f):
		return (0, 0, 0)
	i = f * (len(colors) - 1.0)
	low = int(math.floor(i))
	high = int(math.ceil(i))
	f = i - low
	low_color = colors[low]
	high_color = colors[high]
	rgb = high_color * f + low_color * (1.0 - f)
	return np.array(rgb, dtype=np.uint8)


"""
Displays the AMG8833 8x8 pixel values to the Unicorn HAT HD 16x16 display
"""
def display_to_uh(arr):
	arr = imresize(arr, (16, 16), interp='lanczos')
	for y in range(arr.shape[0]):
		for x in range(arr.shape[1]):
			f = (arr[y][x] - arr.min()) / (arr.max() - arr.min())
			rgb = get_color(f)
			uh.set_pixel(x, y, rgb[0], rgb[1], rgb[2])
	uh.show()


def display_to_pioled(amg_pixels):
	global min_sampled_mean
	global max_sampled_mean

	min = amg_pixels.min()
	max = amg_pixels.max()
	mean = amg_pixels.mean()
	min_sampled_mean = np.min([min_sampled_mean, mean])
	max_sampled_mean = np.max([max_sampled_mean, mean])
	if max_sampled_mean > min_sampled_mean:
		level = (mean - min_sampled_mean) / (max_sampled_mean - min_sampled_mean)
	else:
		level = 1.0
	add_mean(mean)
	led_disp.clear(disp=False)
	led_disp.text("Min: %.1f"%min, (0, 2))
	led_disp.text("Max: %.1f"%max, (0, 10))
	led_disp.text("Mean: %.1f"%mean, (0, 18))
	draw_means_line()
	led_disp.show()

	led_scale.set(level)




"""
Continually refreshes the AMG8833 pixel values and redisplays
"""
def loop_display(amg):
	while True:
		pixels = np.array(amg.pixels)
		display_to_uh(pixels)
		display_to_pioled(pixels)


if __name__ == "__main__":

	led_scale = LedScale([5, 6, 12, 13, 16, 19, 20, 21, 26])
	led_scale.clear()

	i2c = busio.I2C(board.SCL, board.SDA)
	amg = adafruit_amg88xx.AMG88XX(i2c)

	led_disp = PiOLED()

	mean_list_len = int(led_disp.width / 2)
	means = np.zeros((mean_list_len,))
	means[:] = np.nan

	try:
		loop_display(amg)
	finally:
		uh.off()
