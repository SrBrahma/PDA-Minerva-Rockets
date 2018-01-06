#!/usr/bin/python
import smbus
import time
import math

# Isn't the same code, but in this page explains a little:
# http://bluelemonlabs.blogspot.com.br/2013/08/arduino-simple-compass-with-hmc5883l.html

# The original code was giving me very problematic readings on south readings, so
# after braking my head for some time I changed the original code to meet my needings.
#
# NOTICE: I made these "calibrations" (inverting signal of X, subtracting 160 from Y)
# to work where I live, Rio de Janeiro - Brazil. To work on different places,
# maybe you only need to add a correcting degree to the output, or maybe you will
# need to change these "calibrations".
#
# It is intended to work with the integrated circuits pointing the Earth.
# 

bus = smbus.SMBus(1)
I2C_ADDRESS = 0x1e

def read_byte(adr):
    return bus.read_byte_data(I2C_ADDRESS, adr)

def read_word(adr):
    high = bus.read_byte_data(I2C_ADDRESS, adr)
    low = bus.read_byte_data(I2C_ADDRESS, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def write_byte(adr, value):
    bus.write_byte_data(I2C_ADDRESS, adr, value)

write_byte(0, 0b01110000) # Set to 8 samples @ 15Hz
write_byte(1, 0b00100000) # 1.3 gain LSb / Gauss 1090 (default)
write_byte(2, 0b00000000) # Continuous sampling


# I (HB :D) changed significantly this code. After something like 4 hours, I came to this simple solution.
# The previous code and the explanation of changes are on the bottom. 
def returnBearingDegrees():
    x_out = -read_word_2c(7) # invert signal
    y_out = read_word_2c(3) - 160
    # print "z= ",
    read_word_2c(5) # The z-axis. Must be readen to the magnetometer keep running.

    #print "Bearing degrees: ", math.degrees(math.atan2(y_out, x_out))
    return math.degrees(math.atan2(y_out, x_out))
    
def returnBearingRadians():
    x_out = -read_word_2c(7) # invert signal
    y_out = read_word_2c(3) - 160
    read_word_2c(5) # The z-axis. Must be readen to the magnetometer keep running.

    #print "Bearing radians: ", math.atan2(y_out, x_out)
    return math.atan2(y_out, x_out)
    

# Previous code:

''' Maybe the scale was taken from a table on this datasheet, but on code, this didn't made any sense.
https://cdn-shop.adafruit.com/datasheets/HMC5883L_3-Axis_Digital_Compass_IC.pdf

scale = 0.92

def returnBearingRadians():
    x_out = read_word_2c(3) * scale
    y_out = read_word_2c(7) * scale
    z_out = read_word_2c(5) * scale

    bearing  = math.atan2(y_out, x_out) 
    if (bearing < 0):
        bearing += 2 * math.pi
    
    #print "Bearing: ", bearing
    return bearing
    
    
Outputs I was getting from the previous code:
(without multiplying by the scale, which didn't made any sense on the original code)
I noticed that the X was acting like Y and vice-versa, so I just swapped them
and made a substraction from previousX (now Y) of 160.
Also, the newX should be inverted.
By straigth I meant like a paper laid on a table, without inclinations (it was very hard)

North straight:
x = 330; y = 000; z = -320

West straight:
x = 160; y = 160; z = -320

South straight:
x = -20; y = -20; z = -320

East straight:
x = 170; y = -170; z = -320 '''
 
