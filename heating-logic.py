#!/usr/bin/python3
import os
import glob
import time
import sys
import json
import logging
import calendar

logger = logging.getLogger("heating-logic")
logger.setLevel(logging.INFO)
# define file handler and set formatter
formatter    = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler = logging.FileHandler('/var/log/heating/heating.log')
file_handler.setFormatter(formatter)


# add file handler to logger
logger.addHandler(file_handler)


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
        "Gazkazan": 0,
        "Also_futes": 0,
        "Felso_futes": 0,
        "internal_temperature_ok": 1,
        "eloremeno_min": 50,
        }
system = {
        "temperature": temperature,
        "status": status
        }
temporary = {}


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
    logger.info(str(data))    
        
def radiatorPump():
    with open(path,"r") as json_file:
      data = json.load(json_file)
    user_intention =  int(data["status"]["Felso_futes"]) == 1 \
            or int(data["status"]["Also_futes"]) == 1
    demand_by_temperature = int(data["status"]["internal_temperature_ok"]) != 1
    heat_in_puffer = float(data["temperature"]["Puffer1"]) > int(data["status"]["eloremeno_min"]) 
    if ( user_intention and heat_in_puffer and demand_by_temperature):
        data["status"]["Lakas_keringeto"] = 1
    else:
        data["status"]["Lakas_keringeto"] = 0
        
    write_to_file(data,None)

def fillPuffer():
    with open(path) as json_file:
      data = json.load(json_file)
    turn_off_temp = min(max(70,float(data["temperature"]["Puffer4"])+5),80)
    turn_on_temp = min((turn_off_temp + 10),92)

    #Puffertöltő bekapcsolás, ha megy a gázkazán, vagy meleg a fatüzelésű kazán
    if ( float(data["temperature"]["Kazan_kilepo"]) > turn_on_temp or int(data["status"]["Gazkazan"]) == 1 ):
          data["status"]["Puffertolto"] = 1

    #Puffertöltő kikapcsolása fafűtés esetén - védi a fatüzelésű kazánk a kihűlés ellen
    if ( float(data["temperature"]["Kazan_kilepo"]) < turn_off_temp and  int(data["status"]["Gazfutes"]) == 0 ):
          data["status"]["Puffertolto"] = 0

    #Puffertöltő kikapcsolás ha letelt-e a beégetett érték
    if ( ( int(data["status"]["puffertolto_off_schedule"]) + 90 <  calendar.timegm(time.gmtime()) ) and data["status"]["puffertolto_off_trigger"] == 1 and  data["status"]["Gazkazan"] == 0):
        data["status"]["Puffertolto"] = 0
        data["status"]["puffertolto_off_trigger"] = 0

    write_to_file(data,None)
def gazKazan():
    
    with open(path) as json_file:
       data = json.load(json_file)
    if ( int(data["status"]["internal_temperature_ok"]) == 1 or float(data["temperature"]["Puffer1"]) > int(data["status"]["eloremeno_max"]) or  int(data["status"]["Gazfutes"]) == 0):
      data["status"]["Gazkazan"] = 0 
      
      #Puffertöltő kikapcsolás időzítés beállítása (hűti a gázkazánt, kiveszi a maradékhőt)
      if ( int(data["status"]["Gazfutes"]) == 1):  #Csak gázfűtés esetében van rá szükség
        data["status"]["puffertolto_off_schedule"] = calendar.timegm(time.gmtime())
        data["status"]["puffertolto_off_trigger"] = 1
        
    elif ( int(data["status"]["Gazfutes"]) == 1 and int(data["status"]["internal_temperature_ok"]) == 0 and float(data["temperature"]["Puffer1"]) < int(data["status"]["eloremeno_min"]) ):
      data["status"]["Gazkazan"] = 1 
  #  else:
  #    data["status"]["Gazkazan"] = 0 

    write_to_file(data,None)

while True:
  device_folders = glob.glob(base_dir + '28*')
  for df in device_folders:
      keystring = df.split("-")[-1]
      key = sensors.get(keystring) 
      temporary[key] = str(read_temp(df))
  write_to_file(temporary,"temperature")
  fillPuffer()
  radiatorPump()
  gazKazan()
  time.sleep(10)
