import datetime
from SQL.Connectingmysql import mydb

#----------------To fetch the last file uploaded in BULK DEAL table----------------

cursor = mydb.cursor()
selectData= '''SELECT 'Bhavcopy' AS Table_Name, MAX(T_DATE) AS Last_Date FROM Bhavcopy;'''
cursor.execute(selectData)
records=cursor.fetchone()
print('last_date+record is ',records[1])
last_date_record=records[1]+datetime.timedelta(days=1)
print(records)
cursor.close()
if __name__ == "__main__":
    print(records)
    print('last_date record is ', records[1])


