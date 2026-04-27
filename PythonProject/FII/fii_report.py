from  FII.fii_last_updated import last_date_record
import datetime
from SQL.Connectingmysql import mydb
cursor=mydb.cursor()

start_date=last_date_record
# start_date=datetime.datetime.strptime("2026-04-20", "%Y-%m-%d").date()
end_date=datetime.datetime.now().date()
print(start_date,end_date)
selectData= '''SELECT 
        'fii_derivatives_stats' AS Table_Name, 
        MAX(created_at) AS Last_UPDATE, 
        COUNT(*) AS Total_rows 
    FROM stock_streets.fii_derivatives_stats
    WHERE DATE(report_date) >= %s AND DATE(report_date)<= %s;'''

cursor.execute(selectData,(start_date,end_date))
data=cursor.fetchone()

TABLENAME=data[0]
ROWS_INSERTED=data[2]
START_DATE=start_date.strftime("%d-%m-%Y")
END_DATE=end_date.strftime("%d-%m-%Y")
LAST_UPDATE=data[1].strftime("%d-%m-%Y")
LOCALORVPS="LOCAL"

fii_report_data=[[TABLENAME,ROWS_INSERTED,START_DATE,END_DATE,LAST_UPDATE,LOCALORVPS]]
