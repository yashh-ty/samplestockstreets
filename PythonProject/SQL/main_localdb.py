
import pymysql
try:
    mydb = pymysql.connect(host ='192.168.1.40',
                                   user ='Yash_Dev',
                                   password ='@Yash123#',
                                   database ='stock_streets',
                                   port=3306)
    print("Main_Local_db connection sucessfull")
except Exception as e:
    print(e)
    print("Error Occurred while connecting to server")



