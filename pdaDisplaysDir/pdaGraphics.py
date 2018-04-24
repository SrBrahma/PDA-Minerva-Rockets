#!/usr/bin/python
# -*- encoding: utf-8 -*-
# ToDo: Decompose each mode (gps, graph) into a file of a class. 23/04/2018
import glcd12864zw as graphicLCD
import RPi.GPIO as GPIO
#import timeit
import time
from math import ceil, floor, sin, cos, radians, acos, degrees
from pdaConstants import *
from copy import deepcopy

# THIS CODE MUST BE CALLED BY pdaMain.py, with multiprocessing.

THIS_GRAPHIC_ID = 0         # Not really a constant, will change the value on init.
KEY_PRESSED_DICT_KEY = ""
DO_SHUTDOWN_DICT_KEY = ""

GRAPH_X_AXIS_DEFAULT_INFOS_LIST = [
    ["PacketID", "PacketID", 0, 1000, DATA_LIST_PACKET_ID], # 0
    ["Time", "Time(s)", 0, 60 , DATA_LIST_PACKET_TIME]      # 1
    ]

GRAPH_Y_AXIS_DEFAULT_INFOS_LIST = [
        #["GpsSats", "GpsSats", 0, 7, DATA_LIST_GPS_SATS],           # 0     7max explain: It logically will never reach >6 on Earth surface, but nice to see if there was a reception error (if == 7)
        # ["GpsAlt", "GpsAlt(m)", 0, 3500, DATA_LIST_GPS_ALT],        # 0

    ["Bmp180Press", "Bmp180Press(Pa)", 0, 60, DATA_LIST_BMP_180_PRESS], # 1
    ["Bmp180Alt", "Bmp180Alt(m)", 0, 1200, DATA_LIST_BMP_180_ALT],      # 2
    ["Bmp180Temp", "Bmp180Temp(ºC)", 0, 60, DATA_LIST_BMP_180_TEMP],    # 3
    ["AccelX", "AccelX(m/s^2)", -200, 200, DATA_LIST_ACCEL_X],  # 4
    ["AccelY", "AccelY(m/s^2)", -200, 200, DATA_LIST_ACCEL_Y],  # 5
    ["AccelZ", "AccelZ(m/s^2)", -200, 200, DATA_LIST_ACCEL_Z],  # 6
    ["GyroX", "GyroX", -10, 10, DATA_LIST_GYRO_X],              # 7
    ["GyroY", "GyroY", -10, 10, DATA_LIST_GYRO_Y],              # 8
    ["GyroZ", "GyroZ", -10, 10, DATA_LIST_GYRO_Z],              # 9
    ["MagnX", "MagnX", -360, 360, DATA_LIST_MAGN_X],            # 10
    ["MagnY", "MagnY", -360, 360, DATA_LIST_MAGN_Y],            # 11
    ["MagnZ", "MagnZ", -360, 360, DATA_LIST_MAGN_Z]             # 12
    ]


# The defaults variablesId's to be loaded on the graph
global_graphXAxisVarId = 1   # Time
global_graphYAxisVarId = 2   # Altitude

global_autoScaleX = True

# The graphs values are designed to display the maximum of 4algarisms+'-'.
GRAPH_AXIS_INFO_NAME = 0
GRAPH_AXIS_INFO_FULL_NAME = 1
GRAPH_AXIS_INFO_MIN_VALUE = 2
GRAPH_AXIS_INFO_MAX_VALUE = 3
GRAPH_AXIS_INFO_ORIGINAL_LIST_POS = 4

GPS_MODE_FIXED_NORTH = 0
GPS_MODE_VARIABLE_NORTH = 1

# Yeap, I am using global variables. The code is small, and it runs around these variables. Deal with it.
# Maybe I change it on future. YEAH YOU FCKIN NEED TO MAKE IT BETTER I CANT UNDERSTAND A SIT NOW GRR

global_gpsMode = GPS_MODE_FIXED_NORTH
global_graphConnectPoints = 1

global_displayMode = DISPLAY_MODE_GRAPHIC # To remove warnings
global_graphXAxisInfoList = deepcopy(GRAPH_X_AXIS_DEFAULT_INFOS_LIST) # How it is a list inside list, just a "list(listName)" won't do.
global_graphYAxisInfoList = deepcopy(GRAPH_Y_AXIS_DEFAULT_INFOS_LIST)


def init(managerDict, logArray, pinRW, pinE, haveReset, resetPin = 0, thisGraphicId = 0, initImageId = 0, initInDisplayMode = DISPLAY_MODE_GRAPHIC):
    global THIS_GRAPHIC_ID
    global KEY_PRESSED_DICT_KEY
    global DO_SHUTDOWN_DICT_KEY
    global global_gpsMode
    global global_displayMode

    THIS_GRAPHIC_ID = thisGraphicId                              # Reload values, for the possible graphicId change
    KEY_PRESSED_DICT_KEY = "keyPressed" + str(THIS_GRAPHIC_ID)   #
    DO_SHUTDOWN_DICT_KEY = "doShutdown" + str(THIS_GRAPHIC_ID)
    global_displayMode = initInDisplayMode

    global_gpsMode = GPS_MODE_FIXED_NORTH

    graphicLCD.init(pinRW, pinE, haveReset, resetPin)
    graphicLCD.clearDisplay()
    graphicLCD.initTextMode()
    graphicLCD.initGraphicMode()

    if initImageId and SHOW_INIT_IMAGES:
        drawImage(initImageId)
        time.sleep(3)
        # graphicLCD.softClearGraphicDisplay()              # this will be done in the mainLoop.

    mainLoop(managerDict, logArray)





def drawImage(initImageId):
    if initImageId == DISPLAY_IMAGE_ROCKETS:
        graphicLCD.loadBMP12864("minervaRocketsInit.bmp")
    if initImageId == DISPLAY_IMAGE_BRAZIL:
        graphicLCD.loadBMP12864("brazilianFlag.bmp")




def mainLoop(managerDict, logArray):
    previousMode = global_displayMode

    startFromLogId, graphPrevXPos, graphPrevYPos = 0, 0, 0
    hasDrawnAllX = 0
    redrawAll = True

    gpsMagnDegree, gpsPreviousMagnDegree = 0, 0
    gpsDegree, gpsPreviousDegree = 0, 0

    gpsDistance, gpsPreviousDistance = 0, 0

    gpsLastValidPacketId = 0
    gpsLastPacketChecked = 0

    gpsTargetLat = 0
    gpsTargetLon = 0

    do_memDump = False
    while not managerDict[DO_SHUTDOWN_DICT_KEY]:

        if global_displayMode != previousMode:
            redrawAll = True

        if redrawAll:
            graphicLCD.softClearGraphicDisplay(do_memDump = False)

# GRAPH MODE MAIN LOOP
        if global_displayMode == DISPLAY_MODE_GRAPHIC:
            if redrawAll:
                graphDrawAxisInfos(drawBackground = True, drawValues = True, drawNames = True, do_memDump = True)
                redrawAll = False
                startFromLogId = 0
                hasDrawnAllX = 0

            logLength = managerDict["logLength"]

            if global_autoScaleX:
                if global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE] != logArray[global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_ORIGINAL_LIST_POS]]:
                    global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE] = int (logArray[global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_ORIGINAL_LIST_POS]])

                if global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE] < logArray[(logLength - 1) * DATA_LIST_VARIABLES + global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_ORIGINAL_LIST_POS]]:
                    global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE] = int (logArray[(logLength - 1) * DATA_LIST_VARIABLES + global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_ORIGINAL_LIST_POS]])
                    graphDrawAxisInfos(drawValues = True)
                    startFromLogId = 0
                    hasDrawnAllX = 0

            '''
            if global_autoScaleY:
                if global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE] > logArray[global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_ORIGINAL_LIST_POS]]:
                    global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE] = int (logArray[global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_ORIGINAL_LIST_POS]])

                if global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE] < logArray[(logLength - 1) * DATA_LIST_VARIABLES + global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_ORIGINAL_LIST_POS]]:
                    global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE] = int (logArray[(logLength - 1) * DATA_LIST_VARIABLES + global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_ORIGINAL_LIST_POS]])
                    graphDrawAxisInfos(drawValues = True)
                    startFromLogId = 0
                    hasDrawnAllX = 0
            '''

            if (logLength > startFromLogId and not hasDrawnAllX):
                hasDrawnAllX, graphPrevXPos, graphPrevYPos = graphPlotGraphic(logArray, logLength, startFromLogId, graphPrevXPos, graphPrevYPos)
                startFromLogId = logLength
            if global_displayMode != previousMode:
                previousMode = global_displayMode

            time.sleep(GRAPH_REFRESH_DELAY)
        # ----- END OF GRAPH


