from textwrap import indent
from flask import Flask, redirect, request, abort, make_response , render_template
import numpy as np
import pandas as pd
import requests
import time
import json
import pyodbc
import configparser
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from sqlalchemy import true

server = 'americanassmysqlserver.database.windows.net'
database = 'telemetry'
username = 'azureuser'
password = '_AmericanAss'
driver= '{ODBC Driver 17 for SQL Server}'
cnxn = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

config = configparser.ConfigParser()
config.read('config.ini')

# initialize objects related to line-bot-sdk
line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'), timeout=3000)
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

app = Flask(__name__)

fetchFile = './fetch.json'  # file that store data from telemetry
simulateFile = './simulate.json'    # store data from simulator
controlFile = './control.json'      # control IOT device

# DeviceIP = '192.168.10.95'
# url = 'http://'+DeviceIP+':7000'
url = 'http://20.39.59.50:5000'

# home page
@app.route("/", methods=['GET','POST'])
def homePage():
    return "Welcome to CareerHack HomePage"

# Get data from Device EZ-33 
@app.route("/telemetry", methods=['GET','POST'])
def telemetry():
    data = request.get_json()
    powerConsumption1 = data['telemetry']['powerConsumption1']
    print("powerConsumption 1 :",powerConsumption1)
    powerConsumption2 = data['telemetry']['powerConsumption2']
    print("powerConsumption 2 :",powerConsumption2)
    powerConsumption3 = data['telemetry']['powerConsumption3']
    print("powerConsumption 3 :",powerConsumption3)

    with open(fetchFile,'w',encoding='utf-8') as file :
        json.dump(data,file)
    
    return "telemetry"

# send Post to device
@app.route("/control", methods=['GET','POST'])
def control():
    with open(controlFile,'r',encoding='utf-8') as file :
        data = json.load(file)
    requests.post(url+'/control',json.dumps(data))
    return 'control output success'

# receive Post from simulator
@app.route("/simulate", methods=['GET','POST'])
def simulate():
    currTime = time.strftime('%H:%M:%S', time.localtime())
    Month = time.strftime('%B', time.localtime())
    Day = time.strftime('%d', time.localtime())
    data = request.get_json(force=True)
    print(data)
    powerConsumption1 = data['Device_1']
    powerConsumption2 = data['Device_2']
    powerConsumption3 = data['Device_3']
    # table = Month + '_' + Day
    # cursor.execute('''INSERT INTO '''+table+'''(Time, Device_1, Device_2,Device_3) VALUES (?,?,?,?)''',
    #                 (currTime,powerConsumption1,powerConsumption2,powerConsumption3))
    table = 'AmericanAssDevice'
    cursor.execute('''INSERT INTO '''+table+'''(Date, Device_1, Device_2,Device_3) VALUES (?,?,?,?)''',
                    (currTime,powerConsumption1,powerConsumption2,powerConsumption3))
    cnxn.commit()
    return 'simulate input success'

# get data from database and do regression and predict
@app.route("/database",methods=['GET','POST'])
def database():
    Month = time.strftime('%B', time.localtime())
    recordDay = [15,16,17,18,19,20,21,22,23]
    Matrix = np.zeros((3,len(recordDay),8640))  # 3devices , recordDay , 8640data 
    for index in range(len(recordDay)) :
        day = recordDay[index]
        table = Month + '_' + str(day)
        sql = "SELECT * FROM telemetry.dbo.{}".format(table)
        df = pd.read_sql(sql,cnxn)
        Matrix[0][index] = df.Device_1
        Matrix[1][index] = df.Device_2
        Matrix[2][index] = df.Device_3
    # regression here ...

    # after prediction
    # we compare the 'predict watts' and the 'current watts'
    # if there are  big differences between the predict watts and the current watts
    # send alert to users ...

    return 'database'

# LineBot default function
@app.route('/callback', methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# get Event
@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    userID = event.source.user_id
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Received Message'))
    # reply success message
    text = str(event.message.text).lower()
    if text == 'current':
        with open(controlFile,'r',encoding='utf-8') as file :
            data = json.load(file)
        line_bot_api.push_message(userID,TextSendMessage(text=json.dumps(data,indent=4)))
    elif text == 'help':
        text = 'If you want to contorl the device :\nset \'turn\' to true or false\nset \'intensity\' with a number\n'
        text += 'i.e. key1 turn:true\nor key3 intensity:9'
        line_bot_api.push_message(userID,TextSendMessage(text=text))
    elif ':' in text :
        with open(controlFile,'r',encoding='utf-8') as file :
            data = json.load(file)
        command = text.split(' ')
        key = command[0]
        device = data[key]
        feature,mode = command[1].split(':')
        if mode.isdigit() == True :
            mode = int(mode)
            device[feature] = mode
        else:
            if mode == 'true':
                device[feature] = True
            elif mode == 'false':
                device[feature] = False
        line_bot_api.push_message(userID,TextSendMessage(text=json.dumps(data,indent=4)))
        with open(controlFile,'w',encoding='utf-8') as outfile :
            json.dump(data,outfile,indent=2)
        requests.post(url+'/control',json.dumps(data))

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
    except :
        pass
    return 'change success'
# receive  control change from simulator
@app.route("/controlChange", methods=['GET','POST'])
def controlChange():
    data = request.get_json(force=True)
    with open(controlFile,'w',encoding='utf-8') as outfile :
        json.dump(data,outfile,indent=2)
    return 'controlChange'

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=5000)