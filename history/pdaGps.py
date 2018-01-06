import glcd12864zw as graphicLCD
import RPi.GPIO as GPIO
import timeit
import time

#==================================
# GPS CONFIGS
GPS_CONE_RADIUS_PX = 20
GPS_CONE_WIDENESS_DEGREE = 30 # The angle between the pole and the center.

GPS_CENTER_X = 63
GPS_CENTER_Y = 32

GPS_BEARING_DEGREE_ADD = 0          
GPS_BEARING_DEGREE_THRESHOLD = 0     # Only updates the rotational cone/north if the bearing changed >= this degree

GPS_REFRESH_DELAY = 0.068 # Actually should be 0.066667 (the magnetometer refresh rate, 15Hz = 1.0/15.0s),
# but I will leave a little more to avoid same readings. 

GPS_MODE_FIXED_NORTH = 0
GPS_MODE_VARIABLE_NORTH = 1

#
#==================================

    
    
# Yeap, I am using global variables. The code is small, and it runs around these variables. Deal with it.
previousDegree = 0
gpsMode = GPS_MODE_FIXED_NORTH
#totalSum = 0
#number = 0

'''
def signal_handler(signal, frame):
    print "something..."
    global interrupted
    if not interrupted:
        print "Interrupting for signal: ", signal
    interrupted = True
    drawAndDoShutdown()
    '''
def init():
    
    graphicLCD.init()
    graphicLCD.clearDisplay()
    graphicLCD.initTextMode()
    graphicLCD.initGraphicMode()
    
    #signal.signal(signal.SIGINT, signal_handler)
    #signal.signal(signal.SIGTERM, signal_handler)
    
    #drawTest()
    graphDrawBackground()
    graphDrawAxisInfos(0, 120, 0, 30, "t(s)", "h(m)")


def drawTest():
    start_time = timeit.default_timer()
    graphicLCD.drawRectangle(5, 5, 122, 57, 1, 1, 1)
    graphicLCD.memDump()
    elapsed = timeit.default_timer() - start_time
    print "Elapsed Time: ", "%.16f" % elapsed
    '''
    string = ""
    for i in range (32, 65):
        string+=chr(i)
    graphicLCD.printString3x5(string, 2, 10)
    
    string = ""
    for i in range (65, 97):
        string+=chr(i)
    graphicLCD.printString3x5(string, 2, 16)
    
    string = ""
    for i in range (97, 128):
        string+=chr(i)
    graphicLCD.printString3x5(string, 2, 22)
    graphicLCD.memDump()
    
    graphicLCD.printString3x5("Rotation = 0", 50, 10, 0)
    graphicLCD.printString3x5("Rotation = 1", 20, 61, 1)
    
    graphicLCD.printString3x5("Rotation = 2", 80, 31, 2)
    graphicLCD.printString3x5("Rotation = 3", 110, 11, 3)'''
    #graphicLCD.loadBMP12864("Controls LCD10.bmp")
    #graphicLCD.loadBMP12864("Graphic LCD.bmp")

def mainLoop(managerGpsDict = {"toDo": 0, "magnBearing": 0}):
    while managerGpsDict["toDo"] != 999:
        # start_time = timeit.default_timer()
        if (not managerGpsDict["toDo"]):
            #start_time = timeit.default_timer()
                
            gpsDraw(managerGpsDict["magnBearing"])
                
            #elapsed = timeit.default_timer() - start_time
            #print "Elapsed Time GPS: ", "%.16f" % (elapsed)
        elif (managerGpsDict["toDo"] == 1):
            gpsDrawBackground()
            managerGpsDict["toDo"] = 0
        elif (managerGpsDict["toDo"] == 2):
            gpsModeFixedNorth()
            managerGpsDict["toDo"] = 0
        elif (managerGpsDict["toDo"] == 3):
            gpsModeVariableNorth()
            managerGpsDict["toDo"] = 0
            
        elif (managerGpsDict["toDo"] == 10):
            graphDrawBackground()
        time.sleep(GPS_REFRESH_DELAY)
            # elapsed = timeit.default_timer() - start_time
            # print "Elapsed Time GPS: ", "%.16f" % (elapsed)
        
    # implicit if managerGpsDict["toDo"] == 999
    drawAndDoShutdown()


    
def drawShutdown():
    global interrupted
    graphicLCD.clearDisplay()
    graphicLCD.initTextMode()
    #graphicLCD.initGraphicMode()
    #graphicLCD.printStringGraphicMode("     Graphic    ",  0,  0, False)
    #                              #================#
    graphicLCD.printStringTextMode("> SHUTTING DOWN!", 0, 0)
    graphicLCD.printStringTextMode("Please wait 10s ", 0, 1)
    graphicLCD.printStringTextMode("before powering" , 0, 2)
    graphicLCD.printStringTextMode("off.  MINERVA! " , 0, 3)
    
    
    
def gpsModeFixedNorth(mpManagerList = 0):
    global gpsMode
    #if (gpsMode != GPS_MODE_FIXED_NORTH): # Avoids rewriting LCD without need
    gpsMode = GPS_MODE_FIXED_NORTH
    gpsDrawBackground()

