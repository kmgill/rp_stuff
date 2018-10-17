import os
import sys
import numpy as np
from PIL import Image
import unicornhathd as uh



def display_image_array(arr):
	for x in range(16):
		for y in range(16):
			hf = x / 16.0
			vf = y / 16.0
			image_y = int(round(vf * arr.shape[0]))
			image_x = int(round(hf * arr.shape[1]))
			r = arr[image_y][image_x][0]
			g = arr[image_y][image_x][1]
			b = arr[image_y][image_x][2]
			uh.set_pixel(x, y, r, g, b)
	uh.show()

if __name__ == "__main__":
	os.system("fswebcam -r 16x16 --no-banner  image.jpg")

	img = Image.open("image.jpg")
	arr = np.array(img)

	print arr.shape
	display_image_array(arr)
