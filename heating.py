#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import sys

GPIO.setmode(GPIO.BCM)
#GPIO.cleanup()

GPIO.setup(18, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)

## 18: kazan szobatermosztat arankor
## 25: puffertolto szivattyu

def base():
#Basic status, all relays are off
  GPIO.output(23, GPIO.HIGH)
  GPIO.output(24, GPIO.HIGH)
  GPIO.output(18, GPIO.HIGH)
  GPIO.output(25, GPIO.HIGH)

#turn on furnace
def heat_on():
  GPIO.output(18, GPIO.LOW)
  GPIO.output(25, GPIO.LOW)

#turn off furnace
def heat_off():
  GPIO.output(18, GPIO.HIGH)
  time.sleep(300)
  GPIO.output(25, GPIO.HIGH)

#turn on pump for puffer
def pump_on():
   GPIO.output(25, GPIO.LOW)



if (len(sys.argv) > 1):
    print "Argument is: " + sys.argv[1]
    if (sys.argv[1] == "1"):
        print "HEAT ON"
        heat_on()

    elif (sys.argv[1] == "2"):
        heat_off()
    elif (sys.argv[1] == "3"):
        pump_on()
    elif (sys.argv[1] == "0"):
        base()
    else:
        heat_off()
else:
  print "No argument supplied"
  heat_off()

print "Hello world!"





