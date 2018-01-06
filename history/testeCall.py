
import wiringpi
PIN_TO_SENSE = 18

print "hmm"

def gpio_callback():
    
    print "GPIO_CALLBACK!"

wiringpi.wiringPiSetupGpio()

wiringpi.pinMode(PIN_TO_SENSE, wiringpi.GPIO.INPUT)

wiringpi.pullUpDnControl(PIN_TO_SENSE, wiringpi.GPIO.PUD_DOWN)

wiringpi.wiringPiISR(PIN_TO_SENSE, wiringpi.GPIO.INT_EDGE_RISING, gpio_callback)

while True:
    wiringpi.delay(2000)
