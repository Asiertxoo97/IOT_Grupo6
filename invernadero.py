#!/usr/bin/env python

import spidev # To communicate with SPI devices
import math
from time import sleep	
from sys import argv, exit
import sys
import Adafruit_DHT
import time
import requests
import time,sys
import smbus
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17,GPIO.OUT)#Azul
GPIO.setup(27,GPIO.OUT)#Rojo



rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
    bus = smbus.SMBus(1)
else:
    bus = smbus.SMBus(0)
# Este dispositivo tiene dos direcciones (Slave) para controlar el texto y el color
DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e
# set backlight to (R,G,B) (values from 0..255 for each)
def setRGB(r,g,b):
    bus.write_byte_data(DISPLAY_RGB_ADDR,0,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,1,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xaa)
    bus.write_byte_data(DISPLAY_RGB_ADDR,4,r)
    bus.write_byte_data(DISPLAY_RGB_ADDR,3,g)
    bus.write_byte_data(DISPLAY_RGB_ADDR,2,b)
# send command to display (no need for external use)
def textCommand(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)
# set display text \n for second line (or auto wrap)
def setText(text):
    textCommand(0x01) # clear display
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    for c in text:
        if c == '\n' or count == 16:
            count = 0     
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))
#Update the display without erasing the display
def setText_norefresh(text):
    textCommand(0x02) # return home
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    while len(text) < 32: #clears the rest of the screen
        text += ' '
        for c in text:
            if c == '\n' or count == 16:
                count = 0
                row += 1
                if row == 2:
                    break
                textCommand(0xc0)
                if c == '\n':
                    continue
            count += 1
            bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))
                # Create a custom character (from array of row patterns)

spi = spidev.SpiDev()
spi.open(0,0)	

def create_char(location, pattern):
    location &= 0x07 # Make sure location is 0-7
    textCommand(0x40 | (location << 3))
    bus.write_i2c_block_data(DISPLAY_TEXT_ADDR, 0x40, pattern)

#while True:

for x in range(0, 1):
    humidity, temperature = Adafruit_DHT.read_retry(11, 4)
    print("Temp: %s C  Humidity: %s" % (temperature, humidity))
    setText("Tempera: "+str(temperature)+"C"+"\nHumedad: "+str(humidity)+"%")
    setRGB(0,128,0)
    if temperature < 16:
        GPIO.output(27,True)
        setRGB(128,0,0)
    elif temperature > 25:
        GPIO.output(27,True)
        setRGB(145,0,0)
    else:
        GPIO.output(27,False)
        
    if humidity < 30:
        GPIO.output(17,True)
        setRGB(0,0,100)
    elif humidity > 36:
         GPIO.output(17,True)
         setRGB(0,0,128)
    else:
        GPIO.output(17,False)
        
        
    url = "https://corlysis.com:8086/write"
    params = {"db": "invernadero", "u": "token", "p": "0b44a73a3669715e5d93acd7f312e4ff"}
    humidity = "Humedad,place=lab value="+str(humidity)
    temperature = "Temperatura,place=garden value="+str(temperature)
    r1 = requests.post(url, params=params, data=humidity)
    r2 =requests.post(url, params=params, data=temperature)
    
    #time.sleep(0.8)



