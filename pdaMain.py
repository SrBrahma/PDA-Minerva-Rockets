#!/usr/bin/python
# -*- encoding: utf-8 -*-

import RPi.GPIO as GPIO
import math
import time
from os import system
import sys
import multiprocessing
import keyboard
import gps

# import timeit
# Custom packages:
import I2C_LCD_driver
from pdaConstants import *
import magnetometerHMC5883L as magnetometer
import pdaGraphics
import pdaLoRa

# READ: All these codes (including the packages) were written in a incredibly hurry. There are many bad programming practices,
# such as abusive use of global variables. In the future, more calmly, I intend to improve it.



# About the multiprocessing manager bug (explains the weird code I made): https://stackoverflow.com/a/8644552

logArray = multiprocessing.Array('f', ARRAY_LENGTH)

if (HAVE_SHUTDOWN_BUTTON):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SHUTDOWN_BUTTON_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)


pdaDataDict = {"gpsIsOn": 0, "gpsLat": 0, "gpsLon": 0, "magnBearing": 0}


keysList = [[0]]*128 # isPressed, time last pressed

def getKeyPressEventFunction(key):
    global keysList
    global global_currentGraphicDisplay
    global managerDict
    #print "name = ", key.name, "isStr = ", isinstance(key.name, str)
    #print "code = ", key.scan_code
    #print "time = ", key.time
    if key.scan_code < 128:             # As I remember, keyboard don't >128, but I will leave this here to avoid accessing the list with invalid position.


        if keysList[key.scan_code][0] == 0: # if not pressed yet
            keysList[key.scan_code][0] = 1
            #keysList[key.scan_code][1] = key.time

            if key.name == KEY_CHANGE_ACTIVE_DISPLAY:
                global_currentGraphicDisplay += 1
                if global_currentGraphicDisplay > (QNTY_GRAPHICS_DISPLAYS - 1):
                    global_currentGraphicDisplay = 0

            if global_currentGraphicDisplay == 0:
                managerDict.update({"keyPressed0": key.name})
            elif global_currentGraphicDisplay == 1:
                managerDict["keyPressed1"] = key.name

def getKeyReleaseEventFunction(key):
    global keysList

    if key.scan_code < 128:
        keysList[key.scan_code][0] = 0
        # keysList[key.scan_code][1] = 0 # resets the time

'''
def keyboardInitialize():        # If there was no keyboard connected on boot, an error would occur.
    try:
        keyboard.on_press(getKeyPressEventFunction)          # EVENT
        keyboard.on_release(getKeyReleaseEventFunction)      # EVENT
        return 1
    except:
        return 0
'''

def readGps(managerDict):
    # Listen on port 2947 (gpsd) of localhost
    session = gps.gps("localhost", "2947")
    session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

    try:
        while not managerDict["shutdownRequested"]:
                # GET GPS DATA
            gpsReport = session.next()
            #print gpsReport
            # pdaDataDict = ["gpsLat": 0, "gpsLon": 0, "magnBearing": 0]
            if gpsReport['class'] == 'TPV': # Is this needed?
                tempDict = dict(managerDict["pdaDataDict"])
                if hasattr(gpsReport, 'lon'):
                #print "LON = ", gpsReport.lon
                    tempDict["gpsLon"] = gpsReport.lon
                    if not tempDict["gpsIsOn"]:
                        tempDict["gpsIsOn"] = 1
                else:
                    if tempDict["gpsIsOn"]:
                        tempDict["gpsIsOn"] = 0

                if hasattr(gpsReport, 'lat'):
                #print "LAT = ", gpsReport.lat
                    tempDict["gpsLat"] = gpsReport.lat

                #if hasattr(gpsReport, 'time'):
                #    print "time = ", gpsReport.time

                managerDict["pdaDataDict"] = tempDict

    except:
        pass # If shutted down, a broken pipe exception can/will be raised. This try-except is not needed, however, as the system will shutdown anyway.


