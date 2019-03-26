#!/usr/bin/python
import os
import glob
import time
import sys
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
  
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_folders = glob.glob(base_dir + '28*')
device_file = device_folder + '/w1_slave'
sensors = {
  "000002cc5842": "Kazan kilepo",
  "00000724371b": "Futes elore",
  "00000723b2b2": "Futes vissza",
  "0000064ff9ea": "Puffer1",
  "0000072411c1": "Puffer2",
  "000002cc42b9": "Puffer3",
  "0000063759a7": "Puffer4" 
        }


#device = filename.split("-")

def read_temp_raw(dev):
   dev_file = dev + '/w1_slave' 
   f = open(dev_file, 'r')
   lines = f.readlines()
   f.close()
   return lines

def read_temp(dev):
  lines = read_temp_raw(dev)
  while lines[0].strip()[-3:] != 'YES':
    time.sleep(0.2)
    lines = read_temp_raw(dev)
  equals_pos = lines[1].find('t=')
  if equals_pos != -1:
    temp_string = lines[1][equals_pos+2:]
    temp_c = float(temp_string) / 1000.0
    temp_f = temp_c * 9.0 / 5.0 + 32.0
    return temp_c

while True:
#  print(read_temp())  
#  print(read_temp())  
  device_folders = glob.glob(base_dir + '28*')
  output = ""
  for df in device_folders:
      key = df.split("-")[-1]
      output += sensors.get(key, "Ismeretlen") + ":\t"
      output += str(read_temp(df)) + "\n" 
      #print(sensors.get(key, "Ismeretlen"))
      #print(df)
      #print(read_temp(df))
  print(chr(27) + "[2J")
  print output
  time.sleep(10)
