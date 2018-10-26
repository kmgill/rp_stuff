import RPi.GPIO as GPIO
import time
from sys import argv
whichled=argv[1]
ledaction = argv[2]
#12 13 16 19
LEDa=12
LEDb=13
LEDc=16
LEDd=19
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEDa, GPIO.OUT)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEDb, GPIO.OUT)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEDc, GPIO.OUT)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEDd, GPIO.OUT)
if ledaction=="off":
    if whichled=="a":
        GPIO.output(LEDa, False)
    if whichled=="b":
        GPIO.output(LEDb, False)
    if whichled=="c":
        GPIO.output(LEDc, False)
    if whichled=="d":
        GPIO.output(LEDd, False)
    if whichled=="all":
        GPIO.output(LEDa, False)
        GPIO.output(LEDb, False)
        GPIO.output(LEDc, False)
        GPIO.output(LEDd, False)
if ledaction=="on":
    if whichled=="a":
        GPIO.output(LEDa, True)
    if whichled=="b":
        GPIO.output(LEDb, True)
    if whichled=="c":
        GPIO.output(LEDc, True)
    if whichled=="d":
        GPIO.output(LEDd, True)
    if whichled=="all":
        GPIO.output(LEDa, True)
        GPIO.output(LEDb, True)
        GPIO.output(LEDc, True)
        GPIO.output(LEDd, True)