# GPS MODE MAIN LOOP
        elif global_displayMode == DISPLAY_MODE_GPS:
            gpsMagnDegree = managerDict["pdaDataDict"]["magnBearing"]
            if redrawAll:
                gpsDrawBackground()
                gpsDrawCone(gpsMagnDegree, style = 1)

                gpsPreviousMagnDegree = 0
                gpsDegree, gpsPreviousDegree = 0, 0
                gpsDistance, gpsPreviousDistance = 0, 0

                redrawAll = False
                do_memDump = True

            for gpsLastPacketChecked in range (gpsLastPacketChecked, managerDict["logLength"]):
                if logArray[gpsLastPacketChecked * DATA_LIST_VARIABLES + DATA_LIST_GPS_LAT]:
                    gpsLastValidPacketId = gpsLastPacketChecked
                    gpsTargetLat = logArray[gpsLastPacketChecked * DATA_LIST_VARIABLES + DATA_LIST_GPS_LAT]
                    gpsTargetLon = logArray[gpsLastPacketChecked * DATA_LIST_VARIABLES + DATA_LIST_GPS_LON]

            gpsDistance, gpsDegree = gpsGetDistanceAndAngle(managerDict["pdaDataDict"]["gpsLat"], managerDict["pdaDataDict"]["gpsLon"], gpsTargetLat, gpsTargetLon)

            # Print the distance
            if (abs(gpsDistance - gpsPreviousDistance) > GPS_DISTANCE_THRESHOLD):
                gpsPrintDistance(int(round(gpsDistance)))
                gpsPreviousDistance = gpsDistance
                do_memDump = True

            # Draw the target
            if (abs(gpsDegree - gpsPreviousDegree) > GPS_TARGET_DEGREE_THRESHOLD):
                gpsDrawTarget(gpsPreviousDegree, style = 0)
                gpsDrawTarget(gpsDegree, style = 1)
                gpsPreviousDegree = gpsDegree
                do_memDump = True

            # Draw the magnetometer cone
            if (abs(gpsMagnDegree - gpsPreviousMagnDegree) > GPS_BEARING_DEGREE_THRESHOLD):
                gpsDrawCone(gpsPreviousMagnDegree, style = 0)  # Clears the previous cone
                gpsDrawCone(gpsMagnDegree, style = 1)             # Draws the new cone
                gpsPreviousMagnDegree = gpsMagnDegree
                do_memDump = True

            if do_memDump:
                graphicLCD.memDump()
                do_memDump = False

            if global_displayMode != previousMode:
                previousMode = global_displayMode

            time.sleep(GPS_REFRESH_DELAY)
        # ----- END OF GPS

        # Open menu
        if managerDict[KEY_PRESSED_DICT_KEY] in KEY_OPEN_MENU_STR_LIST:
            managerDict[KEY_PRESSED_DICT_KEY] = ""
            drawAndControlMenu(managerDict)
            redrawAll = True

        # Change active display blink
        if managerDict[KEY_PRESSED_DICT_KEY] == KEY_CHANGE_ACTIVE_DISPLAY:
            blinkScreen()
            managerDict[KEY_PRESSED_DICT_KEY] = ""

    drawShutdown(managerDict[DO_SHUTDOWN_DICT_KEY])
    time.sleep(5) # Avoids breaking the multiprocessing pipe prematurely


def drawShutdown(mode):
    graphicLCD.softClearGraphicDisplay()
    if mode == DO_SHUTDOWN_DRAW_IMAGE:
        drawImage(DISPLAY_IMAGE_ROCKETS)

    elif mode == DO_SHUTDOWN_PRINT_MESSAGE:
        graphicLCD.clearDisplay()
        graphicLCD.initTextMode() # Graphic mode can't be active when going to print in text mode.
                                       #================#
        graphicLCD.printStringTextMode("> SHUTTING DOWN!", 0, 0)
        graphicLCD.printStringTextMode("Please wait 10s ", 0, 1)
        graphicLCD.printStringTextMode("before powering" , 0, 2)
        graphicLCD.printStringTextMode("off.  MINERVA! " , 0, 3)

GRAPH_0_OF_X_AXIS_X_POS = 7
GRAPH_MAX_OF_X_AXIS_X_POS = 119
GRAPH_X_DIST = GRAPH_MAX_OF_X_AXIS_X_POS - GRAPH_0_OF_X_AXIS_X_POS

GRAPH_0_OF_Y_AXIS_Y_POS = 56
GRAPH_MAX_OF_Y_AXIS_Y_POS = 8
GRAPH_Y_DIST = GRAPH_0_OF_Y_AXIS_Y_POS - GRAPH_MAX_OF_Y_AXIS_Y_POS

GRAPH_REFRESH_DELAY = 0.2


# The first return is "if has drawn all the X axis variable".
# There is a ambiguity in dataCoords/graphicDisplayCoords, be careful. On future I will improve it, but THERE IS NO TIME FOR IT HELP ME
def graphPlotGraphic(logList, logLength, startFromLogId, prevXPos, prevYPos):
    xDataMin = global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE]
    xDataMax = global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE]
    relativeXDataMax = float(xDataMax - xDataMin) # Float to make the division on xPos calc a float.

    yDataMin = global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE]
    yDataMax = global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE]
    relativeYDataMax = float(yDataMax - yDataMin)

    if (relativeXDataMax and relativeYDataMax): # If they aren't equal to 0 (would make a division by 0 in the code)

        for logId in range (startFromLogId, logLength):

            xValue = logList[logId * DATA_LIST_VARIABLES + global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_ORIGINAL_LIST_POS]]
            if xValue < global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE]:
                xValue = global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE]
                graphicLCD.drawVerticalLine(GRAPH_0_OF_X_AXIS_X_POS, GRAPH_MAX_OF_Y_AXIS_Y_POS + 4, GRAPH_0_OF_Y_AXIS_Y_POS - 4, use_memPlot = 1)

            elif xValue > global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE]:
                graphicLCD.drawVerticalLine(GRAPH_MAX_OF_X_AXIS_X_POS, GRAPH_MAX_OF_Y_AXIS_Y_POS + 4, GRAPH_0_OF_Y_AXIS_Y_POS - 4, use_memPlot = 1)
                graphicLCD.memDump()
                return 1, GRAPH_MAX_OF_X_AXIS_X_POS, GRAPH_0_OF_Y_AXIS_Y_POS # Returns the position maxOfX, 0ofY, so the nexts functions call with connect points wont mess the graph.

                xValue = global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE]

            yValue = logList[logId * DATA_LIST_VARIABLES + global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_ORIGINAL_LIST_POS]]
            if yValue < global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE]:
                yValue = global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE]

            elif yValue > global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE]:
                yValue = global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE]

            xPos = int(round((((xValue - xDataMin) / relativeXDataMax) * GRAPH_X_DIST) + GRAPH_0_OF_X_AXIS_X_POS))
            yPos = int(round(GRAPH_0_OF_Y_AXIS_Y_POS - ((((yValue - yDataMin) / relativeYDataMax)) * GRAPH_Y_DIST)))

            if global_graphConnectPoints:
                if logId > 0:
                    graphicLCD.drawGenericLine(prevXPos, prevYPos, xPos, yPos, use_memPlot = 1)

                else:
                    graphicLCD.memPlot(xPos, yPos)

                prevXPos = xPos
                prevYPos = yPos

            else:
                graphicLCD.memPlot(xPos, yPos)

        graphicLCD.memDump()
        return 0, xPos, yPos
    # -=-=-=- End of if(relativeXDataMax and relativeYDataMax)
    else:
        return GRAPH_0_OF_X_AXIS_X_POS, GRAPH_0_OF_Y_AXIS_Y_POS




