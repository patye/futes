#!/usr/bin/env python3
import serial
import time
import json

ser = serial.Serial('/dev/ttyACM0',115200, timeout = 1.0)
time.sleep(3)
ser.reset_input_buffer()
print("Serial OK")

sensorlist={'284258CC020000CA':'Kazan_kilepo',
        '28B2B22307000039':'Futes_vissza',
        '28EAF94F06000006':'Puffer1',
        '28C1112407000003':'Puffer2',
        '28B942CC02000081':'Puffer3',
        '281B37240700006C':'Futes_elore',
        '28A75937060000BE':'Puffer4'}


temperature = {

        "Kazan_kilepo": 0,
        "Futes_elore": 0,
        "Futes_vissza": 0,
        "Puffer1": 0,
        "Puffer2": 0,
        "Puffer3": 0,
        "Puffer4": 0
        }

prevtime = 0

def write_to_file(output):
  f=open("/home/pi/code/temperature.json","w+")
  f.write(json.dumps(output, separators=(',',':')))
  f.close()


try:
    while True:
        time.sleep(0.1)
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8')
            sensorid = line.split(':')[0]
            temp = line.split(':')[1]
            sensorname=sensorlist[sensorid]
            temperature[sensorname] = float(temp.strip())
            if int(time.time())-10 >= prevtime:
                write_to_file(temperature)
                print(temperature)
                prevtime = int(time.time())
except KeyboardInterrupt:
    print("Closing serial...")
    ser.close
