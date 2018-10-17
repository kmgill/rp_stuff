import unicornhathd as uh


tl = [255, 0, 0]
bl = [255, 255, 0]
tr = [0, 255, 0]
br = [0, 0, 255]

def linear_interpolate(f, v0, v1):
	return (v0 * f) + (v1 * (1.0 - f))

def linear_interpolate_rgb(f, rgb0, rgb1):
	r = linear_interpolate(f, rgb0[0], rgb1[0])
	g = linear_interpolate(f, rgb0[1], rgb1[1])
	b = linear_interpolate(f, rgb0[2], rgb1[2])
	return (r, g, b)

def bilinear_interpolate_rgb(vf, hf, tl, bl, tr, br):
	top = linear_interpolate_rgb(hf, tl, tr)
	bottom = linear_interpolate_rgb(hf, bl, br)
	c = linear_interpolate_rgb(vf, top, bottom)
	return c


def display(tl, bl, tr, br):
	for x in range(16):
		for y in range(16):
			hf = x / 16.0
			vf = y / 16.0
			c = bilinear_interpolate_rgb(vf, hf, tl, bl, tr, br)
			uh.set_pixel(x, y, c[0], c[1], c[2])

	uh.show()


if __name__ == "__main__":
	display(tl, bl, tr, br)
