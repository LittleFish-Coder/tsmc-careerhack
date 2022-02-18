from flask import Flask, redirect, request, abort, make_response , render_template
import requests
import time
import json
from simulator2 import Device_1 , Device_2 , Device_3 , Simulate 
import threading

d1 = Device_1()
d2 = Device_2()
d3 = Device_3()
devices = [d1 , d2 , d3]
data_post= {"Device_1" : 0 , "Device_2" : 0 , "Device_3" : 0}


app = Flask(__name__)

fetchFile = './fetch.json'
simulateFile = './simulate.json'
controlFile = './control.json'

# HostIP = '192.168.10.112'
# url = 'http://'+HostIP+':5000'
url = 'https://45c5-111-255-202-67.ngrok.io'

@app.route("/", methods=['GET','POST'])
def homePage():
    return "Welcome to CareerHack HomePage"

@app.route("/control", methods=['GET','POST'])
def control():  
    data = request.get_json(force=True)
    #with open(controlFile,'w',encoding='utf-8') as outfile :
    #    json.dump(data,outfile,indent=2)
    global data_post
    data_post["Device_1"] = Simulate(data["key1"]["turn"], data["key1"]["intensity"] ,d1)
    data_post["Device_2"] = Simulate(data["key2"]["turn"], data["key2"]["intensity"] ,d2)
    data_post["Device_3"] = Simulate(data["key3"]["turn"], data["key3"]["intensity"] ,d3)
    print(data_post)
    return 'control input success'

@app.route("/simulate", methods=['GET','POST'])
def simulate():
    global data_post
    while True :
        time.sleep(10)
        requests.post(url+'/simulate',json.dumps(data_post))
        print(data_post)
    return 'simulate output success'

# panel
@app.route("/panel", methods=['GET','POST'])
def panel():
    return render_template('index.html')

# apply change to control.json
@app.route("/change", methods=['GET','POST'])
def change():
    with open(controlFile,'r',encoding='utf-8') as file :   # write input data to simulate.json
        data = json.load(file)
    device1_turn = request.values['device1_turn']
    device1_intensity = request.values['device1_intensity']
    device2_turn = request.values['device2_turn']
    device2_intensity = request.values['device2_intensity']
    device3_turn = request.values['device3_turn']
    device3_intensity = request.values['device3_intensity']
    try :
        data['key1']['turn'] = True  if device1_turn.lower() == 'true' else False
        data['key1']['intensity'] = int(device1_intensity)
        data['key2']['turn'] = True  if device2_turn.lower() == 'true' else False
        data['key2']['intensity'] = int(device2_intensity)
        data['key3']['turn'] = True  if device3_turn.lower() == 'true' else False
        data['key3']['intensity'] = int(device3_intensity)
        with open(controlFile,'w',encoding='utf-8') as outfile :
            json.dump(data,outfile,indent=2)
        global data_post
        data_post["Device_1"] = Simulate(data["key1"]["turn"], data["key1"]["intensity"] ,d1)
        data_post["Device_2"] = Simulate(data["key2"]["turn"], data["key2"]["intensity"] ,d2)
        data_post["Device_3"] = Simulate(data["key3"]["turn"], data["key3"]["intensity"] ,d3)            

        requests.post(url+'/controlChange',json.dumps(data))
    except :
        pass
    return 'change success'

if __name__ == "__main__":
    threading.Thread(target=simulate).start()
    app.run(host='0.0.0.0',debug= False , port=5000)