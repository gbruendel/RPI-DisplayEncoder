#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
import Adafruit_CharLCD as LCD

"""
Rotary encoder with a 2 X 16 LCD display
If button on encoder is pressed the counter is set to zero.

"""


# Rotary encoder connections and defenitions
RoAPin = 5    # CLK - GPIO 5
RoBPin = 6    # DT - GPIO 6
RoSwitch = 13

globalCounter = 0

Last_RoB_Status = 0
Current_RoB_Status = 0
flag = 0
RoBPinStatusOld = 0

#LCD display connections and definitions
# Raspberry Pi pin configuration:
lcd_rs        = 27  # Note this might need to be changed to 21 for older revision Pi's.
lcd_en        = 22
lcd_d4        = 25
lcd_d5        = 24
lcd_d6        = 23
lcd_d7        = 18
lcd_backlight = 4
lcd_invert_polarity = False   #Polarity of backlight pin
lcd_enable_pwm = True
lcd_contrast = 17
# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows    = 2


# Define a threaded callback function to run in another thread when events are detected
# switch is pressed on encoder
def RoSwitch_event(channel):
	global globalCounter
	globalCounter = 0
	#print("switch pressed")


def setup():
	global lcd
#	GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
	GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by physical location
	GPIO.setup(RoAPin, GPIO.IN)    # input mode  , pull_up_down = GPIO.PUD_UP
	GPIO.setup(RoBPin, GPIO.IN)    #  , pull_up_down = GPIO.PUD_UP
	GPIO.setup(RoSwitch, GPIO.IN, pull_up_down = GPIO.PUD_UP)

	# Event callbacks f
	# detect falling edge of rotay encoder switch, ignoring further edges for 200ms, execute RoSwitch_event
	GPIO.add_event_detect(RoSwitch, GPIO.FALLING, callback=RoSwitch_event, bouncetime=200)

	# Initialize the LCD using the pins above.
	lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
	                           lcd_columns, lcd_rows, lcd_backlight,
	                           lcd_invert_polarity, lcd_enable_pwm, lcd_contrast)

	# Set backlight and contrast.
	lcd.enable_display(True)
	lcd.set_backlight(1.0)
	lcd.set_contrast(0.45)
	#LCD title
	message = "Rotary Encoder:"
	mess_pos = int(len(message) / 2)
	lcd.set_cursor(int(lcd_columns / 2 - len(message) / 2),0)
	lcd.message(message)
	print("Rotary Encoder Test with LCD Display, terminate with CTRL+C")

def rotaryDeal():
	global flag
	global Last_RoB_Status
	global Current_RoB_Status
	global globalCounter
	Last_RoB_Status = GPIO.input(RoBPin)
	while(not GPIO.input(RoAPin)):
		Current_RoB_Status = GPIO.input(RoBPin)
		flag = 1
	if flag == 1:
		flag = 0
		if (Last_RoB_Status == 0) and (Current_RoB_Status == 1):
			globalCounter = globalCounter + 1
		if (Last_RoB_Status == 1) and (Current_RoB_Status == 0):
			globalCounter = globalCounter - 1


def loop():
	global globalCounter
	global lcd
	globalCounter_old = -1
	while True:
		rotaryDeal()
		if globalCounter != globalCounter_old:
			print ("globalCounter = %d" % globalCounter)
			globalCounter_old = globalCounter
			message = "    " + str(globalCounter)   #add leading zero
			message = message [-5:]                 #return only the 2 most right chars
			lcd.set_cursor(lcd_columns-len(message),1)
			lcd.message(message)

def destroy():
	global lcd
	lcd.set_backlight(0.0)
	lcd.clear()
	GPIO.cleanup()             # Release resource
	print(" received app terminates")



if __name__ == '__main__':    # Program start from here
	setup()
	try:
		loop()


	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed
	    destroy()
