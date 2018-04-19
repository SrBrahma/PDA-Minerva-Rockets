# This file has some variables (consider them to be constants) that are used in more than one code.
# Just import this file.
# =======================================================================
#  Shutdown 
# =======================================================================
HAVE_SHUTDOWN_BUTTON = False
SHUTDOWN_BUTTON_GPIO = 18
SHUTDOWN_BUTTON_HOLD_TIME = 3

# =======================================================================
#  LoRa
# =======================================================================
# BCM pins numbering, as the wiringpi.wiringPiSetupGpio() function declares to use the BCM.
PIN_LORA_RST = 21            # Reset
PIN_LORA_IRQ = 20            # Interrupt
LORA_FREQUENCY = 915         # Mhz
LORA_SPI_CHANNEL = 0         # SPI Channel (CE0, BCM 8, pin 24)

# =======================================================================
# Character display (I2C)
# =======================================================================
CHAR_LCD_HEALTH_ENABLED = True
CHAR_LCD_HEALTH_DELAY = 1
CHAR_LCD_HEALTH_I2C_ADDRESS = 0x3D

# =======================================================================
#  Graphic displays 
# =======================================================================
SHOW_INIT_IMAGES = True

# Pins setup (in BCM mode (GPIO))
PIN_DISPLAYS_RST = 22

PIN_DISPLAY0_RW = 24
PIN_DISPLAY0_E = 23

PIN_DISPLAY1_RW = 17
PIN_DISPLAY1_E = 27




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


# RF data sequence
# All the data, with the exception of the Header, is a float (4 Bytes)
DATA_LIST_CSV_HEADER_NAME = [
"PacketId", "PacketTime", "GpsLat", "GpsLon", "Bmp180Press(Pa)", "Bmp180Alt(m)", "Bmp180Temp(C)",
"AccelX(m/s^2)", "AccelY(m/s^2)",   "AccelZ(m/s^2)", "GyroX",    "GyroY", "GyroZ",  "MagnX",  "MagnY",  "MagnZ",          

"LoRaSNR",      "LoRaRSSI"]
# "GpsSats", "GpsDate",  "GpsTime" "GpsVel(m/s)",  "GpsVelTheta", "SystemResets", "Photoresistor(anRead)",

# This header won't be stored.
# DATA_LIST_HEADER_POS = 0       # The "MNRV" in the beggining of the package, to filter moderately the incoming packages, from others RF.
                                 #     It isn't included in the saving list. Is 4 chars long = 4 bytes long, 'M', 'N', 'R', 'V'.

DATA_LIST_PACKET_ID = 0          # Packet Id
DATA_LIST_PACKET_TIME = 1        # The time the packet was sent
        #DATA_LIST_GPS_SATS = 2           # Number of GPS satellites with contact
        #DATA_LIST_GPS_DATE = 3           # The date from GPS
        #DATA_LIST_GPS_TIME = 4           # The time from GPS

DATA_LIST_GPS_LAT = 2            # Latitude (float mode) from GPS
DATA_LIST_GPS_LON = 3            # Longitude (float mode) from GPS
# DATA_LIST_GPS_ALT = 4            # Altitude from GPS

        # DATA_LIST_GPS_VEL = 8            # The velocity (m/s) from GPS
        # DATA_LIST_GPS_VEL_THETA = 9     # The horizontal degree

DATA_LIST_BMP_180_PRESS = 5
DATA_LIST_BMP_180_ALT = 6
DATA_LIST_BMP_180_TEMP = 7

DATA_LIST_ACCEL_X = 8
DATA_LIST_ACCEL_Y = 9
DATA_LIST_ACCEL_Z = 10

DATA_LIST_GYRO_X = 11
DATA_LIST_GYRO_Y = 12
DATA_LIST_GYRO_Z = 13

DATA_LIST_MAGN_X = 14
DATA_LIST_MAGN_Y = 15
DATA_LIST_MAGN_Z = 16




        # DATA_LIST_SYSTEM_RESETS = 22
        # DATA_LIST_LDR = 23              # Photoresistor analogRead()


DATA_LIST_LAST_RF_INDEX = DATA_LIST_MAGN_Z

# Additional data to be saved to log / readen by displays, not 


DATA_LIST_SNR = DATA_LIST_LAST_RF_INDEX + 1
DATA_LIST_RSSI = DATA_LIST_LAST_RF_INDEX + 2

RF_PACKET_DATA_VARIABLES = DATA_LIST_MAGN_Z + 1 # Last element plus 1, variables amount
RF_PACKET_DATA_LENGTH_BYTE = RF_PACKET_DATA_VARIABLES * 4

DATA_LIST_VARIABLES = RF_PACKET_DATA_VARIABLES + 2
DATA_LIST_MAX_PACKETS = 999999

ARRAY_LENGTH = DATA_LIST_MAX_PACKETS * DATA_LIST_VARIABLES
RF_CUSTOM_HEADER_STR = "MNRV"
RF_CUSTOM_HEADER_LIST = [ord(x) for x in RF_CUSTOM_HEADER_STR]      # Decompose the string to a list of chars, in bytes.

RF_CUSTOM_HEADER_EXTRA_STR = "MNEX"
RF_CUSTOM_HEADER_EXTRA_LIST = [ord(x) for x in RF_CUSTOM_HEADER_STR]      # Decompose the string to a list of chars, in bytes.