def gpsModeVariableNorth(mpManagerList = 0):
    global gpsMode
    #if (gpsMode != GPS_MODE_VARIABLE_NORTH): # Avoids rewriting LCD without need 
    gpsMode = GPS_MODE_VARIABLE_NORTH
    gpsDrawBackground()
    

def gpsDrawBackground(mpManagerList = 0):
    graphicLCD.drawRectangle(5, 5, 122, 57, 0)
    if (gpsMode == GPS_MODE_FIXED_NORTH):     
        gpsDrawNorthSymbol(GPS_CENTER_X, 0)
    #graphicLCD.loadBMP12864("GPS_Background.bmp")    # To load the background .bmp. I probably won't use this anymore,
                                                      # but I will keep here for recordation.

def gpsDrawNorthSymbol(posX, posY, style = 1):
    graphicLCD.drawVerticalLine(posX, posY, posY + 3, style)
    graphicLCD.plot(posX + 1, posY + 1, style)
    graphicLCD.plot(posX + 2, posY + 2, style)
    graphicLCD.drawVerticalLine(posX + 3, posY, posY + 3, style)
    
def gpsDraw(magnetometerBearingDegree):
    global previousDegree
    #global totalSum
    #global number
    
    #start_time = timeit.default_timer()
    
    if (gpsMode == GPS_MODE_FIXED_NORTH):

        degree = magnetometerBearingDegree + GPS_BEARING_DEGREE_ADD
        #print degree, previousDegree, "diff =", abs(degree - previousDegree)
        # Draw rotational cone
        
        if (abs(degree - previousDegree) > GPS_BEARING_DEGREE_THRESHOLD):
            #start_time = timeit.default_timer()
            '''
            if (degree < 0):
                degree = 360 + degree
            if (degree > 360):
                degree -= 360'''
            # print "degree = ", degree, "; previousDegree = ", previousDegree
            graphicLCD.drawRadiusLine(GPS_CENTER_X, GPS_CENTER_Y, (previousDegree - GPS_CONE_WIDENESS_DEGREE), GPS_CONE_RADIUS_PX, 0)
            graphicLCD.drawRadiusLine(GPS_CENTER_X, GPS_CENTER_Y, (previousDegree + GPS_CONE_WIDENESS_DEGREE), GPS_CONE_RADIUS_PX, 0)
            graphicLCD.drawRectangle(GPS_CENTER_X - 1, GPS_CENTER_Y - 1, GPS_CENTER_X + 1, GPS_CENTER_Y + 1, 1, 0)

            graphicLCD.drawRadiusLine(GPS_CENTER_X, GPS_CENTER_Y, (degree - GPS_CONE_WIDENESS_DEGREE), GPS_CONE_RADIUS_PX)
            graphicLCD.drawRadiusLine(GPS_CENTER_X, GPS_CENTER_Y, (degree + GPS_CONE_WIDENESS_DEGREE), GPS_CONE_RADIUS_PX)

            graphicLCD.drawRectangle(GPS_CENTER_X - 1, GPS_CENTER_Y - 1, GPS_CENTER_X + 1, GPS_CENTER_Y + 1, 1, 2)
            #print degree
            previousDegree = degree
            
            #totalSum += timeit.default_timer() - start_time
            #number += 1
            #print "Median = ", totalSum/number
            
    #elapsed = timeit.default_timer() - start_time
    #print "Elapsed Time: ", "%.16f" % elapsed

#######################################


def graphDrawBackground():
    graphicLCD.drawVerticalLine(6, 0, 57, use_memPlot= 1)
    graphicLCD.drawHorizontalLine(57, 6, 127, use_memPlot = 1)
    graphicLCD.memPlot(5, 56) # graphY = 0
    graphicLCD.memPlot(5, 28) # graphY = y/2
    graphicLCD.memPlot(5,  0) # graphY = y
    graphicLCD.memPlot(7, 58) # graphX = 0
    graphicLCD.memPlot(37, 58) # graphX = x/4
    graphicLCD.memPlot(67, 58) # graphX = 2x/4
    graphicLCD.memPlot(97, 58) # graphX = 3x/4
    graphicLCD.memPlot(127, 58) # graphX = 3x/4
    graphicLCD.memDump()
    
def graphDrawAxisInfos(xMin, xMax, yMin, yMax, xName, yName):
    xDist, yDist = xMax - xMin, yMax - yMin
    
    graphicLCD.printString3x5(str(xMin), 8, 59, 0, 1)
    graphicLCD.printString3x5(str(xDist/4), 34, 59, 0, 1)
    graphicLCD.printString3x5(str(xDist/2), 64, 59, 0, 1)
    graphicLCD.printString3x5(str(xDist*3/4), 94, 59, 0, 1)
    graphicLCD.printString3x5(str(xMax), 125 - (len(str(xMax)) * 3), 59, 0, 1)
    
    graphicLCD.printString3x5(str(yMin), 0, 55, 1, 1)
    graphicLCD.printString3x5(str(yDist/2), 0, 31, 1, 1)
    graphicLCD.printString3x5(str(yMax), 0, 1 + (len(str(yMax)) * 3), 1, 1)
    
    graphicLCD.printString3x5(xName, 16, 59, 0, 1)
    graphicLCD.printString3x5(yName,  0, 47, 1, 1)
    graphicLCD.memDump()
    
init()
