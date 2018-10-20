# Displays the pixel values of the AMG8833 to the Pimoroni Unicorn HAT HD



import unicornhathd as uh
import busio
import board
import adafruit_amg88xx
import numpy as np
import math
from scipy.misc import imresize
from PIL import Image

colors = np.array([
	[125, 0, 255],
	[0, 0, 255],
	[0, 255, 255],
	[255, 255, 0],
	[255, 125, 0],
	[255, 0, 0]
])

"""
Fetches the color gradient relative to the fraction ('f') of 0-1.0
"""
def get_color(f):
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
def display(amg_pixels):
	arr = np.array(amg_pixels)
	arr = imresize(arr, (16, 16), interp='lanczos')
	for y in range(arr.shape[0]):
		for x in range(arr.shape[1]):
			f = (arr[y][x] - arr.min()) / (arr.max() - arr.min()) 
			rgb = get_color(f)
			uh.set_pixel(x, y, rgb[0], rgb[1], rgb[2])
	uh.show()

"""
Continually refreshes the AMG8833 pixel values and redisplays
"""
def loop_display(amg):
	while True:
		display(amg.pixels)

if __name__ == "__main__":
	i2c = busio.I2C(board.SCL, board.SDA)
	amg = adafruit_amg88xx.AMG88XX(i2c)
	
	try:
		loop_display(amg)
	finally:
		uh.off()