def graphDrawAxisInfos(drawBackground = False, drawValues = False, drawNames = False, do_memDump = False):
    # I could do "drawXValues" and "drawYValues", instead of just "drawValues", but no. The code would get bigger for a small
    # amount of performance, when drawing the new values.
    if drawBackground:
        graphicLCD.drawRectangle(6, 7, 120, 57, use_memPlot = 1)

        graphicLCD.memPlot(5, GRAPH_MAX_OF_Y_AXIS_Y_POS) # graphY = y      ON LEFT
        graphicLCD.memPlot(5, 32) # graphY = y/2
        graphicLCD.memPlot(5, GRAPH_0_OF_Y_AXIS_Y_POS) # graphY = 0

        graphicLCD.memPlot(121, GRAPH_MAX_OF_Y_AXIS_Y_POS) # graphY = y    ON LEFT
        graphicLCD.memPlot(121, 32) # graphY = y/2
        graphicLCD.memPlot(121, GRAPH_0_OF_Y_AXIS_Y_POS) # graphY = 0

        graphicLCD.memPlot(GRAPH_0_OF_X_AXIS_X_POS, 58) # graphX = 0      ON BOTTON
        graphicLCD.memPlot(35, 58) # graphX = x/4
        graphicLCD.memPlot(63, 58) # graphX = 2x/4
        graphicLCD.memPlot(91, 58) # graphX = 3x/4
        graphicLCD.memPlot(GRAPH_MAX_OF_X_AXIS_X_POS, 58) # graphX = 3x/4

        graphicLCD.memPlot(GRAPH_0_OF_X_AXIS_X_POS, 6) # graphX = 0      ON TOP
        graphicLCD.memPlot(35, 6) # graphX = x/4
        graphicLCD.memPlot(63, 6) # graphX = 2x/4
        graphicLCD.memPlot(91, 6) # graphX = 3x/4
        graphicLCD.memPlot(GRAPH_MAX_OF_X_AXIS_X_POS, 6) # graphX = 3x/4

    # Print axis names
    if drawNames:
        xName = global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_FULL_NAME]
        yName = global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_FULL_NAME]
        graphicLCD.drawRectangle(5, 0, 127, 5, fill = 1, style = 0, use_memPlot = 1)
        graphicLCD.drawRectangle(122, 6, 127, 58, fill = 1, style = 0, use_memPlot = 1)
        graphicLCD.printString3x5(xName, 63, 0, rotation = 0, align = 1, use_memPlot = 1)
        graphicLCD.printString3x5(yName, 123, 31, rotation = 1, align = 1, use_memPlot = 1)

    if drawValues:
        xMin = global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE]
        xMax = global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE]
        yMin = global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE]
        yMax = global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE]

        xDist = (xMax - xMin) / 4
        yDist = (yMax - yMin) / 2

        # Print the x-axis values
        graphicLCD.drawRectangle(8, 59, 127, 63, fill = 1, style = 0, use_memPlot = 1) # Clears previous values on screen

        numberStr = str(xMin)
        graphicLCD.printString3x5(numberStr, 8, 59, 0, use_memPlot = 1)

        numberStr = str(xMin + xDist)
        if len(numberStr) == 1:
            strPosX = 32
        elif len(numberStr) == 2:
            strPosX = 32
        elif len(numberStr) == 3:
            strPosX = 32
        elif len(numberStr) == 4:
            strPosX = 32
        else:
            strPosX = 32
        if xMin + xDist < 0:        # If negative.. (the '-' char in the 3x5 font is just 2pixels wide)
            strPosX += 1
        graphicLCD.printString3x5(numberStr, strPosX, 59, 0, 0, use_memPlot = 1)

        numberStr = str(xMin + xDist*2)
        if len(numberStr) == 1:
            strPosX = 60
        elif len(numberStr) == 2:
            strPosX = 56
        elif len(numberStr) == 3:
            strPosX = 56
        elif len(numberStr) == 4:
            strPosX = 56
        else:
            strPosX = 56
        if xMin + xDist*2 < 0:        # If negative.. (the '-' char in the 3x5 font is just 2pixels wide)
            strPosX += 1
        graphicLCD.printString3x5(numberStr, strPosX, 59, 0, use_memPlot = 1)

        numberStr = str(xMin + xDist*3)
        if len(numberStr) == 1:
            strPosX = 88
        elif len(numberStr) == 2:
            strPosX = 84
        elif len(numberStr) == 3:
            strPosX = 84
        elif len(numberStr) == 4:
            strPosX = 80
        else:
            strPosX = 80
        if xMin + xDist*3 < 0:        # If negative.. (the '-' char in the 3x5 font is just 2pixels wide)
            strPosX += 1
        graphicLCD.printString3x5(numberStr, strPosX, 59, 0, use_memPlot = 1)

        numberStr = str(xMax)
        if len(numberStr) == 1:
            strPosX = 116
        elif len(numberStr) == 2:
            strPosX = 116
        elif len(numberStr) == 3:
            strPosX = 112
        elif len(numberStr) == 4:
            strPosX = 108
        else:
            strPosX = 108
        if xMax < 0:        # If negative.. (the '-' char in the 3x5 font is just 2pixels wide)
            strPosX += 1
        graphicLCD.printString3x5(numberStr, strPosX, 59, 0, use_memPlot = 1)

        # Print the y-axis values
        graphicLCD.drawRectangle(0, 0, 4, 63, fill = 1, style = 0, use_memPlot = 1) # Clears previous values on screen

        numberStr = str(yMin)
        if len(numberStr) == 1:
            strPosY = 55
        elif len(numberStr) == 2:
            strPosY = 59
        elif len(numberStr) == 3:
            strPosY = 63
        else: # > 3
            strPosY = 63
        if yMin < 0:        # If negative.. (the '-' char in the 3x5 font is just 2pixels wide)
            strPosY -= 1
        graphicLCD.printString3x5(numberStr, 0, strPosY, rotation = 1, use_memPlot = 1)

        numberStr = str(yMin + yDist)
        if len(numberStr) == 1:
            strPosY = 35
        elif len(numberStr) == 2:
            strPosY = 35
        elif len(numberStr) == 3:
            strPosY = 39
        elif len(numberStr) == 4:
            strPosY = 39
        else: # > 4
            strPosY = 43
        if (yMin + yDist) < 0:        # If negative.. (the '-' char in the 3x5 font is just 2pixels wide)
            strPosY -= 1
        graphicLCD.printString3x5(numberStr, 0, strPosY, rotation = 1, use_memPlot = 1)

        numberStr = str(yMax)
        if len(numberStr) == 1:
            strPosY = 11
        elif len(numberStr) == 2:
            strPosY = 11
        elif len(numberStr) == 3:
            strPosY = 11
        elif len(numberStr) == 4:
            strPosY = 15
        else:
            strPosY = 19
        if yMax < 0:        # If negative.. (the '-' char in the 3x5 font is just 2pixels wide)
            strPosY -= 1
        graphicLCD.printString3x5(numberStr, 0, strPosY, rotation = 1, use_memPlot = 1)

    if do_memDump:
        graphicLCD.memDump()

def blinkScreen(): # To use when changing the screen.
    graphicLCD.drawRectangle(0, 0, 127, 63, style = 2, use_memPlot = 1)
    graphicLCD.memDump()
    #time.sleep(0.1)
    graphicLCD.drawRectangle(0, 0, 127, 63, style = 2, use_memPlot = 1)
    graphicLCD.memDump()

# ==============================================================
#                       GPS CONFIGURATIONS
# ==============================================================
GPS_CONE_RADIUS_PX = 20
GPS_CONE_WIDENESS_DEGREE = 30 # The angle between the pole and the center.

EARTH_RADIUS = 6378100 #meters

GPS_CIRCLE_RADIUS = GPS_CONE_RADIUS_PX + 3

GPS_TARGET_DIST = GPS_CIRCLE_RADIUS + 3
GPS_TARGET_DEGREE_THRESHOLD = 2

GPS_CENTER_X = 63
GPS_CENTER_Y = 31

GPS_BEARING_DEGREE_ADD = 0
GPS_BEARING_DEGREE_THRESHOLD = 2     # Only updates the rotational cone/north if the bearing changed >= this degree

GPS_REFRESH_DELAY = 0.1 # Actually should be 0.066667 (the magnetometer refresh rate, 15Hz = 1.0/15.0s),
# but I will leave a little more to avoid same readings. AND FOR SAVING POWER

GPS_FIXED_NORTH_LEFT_X = GPS_CENTER_X - 2
GPS_FIXED_NORTH_TOP_Y = 0

GPS_DISTANCE_THRESHOLD = 1

GPS_DISTANCE_HEADER_LEFT_X = 2
GPS_DISTANCE_TOP_Y = 59
GPS_DISTANCE_HEADER_STRING = "Distance = "
GPS_DISTANCE_MAX_ALGARISMS = 4
GPS_DISTANCE_MAX_LENGTH = graphicLCD.get3x5StringWidth("X" * (GPS_DISTANCE_MAX_ALGARISMS + 1))    # With the "m" on the end.
GPS_DISTANCE_LEFT_X = graphicLCD.get3x5StringWidth(GPS_DISTANCE_HEADER_STRING) + GPS_DISTANCE_HEADER_LEFT_X + 2
GPS_DISTANCE_RIGHT_X =  GPS_DISTANCE_LEFT_X + GPS_DISTANCE_MAX_LENGTH     # Is aligned to right
# ==============================================================
#                          GPS FUNCTIONS
# ==============================================================

def gpsGetDistanceAndAngle(lat1,lon1,lat2,lon2):
    earthAngle = sin(radians(lat1)) * sin(radians(lat2)) + cos(radians(lat1)) * cos(radians(lat2)) * cos(radians(lon2-lon1))
    if lat1 == lat2:        # Avoids division by 0
        bearingDegrees = 0
    else:
        bearingDegrees = degrees((lon1 - lon2) / (lat1 - lat2))
    return acos(earthAngle) * EARTH_RADIUS, bearingDegrees

def gpsDrawTarget(bearingDegrees, style):
    # Center point
    posX = int(round(cos(radians(bearingDegrees)) * GPS_TARGET_DIST + GPS_CENTER_X))
    posY = int(round(sin(radians(bearingDegrees)) * (- GPS_TARGET_DIST) + GPS_CENTER_Y))
    graphicLCD.memPlot(posX,     posY,     style)
    graphicLCD.memPlot(posX,     posY - 1, style)
    graphicLCD.memPlot(posX - 1, posY,     style)
    graphicLCD.memPlot(posX + 1, posY,     style)
    graphicLCD.memPlot(posX,     posY + 1, style)

