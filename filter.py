import Adafruit_BMP.BMP085 as BMP085
sensor = BMP085.BMP085()

last_y=0

def losspass(a,x,last_y):
	y=a*x+(1-a)*last_y
	return y

while True:
	x=sensor.read_altitude
	y=losspass(0.5,x,last_y)
	print('(Low-pass Filter)Altitude={0:0.2f} m'.format(y))
	last_y=y
	time.sleep(0.5)
