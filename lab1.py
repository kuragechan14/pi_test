import time
import Adafruit_ADXL345
from time import sleep
import smbus
import string

accel=Adafruit_ADXL345.ADXL345()
def getSignedNumber(number):
	if number & (1<<15):
		return number | ~65535
	else:
		return number & 65535
i2c_bus=smbus.SMBus(1)
i2c_address=0x69
i2c_bus.write_byte_data(i2c_address,0x20,0x0F)
i2c_bus.write_byte_data(i2c_address,0x23,0x20)


while True:
	x,y,z=accel.read()
	x2=x/256.0
	y2=y/256.0
	z2=z/256.0
	print('X={0}, Y={1}, Z={2}'.format(x2,y2,z2))
	time.sleep(0.5)