def gpsPrintDistance(distanceToTarget):
    graphicLCD.drawRectangle(GPS_DISTANCE_LEFT_X, GPS_DISTANCE_TOP_Y, GPS_DISTANCE_RIGHT_X, GPS_DISTANCE_TOP_Y + 4, fill = 1, style = 0, use_memPlot = 1)
    string = str(distanceToTarget)
    if len(string) > GPS_DISTANCE_MAX_ALGARISMS:
        string = ">10k"
    string += "m"
    graphicLCD.printString3x5(string, GPS_DISTANCE_RIGHT_X, GPS_DISTANCE_TOP_Y, align = 2, use_memPlot = 1)

def gpsDrawBackground():
    graphicLCD.printString3x5(GPS_DISTANCE_HEADER_STRING, GPS_DISTANCE_HEADER_LEFT_X, GPS_DISTANCE_TOP_Y, use_memPlot = 1)
    graphicLCD.drawCircle(GPS_CENTER_X, GPS_CENTER_Y, 23, startDegree = 1, stopDegree = 360, stepDegree = 1, use_memPlot = 1)
    gpsPrintDistance(0)
    #graphicLCD.drawRectangle(5, 5, 122, 57, 0, use_memPlot = 1)
        # Draws the north symbol
    if (global_gpsMode == GPS_MODE_FIXED_NORTH):
        graphicLCD.drawVerticalLine(GPS_FIXED_NORTH_LEFT_X,     GPS_FIXED_NORTH_TOP_Y, 3, use_memPlot = 1)
        graphicLCD.memPlot(GPS_FIXED_NORTH_LEFT_X + 1,          GPS_FIXED_NORTH_TOP_Y + 1)
        graphicLCD.memPlot(GPS_FIXED_NORTH_LEFT_X + 2,          GPS_FIXED_NORTH_TOP_Y + 2)
        graphicLCD.drawVerticalLine(GPS_FIXED_NORTH_LEFT_X + 3, GPS_FIXED_NORTH_TOP_Y, 3, use_memPlot = 1)

def gpsDrawCone(magnetometerBearingDegree, style = 1):
    if (global_gpsMode == GPS_MODE_FIXED_NORTH):
        degree = magnetometerBearingDegree + GPS_BEARING_DEGREE_ADD
        # Draw rotational cone
        graphicLCD.drawRadiusLine(GPS_CENTER_X, GPS_CENTER_Y, (degree - GPS_CONE_WIDENESS_DEGREE), GPS_CONE_RADIUS_PX, style, use_memPlot = 1)
        graphicLCD.drawRadiusLine(GPS_CENTER_X, GPS_CENTER_Y, (degree + GPS_CONE_WIDENESS_DEGREE), GPS_CONE_RADIUS_PX, style, use_memPlot = 1)
        if not style:
            graphicLCD.drawRectangle(GPS_CENTER_X - 1, GPS_CENTER_Y - 1, GPS_CENTER_X + 1, GPS_CENTER_Y + 1, fill = 1, style = 0, use_memPlot = 1)
        else:
            graphicLCD.drawRectangle(GPS_CENTER_X - 1, GPS_CENTER_Y - 1, GPS_CENTER_X + 1, GPS_CENTER_Y + 1, fill = 1, style = 2, use_memPlot = 1)


# ==============================================================
#                      MENU CONFIGURATIONS
# ==============================================================
#
# ==============================
# About the menu WINDOW, which will have everything inside it.
# NOTE!! All positions must have these 2~4 constants below as reference (directly or indirectly)
#
MENU_LEFT_X = 24                            # Where (x) the big rectangle starts
MENU_TOP_Y = 9                              # Where (y) the big rectangle starts
MENU_RIGHT_X = MENU_LEFT_X + 79             # Where (x) the big rectangle ends
MENU_BOTTOM_Y = MENU_TOP_Y + 46             # Where (y) the big rectangle starts
#
# ==============================
#
#  About the MENU NAME
MENU_NAME_FONT_HEIGHT = 5

MENU_NAME_LEFT_X = MENU_LEFT_X + 3
MENU_NAME_MAX_RIGHT_X = MENU_RIGHT_X - 10
MENU_NAME_TOP_Y = MENU_TOP_Y + 2
MENU_NAME_BOTTOM_Y = MENU_NAME_TOP_Y + MENU_NAME_FONT_HEIGHT - 1
#
# ==============================
#
# About the little DECORATION on the right of the menu name
MENU_DECORATION_LEFT_X = MENU_RIGHT_X - 6
MENU_DECORATION_RIGHT_X = MENU_DECORATION_LEFT_X + 3
MENU_DECORATION_TOP_Y = MENU_NAME_TOP_Y
#
# ==============================
#
# The LINE SEPARATING the menu name from the options
MENU_NAME_SEPARATOR_Y = MENU_TOP_Y + 8     # Where (y) is the line separating the menu name from the options
#
# ==============================
#
# The boundaries of the active SCROLL
MENU_SCROLL_OUTLINE_LEFT_X = MENU_RIGHT_X - 6                               # Where (x) the outline from the scroll rectangle starts
MENU_SCROLL_OUTLINE_RIGHT_X = MENU_SCROLL_OUTLINE_LEFT_X + 3                # Where (x) the outline from the scroll rectangle ends
MENU_SCROLL_OUTLINE_TOP_Y = MENU_NAME_SEPARATOR_Y + 3                       # Where (y) the outline from the scroll rectangle starts
MENU_SCROLL_OUTLINE_BOTTOM_Y = MENU_BOTTOM_Y - 3                            # Where (y) the outline from the scroll rectangle ends

MENU_SCROLL_LEFT_X = MENU_SCROLL_OUTLINE_LEFT_X + 1
MENU_SCROLL_RIGHT_X = MENU_SCROLL_OUTLINE_RIGHT_X - 1
MENU_SCROLL_TOP_Y = MENU_SCROLL_OUTLINE_TOP_Y + 1
MENU_SCROLL_BOTTOM_Y = MENU_SCROLL_OUTLINE_BOTTOM_Y - 1
MENU_SCROLL_MAX_HEIGHT = MENU_SCROLL_OUTLINE_BOTTOM_Y - MENU_SCROLL_OUTLINE_TOP_Y - 1
#
# ==============================
#
# About the selectable OPTIONS
MENU_OPTIONS_LEFT_X = MENU_LEFT_X + 3 # Where (x) the options starts
MENU_OPTIONS_MAX_RIGHT_X = MENU_OPTIONS_LEFT_X + 55
MENU_OPTIONS_MAX_PX_WIDTH = MENU_OPTIONS_MAX_RIGHT_X - MENU_OPTIONS_LEFT_X # "Connect Points" ~12~15 chars, deppending their wideness
MENU_OPTIONS_TOP_Y = MENU_NAME_SEPARATOR_Y + 3  # Where (y) the first option starts
#
MENU_OPTIONS_MAX_QUANTITY_DISPLAY = 5
MENU_OPTIONS_MIDDLE_OPTION = 3         # The relative option to keep centered when scrolling
MENU_OPTIONS_FONT_HEIGHT = 5
MENU_OPTIONS_Y_SEPARATOR = 2           # The y distance between the options
MENU_OPTIONS_TOTAL_Y_DISTANCE = MENU_OPTIONS_FONT_HEIGHT + MENU_OPTIONS_Y_SEPARATOR

#
    # CHECK position
MENU_OPTIONS_CHECK_BOX_LEFT_X = MENU_LEFT_X + 65
MENU_OPTIONS_CHECK_BOX_RIGHT_X = MENU_OPTIONS_CHECK_BOX_LEFT_X + 4
MENU_OPTIONS_CHECK_BOX_ADD_Y = 4       # Used to draw the box, with drawRectangle function
MENU_OPTIONS_CHECK_CIRCLE_LEFT_X = MENU_LEFT_X + 66                          # The Y positions of the circle I won't cover here.
MENU_OPTIONS_CHECK_CIRCLE_RIGHT_X = MENU_OPTIONS_CHECK_CIRCLE_LEFT_X + 2     # Check the menuDrawOptions function to change it.
MENU_OPTIONS_CHECK_POINT_X = MENU_OPTIONS_CHECK_BOX_LEFT_X + 2
MENU_OPTIONS_CHECK_POINT_ADD_Y = 2     # Used to put a pixel inside the check (optionY + thisConstant)
#
    # INVERT hovered option
MENU_OPTIONS_INVERT_HOVERED_LEFT_X = MENU_OPTIONS_LEFT_X - 1
MENU_OPTIONS_INVERT_HOVERED_RIGHT_X = MENU_OPTIONS_INVERT_HOVERED_LEFT_X + 57
MENU_OPTIONS_INVERT_BOTTOM_ADD_Y = 6
#
# ==============================
#
# Text ENTRY box
MENU_ENTRY_LEFT_X = MENU_LEFT_X + 13
MENU_ENTRY_RIGHT_X = MENU_RIGHT_X - 13
MENU_ENTRY_TOP_Y = MENU_TOP_Y + 11
MENU_ENTRY_BOTTOM_Y = MENU_BOTTOM_Y - 11

