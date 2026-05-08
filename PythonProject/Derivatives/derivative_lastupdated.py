import datetime

from SQL.Connectingmysql import mydb

#----------------To fetch the last file uploaded in BULK DEAL table----------------

cursor = mydb.cursor()
selectData= '''SELECT 'derivativelast' AS Table_Name, MAX(T_DATE) AS Last_Date FROM derivative_bhavcopy;'''
cursor.execute(selectData)
records=cursor.fetchone()
# print('last_date+record is ',records[1])
last_date_record=records[1]+datetime.timedelta(days=1)
# print(last_date_record)
cursor.close()