def fixStringLcd(string, maxLength):
    if len(string) > maxLength:
        #string = string[len(string) - maxLength + 1:]       # Remove exceding chars to the left
        string = "X" * maxLength

    return (" " * (maxLength - len(string))) + string       # Fill the left with spaces, to clear previous values

def printHealthLcd(init = False):
    global charLcdHealth
    # lcd_display_string (string, row (1~4), column (0~19))
    if init:
        charLcdHealth = I2C_LCD_driver.lcd(CHAR_LCD_HEALTH_I2C_ADDRESS)
                                          #12345678901234567890#
        charLcdHealth.lcd_display_string ("AP    0m | PID     0", 1, 0)
        charLcdHealth.lcd_display_string ("SNR    0 | RSSI    0", 2, 0)
        charLcdHealth.lcd_display_string ("B/s    0 | PGPS  OFF", 3, 0)
        charLcdHealth.lcd_display_string ("READ     | RGPS  OFF", 4, 0)

    else:
        string = str(managerDict["apogee"])
        string = fixStringLcd(string, CHAR_DISPLAY_APOGEE_MAX_LEN)
        charLcdHealth.lcd_display_string (string, 1, CHAR_DISPLAY_APOGEE_BASE_POS - len(string) + 1)

        string = str(int(logArray[(managerDict["logLength"] - 1) * DATA_LIST_VARIABLES + DATA_LIST_PACKET_ID]))
        string = fixStringLcd(string, CHAR_DISPLAY_PID_MAX_LEN)
        charLcdHealth.lcd_display_string (string, 1, PID_BASE_POS - len(string) + 1)


        string = str(int(logArray[(managerDict["logLength"] - 1) * DATA_LIST_VARIABLES + DATA_LIST_SNR]))
        string = fixStringLcd(string, CHAR_DISPLAY_SNR_MAX_LEN)
        charLcdHealth.lcd_display_string (string, 2, CHAR_DISPLAY_SNR_BASE_POS - len(string) + 1)


        string = str(int(logArray[(managerDict["logLength"] - 1) * DATA_LIST_VARIABLES + DATA_LIST_RSSI]))
        string = fixStringLcd(string, CHAR_DISPLAY_RSSI_MAX_LEN)
        charLcdHealth.lcd_display_string (string, 2, CHAR_DISPLAY_RSSI_BASE_POS - len(string) + 1)


        string = str(managerDict["bytePerSecondRF"])
        string = fixStringLcd(string, CHAR_DISPLAY_BPS_MAX_LEN)
        charLcdHealth.lcd_display_string (string, 3, CHAR_DISPLAY_BPS_BASE_POS - len(string) + 1)

        #string = str(int(logArray[(managerDict["logLength"] - 1) * DATA_LIST_VARIABLES + DATA_LIST_SYSTEM_RESETS]))
        #fixStringLcd(string, RSTS_MAX_LEN)
        #charLcdHealth.lcd_display_string (string, 4, RSTS_BASE_POS - len(string) + 1)

        if managerDict["readingRF"]:
            charLcdHealth.lcd_display_string (" ON", 4, 5)
        else:
            charLcdHealth.lcd_display_string ("OFF", 4, 5)

        if managerDict["pdaDataDict"]["gpsIsOn"]:
            charLcdHealth.lcd_display_string (" ON", 3, 17)
        else:
            charLcdHealth.lcd_display_string ("OFF", 3, 17)

        if logArray[managerDict["logLength"] * DATA_LIST_VARIABLES + DATA_LIST_GPS_LAT]:
            charLcdHealth.lcd_display_string (" ON", 4, 17)
        else:
            charLcdHealth.lcd_display_string ("OFF", 4, 17)