MENU_ENTRY_NAME_CENTERED_X = int(floor((MENU_ENTRY_RIGHT_X + MENU_ENTRY_LEFT_X) / 2)) # int should already do floor function, but whatever.
MENU_ENTRY_NAME_TOP_Y = MENU_ENTRY_TOP_Y + 4

MENU_ENTRY_TEXT_BOX_LEFT_X = MENU_ENTRY_LEFT_X + 3
MENU_ENTRY_TEXT_BOX_RIGHT_X = MENU_ENTRY_RIGHT_X - 3
MENU_ENTRY_TEXT_BOX_TOP_Y = MENU_ENTRY_TOP_Y + 12
MENU_ENTRY_TEXT_BOX_BOTTOM_Y = MENU_ENTRY_BOTTOM_Y - 4

MENU_ENTRY_TEXT_CENTERED_X = MENU_ENTRY_NAME_CENTERED_X
MENU_ENTRY_TEXT_TOP_Y = MENU_ENTRY_TEXT_BOX_TOP_Y + 2
#
# ==============================
#
# OPTIONS dictionary
#
MENU_OPTIONS_DICT_MENU_NAME = 0
MENU_OPTIONS_DICT_OPTIONS = 1

# Options LIST
# [["name to write", onlyDisplaysValue, functionToCall, variable, isCheckType, #optional# valueToCheckCircle], [other options]]
#
MENU_OPTIONS_LIST_NAME = 0
    # "name to write":
    # the string to be displayed in the option.

MENU_OPTIONS_LIST_ONLY_DISPLAYS_VALUE = 1
    # This "option" won't be a selectable option, will only display the variable value.

MENU_OPTIONS_LIST_FUNCTION = 2
    # The function to call, when this option is selected.

MENU_OPTIONS_LIST_VARIABLE = 3
    # variable:
    # 1) if the option isn't really a option (onlyDisplaysValue == True);
            # only a display of a value, this variable will be displayed.
    # 2) if the option has a check (isCheckType != 0), the check will be on/off depending the variable value.
    # NOTE: the variable is merely output.

MENU_OPTIONS_LIST_CHECK = 4
    # isCheckType:
    # 0 - it is no check type

MENU_OPTIONS_LIST_CHECK_CIRCLE = 1
    # 1 - Check circle

MENU_OPTIONS_LIST_CHECK_BOX = 2
    # 2 - Check box

MENU_OPTIONS_LIST_VALUE_TO_CHECK_CIRCLE = 5
    # if isCheckType == MENU_OPTIONS_LIST_CHECK_CIRCLE, the

# ==============================




