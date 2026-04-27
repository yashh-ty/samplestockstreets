import mysql.connector
mydb = ''
try:
    mydb = mysql.connector.connect(host ='147.93.97.191',
                                   user ='client',
                                   password ='StockStreets@2026',
                                   database ='stock_streets',
                                   port=3306)
    print("vps_db connection sucessfull")
except:
    print("Error Occurred while connecting to server")
