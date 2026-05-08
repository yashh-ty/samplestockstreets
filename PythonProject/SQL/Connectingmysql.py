import pymysql
mydb = pymysql.connect(
    host="127.0.0.1",
    user="root",
    password="Shankar@123",
    database="stock_streets",
    port=3306,
    autocommit=False
)

cursor = mydb.cursor()
# print("✅ DB Connected")