# ==============================================================
#                   DRAW AND CONTROL MENU FUNCTION
# ==============================================================
def drawAndControlMenu(managerDict): # Menu designed to have 4 options showing at a time (5 was too tall, looked strange on )

    def menuClearArea(everything = False, allInside = False, menuName = False, options = False, scrollbar = False,  do_memDump = False):
        if everything:
            graphicLCD.drawRectangle(MENU_LEFT_X, MENU_TOP_Y, MENU_RIGHT_X, MENU_BOTTOM_Y, fill = 1, style = 0, use_memPlot = 1)

        if allInside:
            graphicLCD.drawRectangle(MENU_LEFT_X + 1, MENU_TOP_Y + 1, MENU_RIGHT_X - 1, MENU_BOTTOM_Y - 1, fill = 1, style = 0, use_memPlot = 1)

        if menuName:
            graphicLCD.drawRectangle(MENU_NAME_LEFT_X, MENU_NAME_TOP_Y, MENU_NAME_MAX_RIGHT_X, MENU_NAME_BOTTOM_Y, fill = 1, style = 0, use_memPlot = 1)

        if options:
            graphicLCD.drawRectangle(MENU_LEFT_X + 2, MENU_NAME_SEPARATOR_Y + 2, MENU_OPTIONS_CHECK_BOX_RIGHT_X, MENU_BOTTOM_Y - 2, fill = 1, style = 0, use_memPlot = 1)

        if scrollbar:
            graphicLCD.drawRectangle(MENU_SCROLL_LEFT_X, MENU_SCROLL_TOP_Y, MENU_SCROLL_RIGHT_X, MENU_SCROLL_BOTTOM_Y, fill = 1, style = 0, use_memPlot = 1)

        if do_memDump:
            graphicLCD.memDump()

    def menuDrawBasicWindow():
        # Draws the menu window
        graphicLCD.drawRectangle(MENU_LEFT_X, MENU_TOP_Y, MENU_RIGHT_X, MENU_BOTTOM_Y, use_memPlot = 1)
            # Clears the previous content inside the menu window
        menuClearArea(allInside = True)
        # Draws the decoration on the right of the menu name
        graphicLCD.drawHorizontalLine(MENU_DECORATION_TOP_Y, MENU_DECORATION_LEFT_X, MENU_DECORATION_RIGHT_X, use_memPlot = 1)
        graphicLCD.drawHorizontalLine(MENU_DECORATION_TOP_Y+2, MENU_DECORATION_LEFT_X, MENU_DECORATION_RIGHT_X, use_memPlot = 1)
        graphicLCD.drawHorizontalLine(MENU_DECORATION_TOP_Y+4, MENU_DECORATION_LEFT_X, MENU_DECORATION_RIGHT_X, use_memPlot = 1)
        # Draws the separator of the menu name and the menu options
        graphicLCD.drawHorizontalLine(MENU_NAME_SEPARATOR_Y, MENU_LEFT_X + 1, MENU_RIGHT_X - 1, use_memPlot = 1)
        # Draws the scroll outline
        graphicLCD.drawRectangle(MENU_SCROLL_OUTLINE_LEFT_X, MENU_SCROLL_OUTLINE_TOP_Y,
                                 MENU_SCROLL_OUTLINE_RIGHT_X, MENU_SCROLL_OUTLINE_BOTTOM_Y, use_memPlot = 1)
        # Clear the pixels inside the options area (includes: options name, check symbol and the invert rectangle (current option)

    def menuDrawName(string):
        menuClearArea(menuName = True)
        graphicLCD.printString3x5(string, MENU_NAME_LEFT_X, MENU_NAME_TOP_Y, use_memPlot = 1)

    def menuDrawScrollbars(optionsAmount, idOfTopOption):
        menuClearArea(scrollbar = True)
        optionsToShow = MENU_OPTIONS_MAX_QUANTITY_DISPLAY
        if (optionsAmount < MENU_OPTIONS_MAX_QUANTITY_DISPLAY):
            optionsToShow = optionsAmount
        scrollSize = MENU_SCROLL_MAX_HEIGHT * optionsToShow / float (optionsAmount)
        hiddenOptions = optionsAmount - optionsToShow
        if hiddenOptions:
            scrollStepPosY = (MENU_SCROLL_MAX_HEIGHT - scrollSize) / hiddenOptions
        else:
            scrollStepPosY = 0
        scrollPosY = MENU_SCROLL_TOP_Y + scrollStepPosY * idOfTopOption
        graphicLCD.drawRectangle(MENU_SCROLL_LEFT_X, int(round(scrollPosY)), MENU_SCROLL_RIGHT_X, int(round(scrollPosY + scrollSize)), fill = 1, use_memPlot = 1)

    def menuDrawOptions(optionsList, optionsAmount, idOfTopOption):
        menuClearArea(options = True)
        untilOption = MENU_OPTIONS_MAX_QUANTITY_DISPLAY + idOfTopOption    # Not inclusive
        if untilOption > optionsAmount:
            untilOption = optionsAmount
        for option in range (idOfTopOption, untilOption):
            optionY = MENU_OPTIONS_TOP_Y + (MENU_OPTIONS_TOTAL_Y_DISTANCE * (option - idOfTopOption))
            if optionsList[option][MENU_OPTIONS_LIST_ONLY_DISPLAYS_VALUE]:
                variableValue = optionsList[option][MENU_OPTIONS_LIST_VARIABLE]
                xPos = graphicLCD.get3x5StringWidth(variableValue)
                graphicLCD.printString3x5(variableValue, MENU_OPTIONS_LEFT_X, optionY, use_memPlot = 1)
            else:
                graphicLCD.printString3x5(optionsList[option][MENU_OPTIONS_LIST_NAME], MENU_OPTIONS_LEFT_X, optionY, use_memPlot = 1)
            if optionsList[option][MENU_OPTIONS_LIST_CHECK]:
                # Draw check circle
                if optionsList[option][MENU_OPTIONS_LIST_CHECK] == MENU_OPTIONS_LIST_CHECK_CIRCLE:
                    graphicLCD.drawHorizontalLine(optionY, MENU_OPTIONS_CHECK_CIRCLE_LEFT_X, MENU_OPTIONS_CHECK_CIRCLE_RIGHT_X, use_memPlot = 1)
                    graphicLCD.drawHorizontalLine(optionY + 4, MENU_OPTIONS_CHECK_CIRCLE_LEFT_X, MENU_OPTIONS_CHECK_CIRCLE_RIGHT_X, use_memPlot = 1)
                    graphicLCD.drawVerticalLine(MENU_OPTIONS_CHECK_BOX_LEFT_X, optionY + 1, optionY + 3, use_memPlot = 1)
                    graphicLCD.drawVerticalLine(MENU_OPTIONS_CHECK_BOX_RIGHT_X, optionY + 1, optionY + 3, use_memPlot = 1)
                    if optionsList[option][MENU_OPTIONS_LIST_VARIABLE] == optionsList[option][MENU_OPTIONS_LIST_VALUE_TO_CHECK_CIRCLE]:
                        graphicLCD.memPlot(MENU_OPTIONS_CHECK_POINT_X, optionY + MENU_OPTIONS_CHECK_POINT_ADD_Y)
                # Draw check box
                elif optionsList[option][MENU_OPTIONS_LIST_CHECK] == MENU_OPTIONS_LIST_CHECK_BOX:
                    graphicLCD.drawRectangle(MENU_OPTIONS_CHECK_BOX_LEFT_X, optionY,
                                             MENU_OPTIONS_CHECK_BOX_RIGHT_X, optionY + MENU_OPTIONS_CHECK_BOX_ADD_Y, use_memPlot = 1)
                    if optionsList[option][MENU_OPTIONS_LIST_VARIABLE]:
                        graphicLCD.memPlot(MENU_OPTIONS_CHECK_POINT_X, optionY + MENU_OPTIONS_CHECK_POINT_ADD_Y)
    # =-= End of menuDrawOptions function =-=

    def menuDrawInvertHoveredOption(hoveredOption, idOfTopOption):
        visualOption = hoveredOption - idOfTopOption
        startY = (MENU_OPTIONS_TOP_Y - 1) + (MENU_OPTIONS_TOTAL_Y_DISTANCE * visualOption)
        graphicLCD.drawRectangle(MENU_OPTIONS_INVERT_HOVERED_LEFT_X, startY,
                                 MENU_OPTIONS_INVERT_HOVERED_RIGHT_X, MENU_OPTIONS_INVERT_BOTTOM_ADD_Y + startY,
                                 fill = 1, style = 2, use_memPlot = 1)
        # Draws the "flag" on the right of the rectangle
        graphicLCD.drawVerticalLine(MENU_OPTIONS_INVERT_HOVERED_RIGHT_X + 1, startY + 1, startY + 5, style = 2, use_memPlot = 1)
        graphicLCD.drawVerticalLine(MENU_OPTIONS_INVERT_HOVERED_RIGHT_X + 2, startY + 2, startY + 4, style = 2, use_memPlot = 1)

    # INIT:
    global global_displayMode, global_gpsMode, global_graphConnectPoints, global_menuOptionsList, global_menuOptionsAmount
    global global_menuIdOfTopOption, global_menuHoveredOptionId, global_menuCloseMenu, global_autoScaleX

    def menuChangeMenu(newOptionKey):
        global global_menuOptionsList, global_menuOptionsAmount, global_menuIdOfTopOption, global_menuHoveredOptionId
        global_menuOptionsList = entireOptionDict[newOptionKey][MENU_OPTIONS_DICT_OPTIONS]
        global_menuOptionsAmount = len(global_menuOptionsList)
        global_menuIdOfTopOption = 0
        global_menuHoveredOptionId = 0
        menuDrawName(entireOptionDict[newOptionKey][MENU_OPTIONS_DICT_MENU_NAME])
        menuDrawOptions(global_menuOptionsList, global_menuOptionsAmount, global_menuIdOfTopOption)
        menuDrawInvertHoveredOption(global_menuHoveredOptionId, global_menuIdOfTopOption)
        menuDrawScrollbars(global_menuOptionsAmount, global_menuHoveredOptionId)
        graphicLCD.memDump()

    def menuReturnToModeRoot(displayMode):
        if displayMode = DISPLAY_MODE_GPS:
            menuChangeMenu("gpsMainOptionList")
        if displayMode = DISPLAY_MODE_GRAPHIC:
            menuChangeMenu("graphMainOptionList")
        if displayMode = DISPLAY_MODE_EXTRA_LOG:
            menuChangeMenu("extraLogMainOptionList")

    def menuEntryTextBox(menuName, originalValue, onlyNumbersAndSignals = True): # For now will only work with numbers.
        # Draws the big box
        graphicLCD.drawRectangle(MENU_ENTRY_LEFT_X, MENU_ENTRY_TOP_Y, MENU_ENTRY_RIGHT_X, MENU_ENTRY_BOTTOM_Y, use_memPlot = 1)
        # Clears inside the big box
        graphicLCD.drawRectangle(MENU_ENTRY_LEFT_X + 1, MENU_ENTRY_TOP_Y + 1, MENU_ENTRY_RIGHT_X - 1, MENU_ENTRY_BOTTOM_Y - 1, fill = 1, style = 0, use_memPlot = 1)
        # Draws the menu name
        graphicLCD.printString3x5(menuName, MENU_ENTRY_NAME_CENTERED_X, MENU_ENTRY_NAME_TOP_Y, align = 1, use_memPlot = 1)
        # Draws the entry box
        graphicLCD.drawRectangle(MENU_ENTRY_TEXT_BOX_LEFT_X, MENU_ENTRY_TEXT_BOX_TOP_Y, MENU_ENTRY_TEXT_BOX_RIGHT_X, MENU_ENTRY_TEXT_BOX_BOTTOM_Y, use_memPlot = 1)
        graphicLCD.memDump()
        valueStr = str(originalValue)
        graphicLCD.printString3x5(valueStr, MENU_ENTRY_TEXT_CENTERED_X, MENU_ENTRY_TEXT_TOP_Y, align = 1, use_memPlot = 1)
        graphicLCD.memDump()
        changedStr = False
        done = False

        while not done:
            if managerDict[KEY_PRESSED_DICT_KEY]:
                for number in range (10):
                    if managerDict[KEY_PRESSED_DICT_KEY] == str(number):
                        valueStr += str(number)
                        changedStr = True
                        break
                if managerDict[KEY_PRESSED_DICT_KEY] == "-":
                    valueStr += "-"
                    changedStr = True
                elif managerDict[KEY_PRESSED_DICT_KEY] == ".":
                    valueStr += "."
                    changedStr = True
                elif managerDict[KEY_PRESSED_DICT_KEY] == KEY_RETURN_STR:
                    valueStr = valueStr[:-1]
                    changedStr = True
                elif managerDict[KEY_PRESSED_DICT_KEY] == KEY_CHANGE_ACTIVE_DISPLAY:
                    blinkScreen()
                if changedStr:
                    # Clears the previous value from screen
                    graphicLCD.drawRectangle(MENU_ENTRY_TEXT_BOX_LEFT_X + 1, MENU_ENTRY_TEXT_BOX_TOP_Y + 1, MENU_ENTRY_TEXT_BOX_RIGHT_X - 1, MENU_ENTRY_TEXT_BOX_BOTTOM_Y - 1, style = 0, fill = 1, use_memPlot = 1)
                    graphicLCD.printString3x5(valueStr, MENU_ENTRY_TEXT_CENTERED_X, MENU_ENTRY_TEXT_TOP_Y, align = 1, use_memPlot = 1)
                    graphicLCD.memDump()
                    changedStr = False
                # Select
                elif managerDict[KEY_PRESSED_DICT_KEY] == KEY_SELECT_STR:
                    try:
                        value = int(valueStr)
                        # if no problem, execute next lines
                        done = True
                    except:
                        # Blinks the entry text box, like a warning that the input is wrong
                        graphicLCD.drawRectangle(MENU_ENTRY_TEXT_BOX_LEFT_X + 1, MENU_ENTRY_TEXT_BOX_TOP_Y + 1, MENU_ENTRY_TEXT_BOX_RIGHT_X - 1, MENU_ENTRY_TEXT_BOX_BOTTOM_Y - 1, style = 2, fill = 1, use_memPlot = 1)
                        graphicLCD.memDump()
                        time.sleep(0.1)
                        graphicLCD.drawRectangle(MENU_ENTRY_TEXT_BOX_LEFT_X + 1, MENU_ENTRY_TEXT_BOX_TOP_Y + 1, MENU_ENTRY_TEXT_BOX_RIGHT_X - 1, MENU_ENTRY_TEXT_BOX_BOTTOM_Y - 1, style = 2, fill = 1, use_memPlot = 1)
                        graphicLCD.memDump()
                elif managerDict[KEY_PRESSED_DICT_KEY] == KEY_ESCAPE_STR:
                    value = originalValue
                    done = True
                managerDict[KEY_PRESSED_DICT_KEY] = ""
            time.sleep(0.01)
        menuDrawOptions(global_menuOptionsList, global_menuOptionsAmount, global_menuIdOfTopOption)
        menuDrawInvertHoveredOption(global_menuHoveredOptionId, global_menuIdOfTopOption)
        graphicLCD.memDump()
        return value
    # -----

    def menuShutdown(managerDict): # Based on text entry box.
        # Draws the big box
        graphicLCD.drawRectangle(MENU_ENTRY_LEFT_X, MENU_ENTRY_TOP_Y, MENU_ENTRY_RIGHT_X, MENU_ENTRY_BOTTOM_Y, use_memPlot = 1)
        # Clears inside the big box
        graphicLCD.drawRectangle(MENU_ENTRY_LEFT_X + 1, MENU_ENTRY_TOP_Y + 1, MENU_ENTRY_RIGHT_X - 1, MENU_ENTRY_BOTTOM_Y - 1, fill = 1, style = 0, use_memPlot = 1)
        # Draws the menu name
        graphicLCD.printString3x5("Shutdown in", MENU_ENTRY_NAME_CENTERED_X, MENU_ENTRY_NAME_TOP_Y - 1, align = 1, use_memPlot = 1)
        graphicLCD.printString3x5("ABORT", MENU_ENTRY_NAME_CENTERED_X, 36, align = 1, use_memPlot = 1)
        graphicLCD.drawRectangle(53, 35, 73, 41, fill = 1, style = 2, use_memPlot = 1) # no constants here, time is running out :)
        graphicLCD.drawVerticalLine(74, 36, 40, use_memPlot = 1)
        graphicLCD.drawVerticalLine(75, 37, 39, use_memPlot = 1)
        shutdownTime = DISPLAY_SHUTDOWN_DELAY
        timeSleepDelay = 0.05
        while not(shutdownTime <= 0 or managerDict[KEY_PRESSED_DICT_KEY] == KEY_SELECT_STR or managerDict[KEY_PRESSED_DICT_KEY] in KEY_ESCAPE_STR_LIST):
            startTime = time.time()
            graphicLCD.printString3x5(str(int(ceil(shutdownTime)))+"s", MENU_ENTRY_NAME_CENTERED_X, MENU_ENTRY_NAME_TOP_Y + 5, align = 1, use_memPlot = 1)
            graphicLCD.memDump()
            time.sleep(timeSleepDelay)
            shutdownTime -= time.time() - startTime

            if managerDict[KEY_PRESSED_DICT_KEY] == KEY_CHANGE_ACTIVE_DISPLAY:
                blinkScreen()
            if shutdownTime <= 0:
                managerDict["shutdownRequested"] = True
                menuCloseMenu()
        if shutdownTime > 0:
            menuDrawOptions(global_menuOptionsList, global_menuOptionsAmount, global_menuIdOfTopOption)
            menuDrawInvertHoveredOption(global_menuHoveredOptionId, global_menuIdOfTopOption)
            graphicLCD.memDump()

    def menuCloseMenu():
        global global_menuCloseMenu
        menuClearArea(everything = True)
        # graphicLCD.memDump()
        global_menuCloseMenu = True

    def menuChangeValue(nameOfVariableStr, additionalVariable = 0):
        global global_graphXAxisInfoList, global_graphXAxisVarId, global_graphYAxisInfoList, global_graphYAxisVarId
        global global_displayMode, global_graphConnectPoints, global_autoScaleX

        if nameOfVariableStr == "xMin":
            global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE] = menuEntryTextBox("Initial X", global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE])
            graphDrawAxisInfos(drawValues = True, do_memDump = True)
        elif nameOfVariableStr == "xMax":
            global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE] = menuEntryTextBox("Final X", global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE])
            graphDrawAxisInfos(drawValues = True, do_memDump = True)
        elif nameOfVariableStr == "yMin":
            global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE] = menuEntryTextBox("Initial Y", global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE])
            graphDrawAxisInfos(drawValues = True, do_memDump = True)
        elif nameOfVariableStr == "yMax":
            global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE] = menuEntryTextBox("Final Y", global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE])
            graphDrawAxisInfos(drawValues = True, do_memDump = True)
        elif nameOfVariableStr == "xDefaults":
            global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE] = GRAPH_X_AXIS_DEFAULT_INFOS_LIST[global_graphXAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE]
            global_graphXAxisInfoList[global_graphXAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE] = GRAPH_X_AXIS_DEFAULT_INFOS_LIST[global_graphXAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE]
            graphDrawAxisInfos(drawValues = True, do_memDump = True)
        elif nameOfVariableStr == "yDefaults":
            global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE] = GRAPH_Y_AXIS_DEFAULT_INFOS_LIST[global_graphYAxisVarId][GRAPH_AXIS_INFO_MIN_VALUE]
            global_graphYAxisInfoList[global_graphYAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE] = GRAPH_Y_AXIS_DEFAULT_INFOS_LIST[global_graphYAxisVarId][GRAPH_AXIS_INFO_MAX_VALUE]
            graphDrawAxisInfos(drawValues = True, do_memDump = True)
        elif nameOfVariableStr == "connectPoints":
            global_graphConnectPoints = not global_graphConnectPoints
            # Change the variable value in the list (**** python)
            entireOptionDict["graphMainOptionList"][1][3][MENU_OPTIONS_LIST_VARIABLE] = global_graphConnectPoints
            menuDrawOptions(global_menuOptionsList, global_menuOptionsAmount, global_menuIdOfTopOption)
            menuDrawInvertHoveredOption(global_menuHoveredOptionId, global_menuIdOfTopOption)
            graphicLCD.memDump()
        elif nameOfVariableStr == "stopReading":
            managerDict["readingRF"] = not managerDict["readingRF"]
            if managerDict["readingRF"]:
                entireOptionDict["systemMenu"][1][0][MENU_OPTIONS_LIST_NAME] = "Stop reading"
            else:
                entireOptionDict["systemMenu"][1][0][MENU_OPTIONS_LIST_NAME] = "Start reading"
            menuDrawOptions(global_menuOptionsList, global_menuOptionsAmount, global_menuIdOfTopOption)
            menuDrawInvertHoveredOption(global_menuHoveredOptionId, global_menuIdOfTopOption)
            graphicLCD.memDump()

        elif nameOfVariableStr == "gpsMode": # Change to gpsMode
            #global global_displayMode
            if global_displayMode != DISPLAY_MODE_GPS:
                global_displayMode = DISPLAY_MODE_GPS
                menuCloseMenu()
        elif nameOfVariableStr == "graphMode": # Change to graphMode
            #global global_displayMode
            if global_displayMode != DISPLAY_MODE_GRAPHIC:
                global_displayMode = DISPLAY_MODE_GRAPHIC
                menuCloseMenu()
        elif nameOfVariableStr == "extraLogMode": # Change to graphMode
            #global global_displayMode
            if global_displayMode != DISPLAY_MODE_EXTRA_LOG:
                global_displayMode = DISPLAY_MODE_EXTRA_LOG
                menuCloseMenu()

        elif nameOfVariableStr == "graphChangeYVar": # Change the Y axis variable
            global_graphYAxisVarId = additionalVariable
            graphDrawAxisInfos(drawValues = True, drawNames = True, do_memDump = True)
        elif nameOfVariableStr == "graphChangeXVar": # Change the Y axis variable
            global_graphXAxisVarId = additionalVariable
            graphDrawAxisInfos(drawValues = True, drawNames = True, do_memDump = True)
        elif nameOfVariableStr == "autoScaleX":
            global_autoScaleX = not global_autoScaleX
            entireOptionDict["graphMainOptionList"][1][4][MENU_OPTIONS_LIST_VARIABLE] = global_autoScaleX
            menuDrawOptions(global_menuOptionsList, global_menuOptionsAmount, global_menuIdOfTopOption)
            menuDrawInvertHoveredOption(global_menuHoveredOptionId, global_menuIdOfTopOption)
            graphicLCD.memDump()

    # [["name to write", onlyDisplaysValue, (functionToCall, args), variable, isCheckType, #optional# valueToCheckCircle], [other options]]
    entireOptionDict = {
        "gpsMainOptionList": [
            "GPS MODE MENU", [
            ("Change mode", False, (menuChangeMenu, "changeModeList"), 0, 0),
            ("Close menu", False, (menuCloseMenu,), 0, 0)]
            ],

        "graphMainOptionList": [
            "GRAPHIC MODE MENU", [
            ("Change mode", False, (menuChangeMenu, "changeModeList"), 0, 0),
            ("Change Y axis", False, (menuChangeMenu, "graphChangeYAxisList"), 0, 0),
            ("Change X axis", False, (menuChangeMenu, "graphChangeXAxisList"), 0, 0),
            ["Connect points", False, [menuChangeValue, "connectPoints"], global_graphConnectPoints, 2],
            ["Auto scaling X", False, [menuChangeValue, "autoScaleX"], global_autoScaleX, 2],
            ("Close menu", False, (menuCloseMenu,), 0, 0)]
            ],
        "graphChangeYAxisList": (
            "CHANGE Y MENU", (
            ("Initial Y value", False, (menuChangeValue, "yMin"), 0, 0),
            ("Final Y value", False, (menuChangeValue, "yMax"), 0, 0),
            ("Load default", False, (menuChangeValue, "yDefaults"), 0, 0),
            ("Change variable", False, (menuChangeMenu, "graphChangeYVariable"), 0, 0),
            ("Return", False, (menuChangeMenu, "graphMainOptionList"), 0, 0),
            ("Close menu", False, (menuCloseMenu,), 0, 0))
            ),
        "graphChangeYVariable": [
            "CHANGE Y VARIABLE", []],
        "graphChangeXAxisList": (
            "CHANGE X MENU", (
            ("Initial X value", False, (menuChangeValue, "xMin"), 0, 0),
            ("Final X value", False, (menuChangeValue, "xMax"), 0, 0),
            ("Load default", False, (menuChangeValue, "xDefaults"), 0, 0),
            ("Change variable", False, (menuChangeMenu, "graphChangeXVariable"), 0, 0),
            ("Return", False, (menuChangeMenu, "graphMainOptionList"), 0, 0),
            ("Close menu", False, (menuCloseMenu,), 0, 0))
            ),
        "graphChangeXVariable": [
            "CHANGE X VARIABLE", []],

        "extraLogMainOptionList": [
            "EXTRA LOG MODE MENU", [
            ("Change mode", False, (menuChangeMenu, "changeModeList"), 0, 0),
            ("Close menu", False, (menuCloseMenu,), 0, 0)]
            ],

        "changeModeList": (
            "CHANGE MODE MENU", (
            ("Graphic mode", False, (menuChangeValue, "graphMode"), global_displayMode, 1, DISPLAY_MODE_GRAPHIC),
            ("Gps mode", False, (menuChangeValue, "gpsMode"), global_displayMode, 1, DISPLAY_MODE_GPS),
            ("Extra log mode", False, (menuChangeValue, "extraLogMode"), global_displayMode, 1, DISPLAY_MODE_EXTRA_LOG),
            ("System menu", False, (menuChangeMenu, "systemMenu"), 0, 0),
            ("Return", False, (menuReturnToModeRoot, global_displayMode), 0, 0),
            ("Close menu", False, (menuCloseMenu,), 0, 0))
            ),
        "systemMenu": [
            "SYSTEM MENU", [
            ["", False, [menuChangeValue, "stopReading"], 0, 0],    # Will change to Start reading, if changed.
            ("Sys shutdown", False, (menuShutdown, managerDict), 0, 0),
            ("Return", False, (menuReturnToModeRoot, global_displayMode), 0, 0),
            ("Close menu", False, (menuCloseMenu,), 0, 0)]
            ],

        } # END OF DICTIONARY

    # Changes "change variable list" in the dictionary, to add the options.
    for counter in range (len(global_graphYAxisInfoList)):
        entireOptionDict["graphChangeYVariable"][1].append((global_graphYAxisInfoList[counter][GRAPH_AXIS_INFO_NAME], False, (menuChangeValue, "graphChangeYVar", counter), 0, 0))
    entireOptionDict["graphChangeYVariable"][1].append(("Return", False, (menuChangeMenu, "graphChangeYAxisList"), 0, 0))
    entireOptionDict["graphChangeYVariable"][1].append(("Close menu", False, (menuCloseMenu,), 0, 0))

    # Changes "change variable list" in the dictionary, to add the options.
    for counter in range (len(global_graphXAxisInfoList)):
        entireOptionDict["graphChangeXVariable"][1].append((global_graphXAxisInfoList[counter][GRAPH_AXIS_INFO_NAME], False, (menuChangeValue, "graphChangeXVar", counter), 0, 0))
    entireOptionDict["graphChangeXVariable"][1].append(("Return", False, (menuChangeMenu, "graphChangeXAxisList"), 0, 0))
    entireOptionDict["graphChangeXVariable"][1].append(("Close menu", False, (menuCloseMenu,), 0, 0))

    if managerDict["readingRF"]:
        string = "Stop reading"
    else:
        string = "Start reading"

        # Change the variable value in the list (**** python)
    entireOptionDict["systemMenu"][1][0][MENU_OPTIONS_LIST_NAME] = string

    # Default actions:
    menuDrawBasicWindow()

    # Actions based on the display mode
    if (global_displayMode == DISPLAY_MODE_GRAPHIC):
        menuChangeMenu("graphMainOptionList")
    if (global_displayMode == DISPLAY_MODE_GPS):
        menuChangeMenu("gpsMainOptionList")
    #
    # =-= End of initing menu graphic mode =-=

    global_menuHoveredOptionId = 0
    global_menuIdOfTopOption = 0
    global_menuCloseMenu = False

    drawAllOptions = False
    onlyDrawInvert = False

    # mainLoop of drawAndControlMenu()
    while not global_menuCloseMenu:

        if managerDict[KEY_PRESSED_DICT_KEY]:

            # Select
            if managerDict[KEY_PRESSED_DICT_KEY] == KEY_SELECT_STR:
                managerDict[KEY_PRESSED_DICT_KEY] = ""       # Reset the key value, before doing the function.
                functionTuple = global_menuOptionsList[global_menuHoveredOptionId][MENU_OPTIONS_LIST_FUNCTION]
                functionTuple[0](*functionTuple[1:]) # Disassembles the tuple, and send them as arguments

            # Escape
            elif managerDict[KEY_PRESSED_DICT_KEY] in KEY_ESCAPE_STR:
                menuCloseMenu()

            # Up
            elif managerDict[KEY_PRESSED_DICT_KEY] == KEY_UP_STR:
                if global_menuHoveredOptionId > 0:        # If can move up

                    while True: # "do{} while()"-like code.

                        global_menuHoveredOptionId -= 1

                        if ((global_menuHoveredOptionId < MENU_OPTIONS_MIDDLE_OPTION - 1) or             # Only moves the invert
                         (global_menuHoveredOptionId > global_menuOptionsAmount - MENU_OPTIONS_MIDDLE_OPTION - 1)):
                            if not onlyDrawInvert:
                                menuDrawInvertHoveredOption(global_menuHoveredOptionId+1, global_menuIdOfTopOption)      # removes the previous invertHovered

                            onlyDrawInvert = True

                        else:
                            global_menuIdOfTopOption -= 1
                            drawAllOptions = True

                        if global_menuOptionsList[global_menuHoveredOptionId][MENU_OPTIONS_LIST_ONLY_DISPLAYS_VALUE] == False:
                            break

                    # =-= End of loop

                    if drawAllOptions:
                        global_menuIdOfTopOption -= changeValueOfIdOfTopOptionBy
                        menuDrawOptions(global_menuOptionsList, global_menuOptionsAmount, global_menuIdOfTopOption)
                        menuDrawInvertHoveredOption(global_menuHoveredOptionId, global_menuIdOfTopOption)
                        menuDrawScrollbars(global_menuOptionsAmount, global_menuIdOfTopOption)
                        changeValueOfIdOfTopOptionBy = 0
                        drawAllOptions = False
                        onlyDrawInvert = False

                    elif onlyDrawInvert:
                        menuDrawInvertHoveredOption(global_menuHoveredOptionId, global_menuIdOfTopOption)             # draws the new invertHovered
                        onlyDrawInvert = False

                    graphicLCD.memDump()

            elif managerDict[KEY_PRESSED_DICT_KEY] == KEY_DOWN_STR:
                if global_menuHoveredOptionId < global_menuOptionsAmount - 1:                 # - 1 as the optionId starts at 0
                    while True:
                        global_menuHoveredOptionId += 1
                        if ((global_menuHoveredOptionId >= global_menuOptionsAmount - MENU_OPTIONS_MIDDLE_OPTION + 1) or     # Only moves the invert
                           (global_menuHoveredOptionId < MENU_OPTIONS_MIDDLE_OPTION)):
                            if not onlyDrawInvert:
                                menuDrawInvertHoveredOption(global_menuHoveredOptionId-1, global_menuIdOfTopOption)      # removes the previous invertHovered
                            onlyDrawInvert = True
                        else:                     # Moves the entire options
                            global_menuIdOfTopOption += 1
                            drawAllOptions = True
                        if global_menuOptionsList[global_menuHoveredOptionId][MENU_OPTIONS_LIST_ONLY_DISPLAYS_VALUE] == False:
                            break
                    # =-= End of loop

                    if drawAllOptions:
                        menuDrawOptions(global_menuOptionsList, global_menuOptionsAmount, global_menuIdOfTopOption)
                        menuDrawInvertHoveredOption(global_menuHoveredOptionId, global_menuIdOfTopOption)
                        menuDrawScrollbars(global_menuOptionsAmount, global_menuIdOfTopOption)
                        changeValueOfIdOfTopOptionBy = 0
                        drawAllOptions = False
                        onlyDrawInvert = False
                    elif onlyDrawInvert:
                        menuDrawInvertHoveredOption(global_menuHoveredOptionId, global_menuIdOfTopOption)             # draws the new invertHovered
                        onlyDrawInvert = False

                    graphicLCD.memDump()

            elif managerDict[KEY_PRESSED_DICT_KEY] == KEY_CHANGE_ACTIVE_DISPLAY:
                blinkScreen()

            managerDict[KEY_PRESSED_DICT_KEY] = ""       # Reset the key value

        time.sleep(0.01)


if __name__ == '__main__':
    try:
        init()
    finally:
        GPIO.cleanup()
