from  Mutual_fund.mutual_lastupdated  import last_date_record
import datetime
from SQL.Connectingmysql import mydb
from tabulate import tabulate
cursor=mydb.cursor()

# start_date=last_date_record
start_date=datetime.datetime.strptime("2026-04-20", "%Y-%m-%d").date()
end_date=datetime.datetime.now().date()
print(start_date,end_date)
selectData= '''SELECT 
        'mutual_fund_nav' AS Table_Name, 
        MAX(created_at) AS Last_UPDATE, 
        COUNT(*) AS Total_rows 
    FROM stock_streets.mutual_fund_nav
    WHERE DATE(nav_date) >= %s AND DATE(nav_date)<= %s;'''

cursor.execute(selectData,(start_date,end_date))
data=cursor.fetchone()

TABLENAME=data[0]
ROWS_INSERTED=data[2]
START_DATE=start_date.strftime("%d-%m-%Y")
END_DATE=end_date.strftime("%d-%m-%Y")
LAST_UPDATE=data[1].strftime("%d-%m-%Y")
LOCALORVPS="LOCAL"

mutual_report_data=[[TABLENAME,ROWS_INSERTED,START_DATE,END_DATE,LAST_UPDATE,LOCALORVPS]]