def main():
    global global_currentGraphicDisplay
    global managerDict

    global_currentGraphicDisplay = 0
    managerDict = multiprocessing.Manager().dict()

    managerDict.update({"doShutdown0": 0, "doShutdown1": 0, "keyPressed0": 0, "keyPressed1": 0, "shutdownRequested": 0, "logLength": 0, "pdaDataDict": pdaDataDict, "readingRF": 1, "apogee": , "bytePerSecondRF": 0}) # Is the same as the lines below


    # Start display 0
    pdaGraphicProcess0 = multiprocessing.Process(name="pdaDisplay0", target=pdaGraphics.init,
                    #managerDict  pinRW                 pinE    haveReset   pinReset   thisGraphicId initImageId initInDisplayMode
        args=(managerDict, logArray, PIN_DISPLAY0_RW, PIN_DISPLAY0_E, True, PIN_DISPLAYS_RST, 0, DISPLAY_IMAGE_BRAZIL, DISPLAY_MODE_GRAPHIC))
    pdaGraphicProcess0.start()

    # Start display 1
    pdaGraphicProcess1 = multiprocessing.Process(name="pdaDisplay1", target=pdaGraphics.init,
                    #managerDict  pinRW                 pinE    haveReset   pinReset   thisGraphicId initImageId initInDisplayMode
        args=(managerDict, logArray, PIN_DISPLAY1_RW, PIN_DISPLAY1_E, False, PIN_DISPLAYS_RST, 1, DISPLAY_IMAGE_ROCKETS, DISPLAY_MODE_GPS))
    pdaGraphicProcess1.start()

    loraProcess = multiprocessing.Process(name="LoRa", target=pdaLoRa.init, args=(managerDict, logArray))
    loraProcess.start()

    pdaGpsProcess = multiprocessing.Process(name="pdaGps", target=readGps, args=(managerDict,))
    pdaGpsProcess.start()

    keyboard.on_press(getKeyPressEventFunction)          # EVENT
    keyboard.on_release(getKeyReleaseEventFunction)      # EVENT

    if CHAR_LCD_HEALTH_ENABLED:
        printHealthLcd(init = True)

    charLcdHealthLastDrawnTime = 0

    startingTime = time.time()
    magnetometerLastReadTime = 0
    shutdownLastReadTime = 0

    shutdownButtonHolden = 0

    doShutdown = False

    while not doShutdown:         # Program main loop Requested"]:

        if (time.time() >= magnetometerLastReadTime + MAGNETOMETER_INTERVAL):
            tempDict = dict(managerDict["pdaDataDict"])

            tempDict["magnBearing"] = magnetometer.returnBearingDegrees()
            managerDict["pdaDataDict"] = tempDict
            magnetometerLastReadTime = time.time()

        if (time.time() >= shutdownLastReadTime + SHUTDOWN_CHECK_INTERVAL):
            if HAVE_SHUTDOWN_BUTTON:
                if GPIO.input(SHUTDOWN_BUTTON_GPIO):
                    shutdownButtonHolden += SHUTDOWN_CHECK_INTERVAL
                    if shutdownButtonHolden >= SHUTDOWN_BUTTON_HOLD_TIME:
                        doShutdown = True

                else:               # Resets the counter
                    if shutdownButtonHolden: # Checking before assigning instead of assigning all the time is cpu-friendlier
                        shutdownButtonHolden = 0

            if managerDict["shutdownRequested"]:
                doShutdown = True
            shutdownLastReadTime = time.time()

        if CHAR_LCD_HEALTH_ENABLED:
            if time.time() >= charLcdHealthLastDrawnTime + CHAR_LCD_HEALTH_DELAY:
                printHealthLcd()

        time.sleep(0.01)

    # ----- End of loop
    #
    # DO BELOW BEFORE END PROGRAM ####################################################

    managerDict["doShutdown0"] = DO_SHUTDOWN_PRINT_MESSAGE
    managerDict["doShutdown1"] = DO_SHUTDOWN_DRAW_IMAGE

    time.sleep(1.5) # Gives time to the displays to display the shutdown, for the gps process and for the 'LoRa + writing to log' process to stop.
    system("sudo shutdown -h now")


if __name__ == '__main__':
    #try:
    main()
    #finally:
     #   GPIO.cleanup()
