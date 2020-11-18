#!/usr/bin/python3

from flask import Flask,redirect,request
import json
import time
import syslog


app = Flask(__name__)

path = "/home/pi/code/system-json.txt"
def getactual():

  with open(path) as json_file:
    data = json.load(json_file)
  # for temp in json.load(json_file):
 
  result = "<!doctype html><html class=\"no-js\" lang=\"\"><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><meta http-equiv=\"refresh\" content=\"5\"></head>"
  result += "<body>"
  result += "Kazán kilépő: " + data["temperature"]["Kazan_kilepo"] + "</br>"
  result += "Puffer1: " + data["temperature"]["Puffer1"] + "</br>"
  result += "Puffer2: " + data["temperature"]["Puffer2"] + "</br>"
  result += "Puffer3: " + data["temperature"]["Puffer3"] + "</br>"
  result += "Puffer4: " + data["temperature"]["Puffer4"] + "</br>"
  result += "Fűtés előre: " + data["temperature"]["Futes_elore"] + "</br>"
  result += "Fűtés vissza: " + data["temperature"]["Futes_vissza"] + "</br>"




  result += "<hr>"
  result += "Üzemmód (csak akkor lehet átváltani, ha a kazánházban kézzel átállítottad a rendszert gázfűtésre): "
  result += "GÁZ" if int(data["status"]["Gazfutes"]) == 1 else "FAFŰTÉS"
  result += " <a href=\"/control/uzemmod/0\">Átváltás fafűtésre</a>" if int(data["status"]["Gazfutes"]) == 1 else " <a href=\"/control/uzemmod/1\">Átváltás gázfűtésre</a>" 
  result += "</br>"

  result += "<hr>"
  result += " <a href=\"/tempupdateform\">Hőmérséklet módosítása</a>" 
  result += "</br>"
  
  
  result += "<hr>"
  result += "Főkapcsoló: "
  result += "BEKAPCSOLT" if int(data["status"]["internal_temperature_ok"]) == 0 else "KIKAPCSOLT"
  result += " <a href=\"/fokapcsolo/1\">Kikapcsolás</a>" if int(data["status"]["internal_temperature_ok"]) == 0 else " <a href=\"/fokapcsolo/0\">Bekapcsolás</a>" 
  result += "</br>"
  

  result += "<hr>"
  result += "Alsó szint fűtés: "
  result += "BEKAPCSOLT" if int(data["status"]["Also_futes"]) == 1 else "KIKAPCSOLT"
  result += " <a href=\"/control/Also_futes/0\">Kikapcsolás</a>" if int(data["status"]["Also_futes"]) == 1 else " <a href=\"/control/Also_futes/1\">Bekapcsolás</a>" 
  result += "</br>"
  
  
  result += "Felső szint fűtés: "
  result += "BEKAPCSOLT" if int(data["status"]["Felso_futes"]) == 1 else "KIKAPCSOLT"
  result += " <a href=\"/control/Felso_futes/0\">Kikapcsolás</a>" if int(data["status"]["Felso_futes"]) == 1 else " <a href=\"/control/Felso_futes/1\">Bekapcsolás</a>" 
  result += "<hr>"
  if (data["status"]["Puffertolto"] == 1):
      result += "<img src=\"static/grundfos.jpg\" height=\"100px\">"
  if (data["status"]["Lakas_keringeto"] == 1):
      result += "<img src=\"static/wilo.jpg\" height=\"100px\">"
  if (data["status"]["Gazkazan"] == 1):
      result += "<img src=\"static/blue-flame-icon.jpg\" height=\"100px\">"
  result += "</body></html>"
  return result

def tempupdateformpage():

    with open(path) as json_file:
       data = json.load(json_file)

    result = "<h2>Előremenő módosítása</h2>"
    result += "<form action=\"tempupdateformpost\" method=\"post\">"
    result += "<label for=\"eloremeno_min\">Előremenő min: </label><br>"
    result += "<input type=\"number\" name=\"eloremeno_min\" value="
    result += str(data["status"]["eloremeno_min"])
    result += ">"
    result += "<input min=\"30\" max=\"70\"  type=\"submit\" value=\"Mentés\"> </form>" 
    return result


@app.route('/tempupdateformpost', methods=['POST'])
def tempupdateformpost():
    eloremeno_min=int(request.form['eloremeno_min'])
    with open(path) as json_file:
      data = json.load(json_file)
    data["status"]["eloremeno_min"] = eloremeno_min
    data["status"]["eloremeno_max"] = eloremeno_min + 10

    with open(path,"w") as outfile:
        json.dump(data, outfile)

    return redirect("/", code = 302)

def change_control(szint, beki):
    with open(path) as json_file:
      data = json.load(json_file)
    data["status"][szint] = beki
    with open(path,"w") as outfile:
        json.dump(data, outfile)

    return True


def fokapcsolo_change(beki):
    with open(path) as json_file:
      data = json.load(json_file)
    data["status"]["internal_temperature_ok"] = beki
    with open(path,"w") as outfile:
        json.dump(data, outfile)

    return True


def uzemmod_change(gaz):

    with open(path) as json_file:
      data = json.load(json_file)
    data["status"]["Gazfutes"] = gaz
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
  time.sleep(2)

  return redirect("/", code = 302)

@app.route('/fokapcsolo/<beki>')
def fokapcsolo(beki):
  syslog.syslog("Fokapcsolo: | beki: " + beki)
  fokapcsolo_change(beki)
  time.sleep(1)
  return redirect("/", code = 302)

@app.route('/control/uzemmod/<gaz>')
def uzemmod(gaz):
    uzemmod_change(gaz)
    time.sleep(1)
    return redirect("/", code = 302)

@app.route('/tempupdateform')
def tempupdateform():
    return tempupdateformpage() 

if __name__ == '__main__':
  app.run(host="0.0.0.0", port="8080")
