import time
import Adafruit_BMP.BMP085 as BMP085
sensor = BMP085.BMP085()

last_y=0

def lowpass(x,last_y):
	return 0.5 * x + 0.5 * last_y

while True:
	x=sensor.read_altitude()
	y=lowpass(x,last_y)
	print('(Low-pass Filter)Altitude={0:0.2f} m'.format(y))
	last_y=y
	time.sleep(0.5)
