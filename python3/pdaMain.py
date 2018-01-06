import RPi.GPIO as GPIO
import math
import time
import os
import timeit
import pdaGps
import multiprocessing
import magnetometerHMC5883L as magnetometer
import signal

#0.0069141387939453
'''def f():
    print "aaaaaaaaaaa"
    print "process f id = " , os.getpid()
    #while True:
    #    y = 2
    
    time.sleep(2)
    print "bbb"
  '''  
    


############################################################
#                    CONFIG                       
'''GPIO.setmode(GPIO.BCM)
GPIO.setup(SHUTDOWN_BUTTON_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
def checkShutdownButton()'''


interrupted = False

def main():
    '''
    print multiprocessing.cpu_count()
    d = multiprocessing.Process(name='daemon', target=f)
    time.sleep(5)

    d.start()
    while True:
        x = 1
    '''
    
    signal.signal(signal.SIGINT, signal_handler)   # CTRL+C
    signal.signal(signal.SIGTERM, signal_handler)  # Kill, shutdown
    
    
    
    
    managerGps = multiprocessing.Manager()
    managerGpsDict = managerGps.dict()
    managerGpsDict.update({"toDo": 0, "magnBearing": 0}) # Is the same as the lines below
    #mpManagerList["toDo"] = 0
    #mpManagerList["magnBearing"] = 0
    # REMEMBER THE ',' IF ONLY ONE ARG IN .Process !!!!!!
    pdaGpsProcess = multiprocessing.Process(name="pdaGpsP", target=pdaGps.mainLoop, args=(managerGpsDict,))
    pdaGpsProcess.start()
    
    
    while not interrupted:         # Program main loop.
        
        # if ((time.time() > pdaGpsLastTimeDraw + pdaGps.GPS_REFRESH_DELAY) and (mpManagerList["pdaGpsBusy"] == 0)):
        managerGpsDict["magnBearing"] = magnetometer.returnBearingDegrees()
            # pdaGpsProcess.join()
        
        time.sleep(0.08)
        
    # DO BELOW BEFORE END PROGRAM ####################################################
    
    pdaGpsProcess.terminate()
    managerGpsDict["toDo"] = 999
    #while (pdaGpsProcess.is_alive()):
    #    time.sleep(0.1)
        
    #print "pdaGpsProcess terminated with code: ", pdaGpsProcess.exitcode
    for i in range(50000):
        print(i)
    #time.sleep(10)
    

def signal_handler(signal, frame):
    global interrupted
    if not interrupted:
        print("Interrupting for signal: ", signal)
    interrupted = True
    
if __name__ == '__main__':
  try:
    main()
  finally:
    GPIO.cleanup()

