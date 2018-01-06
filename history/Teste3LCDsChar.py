
import time
import I2C_LCD_driver

CHAR_LCD_0_I2C_ADDRESS = 0x3B
CHAR_LCD_1_I2C_ADDRESS = 0x3D
CHAR_LCD_2_I2C_ADDRESS = 0x3F

try:
	charLCD0 = I2C_LCD_driver.lcd (CHAR_LCD_0_I2C_ADDRESS)
except:
	print ("Error at address ", format (CHAR_LCD_0_I2C_ADDRESS, '#02X'), ", from LCD 0. Check your wiring.")
'''   This format is for making the output as hexadecimal.
  # = 0x at the beggining
  X = Upper case; x = lower case   '''
 
try:
	charLCD1 = I2C_LCD_driver.lcd (CHAR_LCD_1_I2C_ADDRESS)
except:
	print ("Error at address ", format (CHAR_LCD_1_I2C_ADDRESS, '#02X'), ", from LCD 1. Check your wiring.")


try:
	charLCD2 = I2C_LCD_driver.lcd (CHAR_LCD_2_I2C_ADDRESS)
except:
	print ("Error at address ", format (CHAR_LCD_2_I2C_ADDRESS, '#02X'), ", from LCD 2. Check your wiring.")


from pygame.locals import *
import pygame
import sys


def main():
	charLCD0.lcd_display_string ("Minerva Rockets", 1, 2)
	charLCD0.lcd_display_string ("Minerva Rockets", 2, 2)
	charLCD0.lcd_display_string ("Minerva Rockets", 3, 2)
	charLCD0.lcd_display_string ("Minerva Rockets", 4, 2)
	
	charLCD1.lcd_display_string ("ELETRONICAAAAAA", 1, 2)
	charLCD1.lcd_display_string ("ELETRONICAAAAAA", 2, 2)
	charLCD1.lcd_display_string ("ELETRONICAAAAAA", 3, 2)
	charLCD1.lcd_display_string ("ELETRONICAAAAAA", 4, 2)
	
	charLCD2.lcd_display_string ("eeeeeeeeeeeeeee", 1, 2)
	charLCD2.lcd_display_string ("eeeeeeeeeeeeeee", 2, 2)
	charLCD2.lcd_display_string ("eeeeeeeeeeeeeee", 3, 2)
	charLCD2.lcd_display_string ("eeeeeeeeeeeeeee", 4, 2)
	
	
	print ("Feito!")


#	except KeyboardInterrupt:
#		return 0
#	except:
#		return 1
#
#	finally:
#		terminate ()			
#
def terminate():
	mylcd.lcd_clear ()
	mylcd.backlight(0)
	pygame.quit()
	sys.exit()
	
if __name__ == "__main__":
	main()
