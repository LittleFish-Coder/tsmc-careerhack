from flask import Flask, request
import json
import matplotlib.pyplot as plt

app = Flask(__name__)

address = "https://dcd3-218-166-157-170.ngrok.io"
receiveData = './receive.json'

@app.route("/", methods=['GET'])
def hello():
    return "Welcome to CareerHack HomePage"

@app.route("/IOT", methods=['GET', 'POST'])
def telemetry():
    data = request.get_json()
    with open(receiveData, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    powerConsumption_1 = data['telemetry']['powerConsumption1']
    # powerConsumption_2 = data['telemetry']['powerConsumption2']
    # powerConsumption_3 = data['telemetry']['powerConsumption3']
    print(powerConsumption_1)

if __name__ == "__main__":
    app.run(debug=True , port=5000)        # 啟動app（Flask物件）