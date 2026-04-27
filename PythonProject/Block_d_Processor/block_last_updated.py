import datetime
from SQL.Connectingmysql import mydb

#----------------To fetch the last file uploaded in BULK DEAL table----------------

cursor = mydb.cursor()
selectData= '''SELECT 'block_deal' AS Table_Name, MAX(T_DATE) AS Last_Date FROM block_deal;'''
cursor.execute(selectData)
records=cursor.fetchone()
print('last_date+record is ',records[1])
last_date_record=records[1]+datetime.timedelta(days=1)
print(records)
cursor.close()