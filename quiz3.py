import sys, os, math, time, thread, smbus, random, requests
import time
import Adafruit_ADXL345
from time import sleep
import smbus
import string
import Adafruit_BMP.BMP085 as BMP085
import random
import RPi.GPIO as GPIO
LED_G=11
LED_R=12
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_G,GPIO.OUT)
GPIO.setup(LED_R,GPIO.OUT)
GPIO.setwarnings(False)

accel=Adafruit_ADXL345.ADXL345()
sensor = BMP085.BMP085()
i2c_bus=smbus.SMBus(1)
task=-1
tstart=-1
finish=0

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

task_list=["Shaking (accelerometer)",
        "Heading to North (compass)",
        "Rotate more than 20 degrees (gyro or compass)",
        "Rise up the sensor(altitude)"]
        
def get_acc():
    x,y,z=accel.read()
    ax=x/256.0
    ay=y/256.0
    az=z/256.0
    return ax,ay,az

def get_gry():
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
    gx=(X*8.75)/1000
    gy=(Y*8.75)/1000
    gz=(Z*8.75)/1000
    return gx,gy,gz

def get_mag():
    mx = read_word_2c(addrHMC, 3)
    my = read_word_2c(addrHMC, 7)
    mz = read_word_2c(addrHMC, 5)
    mx = mx*0.92
    my = my*0.92
    mz = mz*0.92
    return mx,my,mz

def get_alt():
    sensor.read_altitude()

def random_task():
    task=random.randint(0,3)
    print("========[New Task]========:",task,task_list[task])
    tstart=time.time()
    finish=0
    oax,oay,oaz=get_acc()
    omx,omy,omz=get_mag()
    ogx,ogy,ogz=get_gry()
    oalt=get_alt()




while True:
    if(task==-1):
        random_task()
    tcurrent=time.time()
    tint=tcurrent-tstart

    if(finish==0):
        if (tint>0 and tint<=3):
            print(tint,"[safe]",task_list[task])
            GPIO.output(LED_G,GPIO.HIGH)
            GPIO.output(LED_R,GPIO.LOW)
        elif (tint>3 and tint<=5):
            print(tint,"[alarm]",task_list[task])
            GPIO.output(LED_R,GPIO.HIGH)
            GPIO.output(LED_G,GPIO.LOW)
        else:
            print('========[Fail]========')
            break
    else:
        print('========[Success]========')
        GPIO.output(LED_R,GPIO.LOW)
        GPIO.output(LED_G,GPIO.LOW)
        task=-1     #refresh

    if (task==0):   #shake
        cax,cay,caz=get_acc()
        print('ACC:x={0:0.3f},y={1:0.3f},z={2:0.3f}'.format(cax,cay,caz))
        if(cax-oax >=5 or cay-oay >=5 or caz-oaz >=5 ):
            finish=1
    elif (task==1):  #north
        cmx,cmy,cmz=get_mag()
        print('MAG:x={0:0.3f},y={1:0.3f},z={2:0.3f}'.format(cmx,cmy,cmz))
        if((cmx-omx > 0 and cmx-omx < 10) or (cmy-omy > 0 and cmy-omy < 10) or (cmz-omz > 0 and cmz-omz < 10)):
            finish=1
    elif (task==2):  #20 degree
        cgx,cgy,cgz=get_gry()
        print('GYRO:x={0:0.3f},y={1:0.3f},z={2:0.3f}'.format(cgx,cgy,cgz))
        if(cgx-ogx >= 20 or cgy-ogy >= 20 or cgz-ogz >=20):
            finish=1
    elif (task==3):  #rise up
        calt=get_alt()
        print('alti:{0:0.2f}'.format(calt))
        if(calt-oalt>=0.3):
            finish=1
    time.sleep(0.5)
