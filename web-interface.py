#!/usr/bin/python3

from flask import Flask,redirect
import json
import time
import syslog


app = Flask(__name__)

path = "/home/pi/code/system-json.txt"
def getactual():

  with open(path) as json_file:
    data = json.load(json_file)
  # for temp in json.load(json_file):
 
  result = "Kazán kilépő: " + data["temperature"]["Kazan_kilepo"] + "</br>"
  result += "Puffer1: " + data["temperature"]["Puffer1"] + "</br>"
  result += "Puffer2: " + data["temperature"]["Puffer2"] + "</br>"
  result += "Puffer3: " + data["temperature"]["Puffer3"] + "</br>"
  result += "Puffer4: " + data["temperature"]["Puffer4"] + "</br>"
  result += "Fűtés előre: " + data["temperature"]["Futes_elore"] + "</br>"
  result += "Fűtés vissza: " + data["temperature"]["Futes_vissza"] + "</br>"
  result += "<hr>"
  result += "Alsó szint fűtés: "
  result += "BEKAPCSOLT" if int(data["status"]["Also_futes"]) == 1 else "KIKAPCSOLT"
  result += " <a href=\"/control/Also_futes/0\">Kikapcsolás</a>" if int(data["status"]["Also_futes"]) == 1 else " <a href=\"/control/Also_futes/1\">Bekapcsolás</a>" 
  result += "</br>"
  result += "Felső szint fűtés: "
  result += "BEKAPCSOLT" if int(data["status"]["Felso_futes"]) == 1 else "KIKAPCSOLT"
  result += " <a href=\"/control/Felso_futes/0\">Kikapcsolás</a>" if int(data["status"]["Felso_futes"]) == 1 else " <a href=\"/control/Felso_futes/1\">Bekapcsolás</a>" 
  return result


def change_control(szint, beki):
    with open(path) as json_file:
      data = json.load(json_file)
    data["status"][szint] = beki
    with open(path,"w") as outfile:
        json.dump(data, outfile)

    return True


@app.route('/')
def hello_world():
  return getactual()


@app.route('/control/<szint>/<beki>')
def control(szint,beki):
  syslog.syslog("Szint: " + szint + " | beki: " + beki)
  change_control(szint, beki)
  print("Szint: " + szint + " | beki: " + beki)
  time.sleep(2)
  return redirect("/", code = 302)



if __name__ == '__main__':
  app.run(host="0.0.0.0", port="8080")
