import datetime
#lastupdated=''
from SQL.Connectingmysql import mydb

#----------------To fetch the last file uploaded in BULK DEAL table----------------

cursor = mydb.cursor()
selectData = """
SELECT 'index_api_data' AS table_name,
       MAX(index_date) AS last_date
FROM index_api_data;
"""
cursor.execute(selectData)
records=cursor.fetchone()
print('last_date+record is ',records[1])
last_date_record=records[1]+datetime.timedelta(days=1)
print(records)
cursor.close()