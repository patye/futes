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


#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')

path = "/home/patye/futes/system-json.txt"
temperaturefile = "/home/patye/futes/temperature.json"
hmvfile = "/home/patye/futes/hmvdata.json"
hysteresis_up = False
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
    f=open("/home/patye/futes/system-json.txt","w+")
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
  #  with open(temperaturefile) as json_file:
  #    temperature = json.load(json_file)
  #  data["temperature"]=temperature
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
#  with open(temperaturefile) as json_file:
#      temperature = json.load(json_file)
#    data["temperature"]=temperature
    turn_off_temp = min(max(65,float(data["temperature"]["Puffer4"])+5),80)
    turn_off_temp_new = min(max(65,float(data["temperature"]["Puffer1"])+5),80)
    turn_on_temp = min((turn_off_temp + 10),92)

    logger.info("Puffertolto off temp: " + str(turn_off_temp))
    logger.info("Puffertolto on temp: " + str(turn_on_temp))



    #Puffertöltő bekapcsolás, ha megy a gázkazán, vagy meleg a fatüzelésű kazán
    if ( float(data["temperature"]["Kazan_kilepo"]) > turn_on_temp or ( int(data["status"]["Gazkazan"]) == 1 and int(data["status"]["Melegviz"]) == 0 )):
          data["status"]["Puffertolto"] = 1
          logger.info("Puffertolot bekapcs, mert gazkazan megy")

    #Puffertöltő kikapcsolása fafűtés esetén - védi a fatüzelésű kazánk a kihűlés ellen
    if ( float(data["temperature"]["Kazan_kilepo"]) < turn_off_temp and  int(data["status"]["Gazfutes"]) == 0 ):
          data["status"]["Puffertolto"] = 0

    #Puffertöltő kikapcsolás ha letelt-e a beégetett érték
    if ( ( int(data["status"]["puffertolto_off_schedule"]) + 180 <  calendar.timegm(time.gmtime()) ) and data["status"]["puffertolto_off_trigger"] == 1 and  data["status"]["Gazkazan"] == 0):
        data["status"]["Puffertolto"] = 0
        data["status"]["puffertolto_off_trigger"] = 0
        logger.info("Puffertolto kikapcs, mert letelt  a timeout")

    write_to_file(data,None)


def hmv_decision(hmv_on, temperature):

    global hysteresis_up
    hmv_hysteresis = {
        "temp_low": 35,
        "temp_high": 55
    }

    logger.info("Temperature is: " + str(temperature))
    logger.info("Hysteresis up is: " + str(hysteresis_up))
    logger.info("HMV on is: " + str(hmv_on))
    logger.info("HMV hysteresis high value is : " + str(hmv_hysteresis["temp_high"]))
    logger.info("Hmv hysteresis low value: " + str(hmv_hysteresis["temp_low"]))

    if hmv_on and (temperature >= hmv_hysteresis["temp_high"]):
        logger.info("Case#1 - Boiler decision is: %s", False)
        hysteresis_up = False
        return False
    elif hmv_on and (temperature <= hmv_hysteresis["temp_low"]):
        hysteresis_up = True
        logger.info("Case#2 - Boiler decision is: %s", True)
        return True
    elif hmv_on and hmv_hysteresis:
        logger.info("Case#3 - Boiler decision is: %s", True)
        return True
    else:
        logger.info("Case#4 - Boiler decision is: %s", False)
        return False



def gazKazan():

    with open(path) as json_file:
       data = json.load(json_file)
    with open(temperaturefile) as json_file:
      temperature = json.load(json_file)
    with open(hmvfile) as json_file:
        hmv = json.load(json_file)
    data["temperature"]=temperature

    #Gazkazan kikapcsolasa, ha nincs sem melegviz igeny, sem futesi igeny
    # if (
    #         (int(data["status"]["internal_temperature_ok"]) == 1
    #         or float(data["temperature"]["Puffer1"]) > int(data["status"]["eloremeno_max"])
    #         or int(data["status"]["Gazfutes"]) == 0
    #         or hmv_decision.hmv_decision())
    #         and int(data["status"]["Melegviz"]) == 0
    #    ):
    #       data["status"]["Gazkazan"] = 0
    #
    #Gazfutes bekapcsolva, a puffer1 nem eri el az elvart eloremeno erteket. #TODO törlendő működési mód
    # if ( int(data["status"]["Gazfutes"]) == 1 and int(data["status"]["internal_temperature_ok"]) == 0 and float(data["temperature"]["Puffer1"]) < int(data["status"]["eloremeno_min"]) ):
    #   data["status"]["Gazkazan"] = 1

    #Gazkazan be, ha van melegvizigeny es a hiszterezis is ezt kivanja
    logger.info("status_melegviz: " + str(data["status"]["Melegviz"]) )
    logger.info("hmv_on is: " + str(int(data["status"]["Melegviz"]) == 1))
    data["status"]["Gazkazan"] = int(hmv_decision(int(data["status"]["Melegviz"]) == 1,float(hmv["hmv"])))
    data["status"]["Hmv_tolto"] = int(hmv_decision(int(data["status"]["Melegviz"]) == 1,float(hmv["hmv"])))
    write_to_file(data,None)

while True:
  fillPuffer()
  radiatorPump()
  gazKazan()
  logger.info("Hysteresis up: " + str(hysteresis_up))
  time.sleep(10)
