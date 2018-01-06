import subprocess
import time
import os
import RPi.GPIO as GPIO
from sys import argv

############################################################
#                    CONFIG                       

HAVE_SHUTDOWN_BUTTON = True
SHUTDOWN_BUTTON_GPIO = 18
#
#

SHUTDOWN_BUTTON_HOLD_TIME = 3
SHUTDOWN_BUTTON_CHECK = 0.1
SHUTDOWN_BUTTON_DELAY = 10

ERROR_INVALID_ARGV = 2
    
# Remember to add '&' at the end of program, to run simultaneously
PROGRAM_1_ACTIVE = True
PROGRAM_1 = "sudo python /home/pi/pda/pdaMain.py &"

############################################################


def shutdown(reboot=False):
    
    if (reboot):
        os.system("sudo reboot now")
        
    else:
        os.system("sudo shutdown -h now") 
                 
                     
def shutdownButton(channel):
    #print ("button pressed")
    timeHolden = 0
    while(GPIO.input(channel)):
        
        time.sleep(SHUTDOWN_BUTTON_CHECK)
        timeHolden += SHUTDOWN_BUTTON_CHECK
        if (timeHolden >= SHUTDOWN_BUTTON_HOLD_TIME):
            
            #print("button holden for "+str(timeHolden)+"miliseconds. Will shutdown after delay.")
            time.sleep(SHUTDOWN_BUTTON_DELAY)
            shutdown()
            #print("Shutdown failed. See autorun.py code.")
            return() # If shutdown fails, at least leave this function.
    
    
    
    
def main ():
    # If argument there is no argument 1 or if it is "boot"
    if ((len(argv) == 1) or (argv[1] == "boot")):
        
        if PROGRAM_1_ACTIVE:
            os.system(PROGRAM_1)
        
        if (HAVE_SHUTDOWN_BUTTON):
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(SHUTDOWN_BUTTON_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
            GPIO.add_event_detect(SHUTDOWN_BUTTON_GPIO, GPIO.RISING, callback = shutdownButton, bouncetime = 100)  
            while True:
                time.sleep(60)
    

    elif (argv[1] == "shutdownRequested"):
        shutdown()
        
    elif (argv[1] == "reboot" ):
        shutdown(True)
        
                
    else:
        print ("Argument \""+argv[1]+"\"invalido. Entre apenas com \"boot\", \"shutdown\" or \"reboot\"")
        exit (ERROR_INVALID_ARGV)

if __name__ == "__main__":
    main()
