import pyodbc
import pandas as pd

server = 'americanassmysqlserver.database.windows.net'
database = 'telemetry'
username = 'azureuser'
password = '_AmericanAss'
driver= '{ODBC Driver 17 for SQL Server}'

cnxn = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

# drop table
# cursor.execute('''
#             DROP TABLE AmericanAssDevice;
#                 ''')

# create table
# cursor.execute('''
# 		CREATE TABLE January_17 (
#             Time varchar(255),
#             Device_1 DECIMAL(8,2),
#             Device_2 DECIMAL(8,2),
#             Device_3 DECIMAL(8,2)
# 			)
#                ''')

# insert
# counter = 0
# for Time , Device_1 , Device_2 , Device_3 in zip(df.Time,df.Device_1,df.Device_2,df.Device_3):
#     cursor.execute('''INSERT INTO January_17 (Time, Device_1, Device_2,Device_3) VALUES (?,?,?,?)''',
#                 (Time,Device_1,Device_2,Device_3))
#     counter += 1
#     print(counter)

# select
# cursor.execute('''SELECT * FROM telemetry.dbo.January_15''')
# for row in cursor:
#     print(row)

cnxn.commit()