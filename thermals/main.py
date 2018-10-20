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

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

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
	min = amg_pixels.min()
	max = amg_pixels.max()
	mean = amg_pixels.mean()
	led_disp.clear(disp=False)
	led_disp.text("Min: %.3f"%min, (0, 2))
	led_disp.text("Max: %.3f"%max, (0, 10))
	led_disp.text("Mean: %.3f"%mean, (0, 18))
	led_disp.show()


"""
Continually refreshes the AMG8833 pixel values and redisplays
"""
def loop_display(amg):
	while True:
		pixels = np.array(amg.pixels)
		display_to_uh(pixels)
		display_to_pioled(pixels)


if __name__ == "__main__":
	i2c = busio.I2C(board.SCL, board.SDA)
	amg = adafruit_amg88xx.AMG88XX(i2c)

	led_disp = PiOLED()
	led_disp.text("Hello There", (0, 2))
	led_disp.show()

	try:
		loop_display(amg)
	finally:
		uh.off()

