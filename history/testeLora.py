# import signal
import wiringpi
import time
# SPI_WRITE_MASK = 0x80

# SPIchannel = 0  # SPI Channel (CE0)
#SPIspeed = 1562500  # Clock Speed in Hz (base 400MHz/256)
#wiringpi.wiringPiSetupGpio()
# wiringpi.wiringPiSetupSys()
# wiringpi.wiringPiSPISetup(SPIchannel, SPIspeed)

'''
'''

def gpio_callback():
    print "CALL BACK!"

PIN_TO_SENSE = 18
wiringpi.wiringPiSetupGpio()

wiringpi.pinMode(PIN_TO_SENSE, wiringpi.GPIO.INPUT)

wiringpi.pullUpDnControl(PIN_TO_SENSE, wiringpi.GPIO.PUD_DOWN)

wiringpi.wiringPiISR(PIN_TO_SENSE, wiringpi.GPIO.INT_EDGE_RISING, gpio_callback)


while True:
    wiringpi.delay(2000)
