#!/usr/bin/python
import os
import glob
import time
import sys
import json
import syslog
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_folders = glob.glob(base_dir + '28*')
device_file = device_folder + '/w1_slave'
path = "/home/pi/code/system-json.txt"
sensors = {
  "000002cc5842": "Kazan_kilepo",
  "00000724371b": "Futes_elore",
  "00000723b2b2": "Futes_vissza",
  "0000064ff9ea": "Puffer1",
  "0000072411c1": "Puffer2",
  "000002cc42b9": "Puffer3",
  "0000063759a7": "Puffer4"
        }
temperature = {
        
        "Kazan_kilepo" : 0,
        "Futes_elore" : 0,
        "Futes_vissza" : 0,
        "Puffer1" : 0, 
        "Puffer2" : 0,
        "Puffer3" : 0,
        "Puffer4" : 0
        }
status = {
        "Lakas_keringeto": 0,
        "Puffertolto": 0,
        "Gazbojler": 0,
        "Also_futes": 0,
        "Felso_futes": 0
        }
system = {
        "temperature": temperature,
        "status": status
        }
temporary = {}

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

def write_to_file(output,obj):
  if (obj is None):
    f=open("/home/pi/code/system-json.txt","w+")
    f.write(json.dumps(output))
    f.close()
  else:
    with open(path,"r") as json_file:
      data = json.load(json_file)
    data[obj] = output
    with open(path,"w") as outfile:
        json.dump(data, outfile) 
        
        
def radiatorPump():
    with open(path,"r") as json_file:
      data = json.load(json_file)
    if (int(data["status"]["Felso_futes"]) == 1 or int(data["status"]["Also_futes"]) == 1):
        data["status"]["Lakas_keringeto"] = 1

    if (int(data["status"]["Felso_futes"]) == 0 and int(data["status"]["Also_futes"]) == 0):
        data["status"]["Lakas_keringeto"] = 0
        
    write_to_file(data,None)

def fillPuffer():
    with open(path) as json_file:
      data = json.load(json_file)
    turn_off_temp = min(max(70,float(data["temperature"]["Puffer4"])+5),80)
    turn_on_temp = min((turn_off_temp + 15),92)
    syslog.syslog(syslog.LOG_INFO,"Puffertöltés kikapcsolása: : " + str(turn_off_temp))
    syslog.syslog("Puffertöltés bekapcsolása: " + str(turn_on_temp))


    if ( float(data["temperature"]["Kazan_kilepo"]) > turn_on_temp):
          syslog.syslog("PUFFERTÖLTÉS BE")
          data["status"]["Puffertolto"] = 1


    if ( float(data["temperature"]["Kazan_kilepo"]) < turn_off_temp):
          syslog.syslog("PUFFERTÖLTÉS KI")
          data["status"]["Puffertolto"] = 0
    write_to_file(data,None) 
#    f = open("/home/pi/code/heating/datas", "r")
#    firstline = f.readline()
#    values = list(map(int, firstline.split()))
#    system["status"]["Lakas_keringeto"] = values[0]
#    system["status"]["Puffertolto"] = values[1]
#    system["status"]["Gazbojler"] = values[2]
#    system["status"]["Also_futes"] = values[3]
#    system["status"]["Felso_futes"] = values[4]

#    f.close()

while True:
  device_folders = glob.glob(base_dir + '28*')
  for df in device_folders:
      keystring = df.split("-")[-1]
      key = sensors.get(keystring) 
      temporary[key] = str(read_temp(df))
  write_to_file(temporary,"temperature")
  fillPuffer()
  radiatorPump()
  time.sleep(10)
