
class DisplayExtraLog:
    EXTRA_LOG_MAX_OPTIONS_ON_SCREEN = 7
    EXTRA_LOG_SCROLLBAR_LEFT_X = 117
    EXTRA_LOG_SCROLL_MAX_HEIGHT = 46
    EXTRA_LOG_SCROLL_TOP_Y = 9
    EXTRA_LOG_SCROLL_LEFT_X = 118
    EXTRA_LOG_SCROLL_RIGHT_X = 119

    def __init__(self, graphicLCDObject, managerDict, extraLogArray):
        self.graphicLCD = graphicLCDObject
        self.managerDict = managerDict
        self.extraLogArray = extraLogArray
        self.stringsList = []
        self.actualLogIndex = 0
        self.numberOfStrings = 0

    def updateStringList(self):
        if self.numberOfStrings != managerDict["logExtraLength"]:
            self.numberOfStrings = managerDict["logExtraLength"]

        for self.actualLogIndex in range (self.actualLogIndex, self.numberOfStrings)
            baseIndex = EXTRA_LOG_MAX_STRING_LENGTH * self.actualLogIndex
            endOfStringPos = self.extraLogArray[baseIndex:baseIndex + EXTRA_LOG_MAX_STRING_LENGTH].index("\0")
            self.stringsList.append(''.join(self.extraLogArray[baseIndex:endOfStringPos-1])) # https://stackoverflow.com/a/5618893

    def drawBackground(self):
        self.graphicLCD.printString3x5("Extra Log", 63, 0, align = 1, use_memPlot = 1)
        self.graphicLCD.drawRectangle(5, 6, 122, 57, use_memPlot = 1) # Draws the big rectangle
        self.graphicLCD.drawRectangle( 117, 8, 120, 55, use_memPlot = 1) # Scrollbar outline

    def menuDrawScrollbar(optionsAmount, idOfTopOption):
        menuClearArea(scrollbar = True)
        optionsToShow = EXTRA_LOG_MAX_OPTIONS_ON_SCREEN
        if (optionsAmount < EXTRA_LOG_MAX_OPTIONS_ON_SCREEN):
            optionsToShow = optionsAmount
        scrollSize = EXTRA_LOG_SCROLL_MAX_HEIGHT * optionsToShow / float (optionsAmount)
        hiddenOptions = optionsAmount - optionsToShow
        if hiddenOptions:
            scrollStepPosY = (EXTRA_LOG_SCROLL_MAX_HEIGHT - scrollSize) / hiddenOptions
        else:
            scrollStepPosY = 0
        scrollPosY = EXTRA_LOG_SCROLL_TOP_Y + scrollStepPosY * idOfTopOption
        graphicLCD.drawRectangle(EXTRA_LOG_SCROLL_LEFT_X, int(round(scrollPosY)), EXTRA_LOG_SCROLL_RIGHT_X, int(round(scrollPosY + scrollSize)), fill = 1, use_memPlot = 1)

    def menuDrawOptions(optionsList, optionsAmount, idOfTopOption):
        6, 7, 115, 55 # Clear previous options
        untilOption = EXTRA_LOG_MAX_OPTIONS_ON_SCREEN + idOfTopOption    # Not inclusive
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
