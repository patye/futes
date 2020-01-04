#!/usr/bin/python3

#Rele sorszamok
#1 - lakas keringeto
#2 - puffertolto
#3 - kazan on-off
#4 - ures
#5 - also nyit
#6 - also zar
#7 - felso-nyit
#8 - felso zar

import time
import tosr0x
import json
import syslog
th = tosr0x.handler(devicePaths=['/dev/ttyUSB0'], relayCount=8)
myTosr0x = th[0]
previous = {}

zona_also_orig = 9
zona_felso_orig = 9 


def zona(also, felso):
    global zona_also_orig
    global zona_felso_orig
    if(also != zona_also_orig):
        change_zona("also", also)
        zona_also_orig = also
    if(felso != zona_felso_orig):
        change_zona("felso", felso)
        zona_felso_orig = felso


def change_zona(szint, ertek):
    if (szint == "also" and ertek == 1):
       myTosr0x.set_relay_position(5,1)
       myTosr0x.set_relay_position(6,0)
       time.sleep(8)
    if (szint == "also" and ertek == 0):
       myTosr0x.set_relay_position(5,0)
       myTosr0x.set_relay_position(6,1)
       time.sleep(8)
    if (szint == "felso" and ertek == 1):
       myTosr0x.set_relay_position(7,1)
       myTosr0x.set_relay_position(8,0)
       time.sleep(8)
    if (szint == "felso" and ertek == 0):
       myTosr0x.set_relay_position(7,0)
       myTosr0x.set_relay_position(8,1)
       time.sleep(8)
    for pos in range(5,9):
       myTosr0x.set_relay_position(pos,0)








while True:
    path = "/home/pi/code/system-json.txt"
    try:    
      with open(path) as json_file:
        data = json.load(json_file)

      if (data != previous):
        syslog.syslog("Puffer ertek: " + str(data["status"]["Puffertolto"]))
        myTosr0x.set_relay_position(1,int(data["status"]["Lakas_keringeto"]))
        myTosr0x.set_relay_position(2,int(data["status"]["Puffertolto"]))
        myTosr0x.set_relay_position(3,int(data["status"]["Gazbojler"]))
        previous = data
        zona_also  = int(data["status"]["Also_futes"])
        zona_felso = int(data["status"]["Felso_futes"])
        zona(zona_also, zona_felso)
    except:
      syslog.syslog("Hiba a json olvasaskor")  
    time.sleep(3)
