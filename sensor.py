import sys, os, math, time, thread, smbus, random, requests
import time
import Adafruit_ADXL345
from time import sleep
import smbus
import string
import Adafruit_BMP.BMP085 as BMP085

accel=Adafruit_ADXL345.ADXL345()
sensor = BMP085.BMP085()
i2c_bus=smbus.SMBus(1)

def getSignedNumber(number):
	if number & (1<<15):
		return number | ~65535
	else:
		return number & 65535

def read_word(address, adr):
    high = i2c_bus.read_byte_data(address, adr)
    low = i2c_bus.read_byte_data(address, adr + 1)
    val = (high << 8) + low
    return val

def read_word_2c(address, adr):
    val = read_word(address, adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val
		
		

i2c_address=0x69
i2c_bus.write_byte_data(i2c_address,0x20,0x0F)
i2c_bus.write_byte_data(i2c_address,0x23,0x20)
addrHMC = 0x1e
i2c_bus.write_byte_data(addrHMC, 0, 0b01110000)  # Set to 8 samples @ 15Hz
i2c_bus.write_byte_data(addrHMC, 1, 0b00100000)  # 1.3 gain LSb / Gauss 1090 (default)
i2c_bus.write_byte_data(addrHMC, 2, 0b00000000)  # Continuous sampling


while True:
	x,y,z=accel.read()
	x2=x/256.0
	y2=y/256.0
	z2=z/256.0
	
	mx = read_word_2c(addrHMC, 3)
	my = read_word_2c(addrHMC, 7)
	mz = read_word_2c(addrHMC, 5)
	mx = mx*0.92
	my = my*0.92
	mz = mz*0.92
	
	i2c_bus.write_byte(i2c_address,0x28)
    	X_L = i2c_bus.read_byte(i2c_address)
    	i2c_bus.write_byte(i2c_address,0x29)
    	X_H = i2c_bus.read_byte(i2c_address)
    	X = X_H << 8 | X_L

    	i2c_bus.write_byte(i2c_address,0x2A)
    	Y_L = i2c_bus.read_byte(i2c_address)
    	i2c_bus.write_byte(i2c_address,0x2B)
    	Y_H = i2c_bus.read_byte(i2c_address)
    	Y = Y_H << 8 | Y_L

    	i2c_bus.write_byte(i2c_address,0x2C)
    	Z_L = i2c_bus.read_byte(i2c_address)
    	i2c_bus.write_byte(i2c_address,0x2D)
    	Z_H = i2c_bus.read_byte(i2c_address)
    	Z = Z_H << 8 | Z_L

    	X = getSignedNumber(X)
    	Y = getSignedNumber(Y)
    	Z = getSignedNumber(Z)

    	X=(X*8.75)/1000
    	Y=(Y*8.75)/1000
    	Z=(Z*8.75)/1000

    	#print string.rjust(`X`, 10),
    	#print string.rjust(`Y`, 10),
    	#print string.rjust(`Z`, 10)
    	#print('Altitude = {0:0.2f} m'.format(sensor.read_altitude()))
	print('ACC:x={0:0.3f},y={1:0.3f},z={2:0.3f};GYRO:x={3:0.3f},y={4:0.3f},z={5:0.3f};MAG:x={6:0.3f},y={7:0.3f},z={8:0.3f};Alti:{9:0.2f}'
	.format(x2,y2,z2,X,Y,Z,mx,my,mz,sensor.read_altitude()))
	time.sleep(0.5)
