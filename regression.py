from turtle import shape
from sklearn.metrics import mean_squared_error as MSE
from sklearn.preprocessing import PolynomialFeatures as PF
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import pyodbc

server = 'americanassmysqlserver.database.windows.net'
database = 'telemetry'
username = 'azureuser'
password = '_AmericanAss'
driver= '{ODBC Driver 17 for SQL Server}'

cnxn = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

Month = time.strftime('%B', time.localtime())
recordDay = [15,16,17,18,19,20,21,22,23]
Matrix = np.zeros((3,len(recordDay),8640))
for index in range(len(recordDay)) :
    day = recordDay[index]
    table = Month + '_' + str(day)
    sql = "SELECT * FROM telemetry.dbo.{}".format(table)
    df = pd.read_sql(sql,cnxn)
    Matrix[0][index] = df.Device_1
    Matrix[1][index] = df.Device_2
    Matrix[2][index] = df.Device_3

model = make_pipeline(PF(1), LinearRegression())

Device_1 = Matrix[0].astype(int)    # x:time y:day
Device_2 = Matrix[1].astype(int)
Device_3 = Matrix[2].astype(int)

# Device_1 = np.transpose(Device_1)   # x:day y:time
print(Device_1.shape)

# for day in Device_1[:,0] :
#     print(day)

# recordDay = [15,16,17,18,19,20,21,22,23]
# for day in range(len(recordDay)) : 
#     singleDay = Device_1[day]
#     watts = singleDay[:]
#     plt.plot(range(len(singleDay)),watts)
# plt.show()

numofDay = 9

X = np.array(numofDay * list(range(8640))).reshape(1, -1)
# X = np.array(numofDay * list(range(8640))).reshape(-1, 1)
Y = Device_1.reshape((8640*numofDay, 1))

# plt.scatter(X, Y)
# plt.show()

# X_test = []
# Y_test = []

model.fit(X,Y)
# model.fit(X,np.transpose(Y))

X_test = np.array(range(8640)).reshape(1, -1)
# X_test = np.array(range(8640)).reshape(-1, 1)
Y_pred = model.predict(X_test)

plt.scatter(Y_pred, X_test)
plt.show()

# mse = MSE(Y_pred, Y_test)