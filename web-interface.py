#!/usr/bin/python3

from flask import Flask, redirect, request, render_template
import json
import time
import syslog


app = Flask(__name__)

path = "/home/pi/code/system-json.txt"
hmv = "/home/pi/code/hmvdata.json"
def getactual():

  with open(path) as json_file:
    data = json.load(json_file)
  with open(hmv) as json_file:
    hmvdata = json.load(json_file)
  # for temp in json.load(json_file):
  return render_template(
      "index.html",
      data=data,
      hmvdata=hmvdata
  )

def tempupdateformpage():

    with open(path) as json_file:
       data = json.load(json_file)
    return render_template("tempupdate.html", data=data)



@app.route('/hmvtemperature', methods=['POST'])
def hmvtemperature():
  temp=request.json.get('melegviz')
  fustgaz=request.json.get('fustgaz')
  kazanhaz_belso=request.json.get('kazanhaz_belso')
  print("Hmvtemp: " + temp)
  with open(hmv) as json_file:
    data = json.load(json_file)
  data["hmv"] = temp
  data["fustgaz"] = fustgaz
  data["kazanhaz_belso"] = kazanhaz_belso

  with open(hmv,"w") as outfile:
      json.dump(data, outfile)
  return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 


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
    data["status"][szint] = int(beki)
    with open(path,"w") as outfile:
        json.dump(data, outfile)

    return True


def fokapcsolo_change(beki):
    with open(path) as json_file:
      data = json.load(json_file)
    data["status"]["internal_temperature_ok"] = int(beki)
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

@app.route('/control/melegviz/<beki>')
def melegviz(beki):
    with open(path) as json_file:
        data = json.load(json_file)
    data["status"]["Melegviz"] = beki
    data["status"]["Gazkazan"] = beki
    with open(path, "w") as outfile:
        json.dump(data, outfile)
    time.sleep(1)
    return redirect("/", code = 302)

@app.route('/tempupdateform')
def tempupdateform():
    return tempupdateformpage() 

@app.route('/xmaslight/<beki>')
def xmaslight(beki):
    with open(path) as json_file:
      data = json.load(json_file)
      data["status"]["xmaslight"] = beki
      with open(path,"w") as outfile:
          json.dump(data,outfile)

if __name__ == '__main__':
  app.run(host="0.0.0.0", port="8080")
