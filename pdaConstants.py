# This file has some variables (consider them to be constants) that are used in more than one code.
# Just import this file.
# =======================================================================
#  Shutdown 
# =======================================================================
HAVE_SHUTDOWN_BUTTON = True
SHUTDOWN_BUTTON_GPIO = 18
SHUTDOWN_BUTTON_HOLD_TIME = 3

# =======================================================================
# Character display (I2C)
# =======================================================================
CHAR_LCD_HEALTH_ENABLED = True
CHAR_LCD_HEALTH_DELAY = 1
CHAR_LCD_HEALTH_I2C_ADDRESS = 0x3D

# =======================================================================
#  Graphic displays 
# =======================================================================
SHOW_INIT_IMAGES = False

# Pins setup (in BCM mode (GPIO))
PIN_DISPLAYS_RST = 22

PIN_DISPLAY0_RW = 17
PIN_DISPLAY0_E = 27

PIN_DISPLAY1_RW = 20
PIN_DISPLAY1_E = 21


    # Graphical display
DISPLAY_SHUTDOWN_DELAY = 5

DO_SHUTDOWN_PRINT_MESSAGE = 1
DO_SHUTDOWN_DRAW_IMAGE = 2

# Keys list
KEY_UP_STR = "up"
KEY_DOWN_STR = "down"
KEY_RETURN_STR = "backspace"            # To remove the last char in text entry boxes. In future will return to previous menu.
KEY_ESCAPE_STR = "esc"                  # To cancel in text entry boxes.
KEY_CHANGE_ACTIVE_DISPLAY = "ctrl"

KEY_SELECT_STR = "enter"
KEY_ESCAPE_STR_LIST = ["esc", "i"]
KEY_OPEN_MENU_STR_LIST = ["i", "m", "esc"]


# Graphical Display consts
DISPLAY_MODE_GRAPHIC = 1
DISPLAY_MODE_GPS = 2

DISPLAY_IMAGE_ROCKETS = 1
DISPLAY_IMAGE_BRAZIL = 2


# =======================================================================
#  RF and DATA_LIST
# =======================================================================
RF_MAX_APOGEE = 3500   # Filter eventual garbage that may come to the display area

RF_PACKET_DATA_VARIABLES = 32
RF_PACKET_DATA_LENGTH_BYTE = RF_PACKET_DATA_VARIABLES * 4

DATA_LIST_VARIABLES = RF_PACKET_DATA_VARIABLES + 2
DATA_LIST_MAX_PACKETS = 30000

ARRAY_LENGTH = DATA_LIST_MAX_PACKETS * DATA_LIST_VARIABLES
RF_CUSTOM_HEADER_STR = "MNRV"
RF_CUSTOM_HEADER_LIST = [ord(x) for x in RF_CUSTOM_HEADER_STR]      # Decompose the string to a list of chars, in bytes.

# RF data sequence
# All the data, with the exception of the Header, is a float (4 Bytes)
DATA_LIST_CSV_HEADER_NAME = [
"PacketId",     "PacketTime",   "GpsSats",  "GpsDate",          "GpsTime",      "GpsLat",           "GpsLon",           "GpsAlt",
"GpsVel(m/s)",  "GpsVelTheta",  "MagnX",    "MagnY",            "MagnZ",        "AccelX(m/s^2)",    "AccelY(m/s^2)",    "AccelZ(m/s^2)", 
"GyroX",        "GyroY",        "GyroZ",    "Bmp180Press(Pa)",  "Bmp180Temp(C)","Bmp180Alt(m)",     "SystemResets",     "Photoresistor(anRead)",
" ",            " ",            " ",        " ",                " ",            " ",                " ",                " ",
"LoRaSNR",      "LoRaRSSI"]


# This header won't be stored.
# DATA_LIST_HEADER_POS = 0       # The "MNRV" in the beggining of the package, to filter moderately the incoming packages, from others RF.
                                 #     It isn't included in the saving list. Is 4 chars long = 4 bytes long, 'M', 'N', 'R', 'V'.

DATA_LIST_PACKET_ID = 0          # Packet Id
DATA_LIST_PACKET_TIME = 1        # The time the packet was sent
DATA_LIST_GPS_SATS = 2           # Number of GPS satellites with contact
DATA_LIST_GPS_DATE = 3           # The date from GPS
DATA_LIST_GPS_TIME = 4           # The time from GPS
DATA_LIST_GPS_LAT = 5            # Latitude (float mode) from GPS
DATA_LIST_GPS_LON = 6            # Longitude (float mode) from GPS
DATA_LIST_GPS_ALT = 7            # Altitude from GPS

DATA_LIST_GPS_VEL = 8            # The velocity (m/s) from GPS
DATA_LIST_GPS_VEL_THETA = 9     # The horizontal degree
DATA_LIST_MAGN_X = 10
DATA_LIST_MAGN_Y = 11
DATA_LIST_MAGN_Z = 12
DATA_LIST_ACCEL_X = 13
DATA_LIST_ACCEL_Y = 14
DATA_LIST_ACCEL_Z = 15

DATA_LIST_GYRO_X = 16
DATA_LIST_GYRO_Y = 17
DATA_LIST_GYRO_Z = 18
DATA_LIST_BMP_180_PRESS = 19
DATA_LIST_BMP_180_TEMP = 20
DATA_LIST_BMP_180_ALT = 21
DATA_LIST_SYSTEM_RESETS = 22
DATA_LIST_LDR = 23              # Photoresistor analogRead()


DATA_LIST_LAST_RF_INDEX = 31

# Additional data to be saved to log / readen by displays, not 

DATA_LIST_SNR = DATA_LIST_LAST_RF_INDEX + 1
DATA_LIST_RSSI = DATA_LIST_LAST_RF_INDEX + 2
