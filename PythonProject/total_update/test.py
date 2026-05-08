import datetime
from SQL.VPS_Connect_SQL import mydb
cursor=mydb.cursor()
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

total_db_size='''SELECT 
    table_schema,
    ROUND(SUM(data_length + index_length) / 1024 / 1024 / 1024, 3) AS total_size_gb
FROM information_schema.tables
WHERE table_schema = 'stock_streets'
GROUP BY table_schema;'''

cursor.execute(total_db_size)
total_size= cursor.fetchone()
total_size=float(total_size[1])


d={"options_candles":"candle_date",
"mutual_fund_nav":"nav_date",
"derivative_bhavcopy":"T_DATE",
"bhavcopy":"T_DATE",
       "fpi":"TRANSACTION_DATE",
       "n50":"created_at",
       "nauto":"created_at",
       "nbank":"created_at",
       "nfmcg":"created_at",
       "nfs":"created_at",
       "nit":"created_at",
       "nm100":"created_at",
       "nm50":"created_at",
       "nmetal":"created_at",
       "nn50":"created_at",
       "npharma":"created_at",
       "ns100":"created_at",
       "ns50":"created_at",
       "nse_index":"T_DATE",
      "symbol_cat":"created_at",
    "agg_industrywise":"T_date","bulk_deal":"DATE","block_deal":"T_DATE",
    "index_api_data":"index_date","fii_derivatives_stats":"report_date","fii_dii":"DATE",
    "registered_users":"created_at",
    "PE":"T_DATE"

}


def report(table_name):


    value=d[table_name]

    table_size_query=f'''SELECT
    ROUND((data_length + index_length) / 1024 / 1024 / 1024, 3) AS size_gb
    FROM information_schema.tables
    WHERE table_schema = 'stock_streets'
    AND table_name = "{table_name}";'''

    cursor.execute(table_size_query)
    size= cursor.fetchone()



    selectData= f'''SELECT
        '{table_name}' AS Table_Name,
        COUNT(*) AS Total_rows,
        SUM(created_at >= CURDATE()) AS Todays_rows,
        MIN({value}) AS START_DATE,
        MAX({value}) AS END_DATE,
        MAX(created_at) as LAST_UPDATE
        FROM stock_streets.{table_name}
    ;'''

    cursor.execute(selectData)
    data=cursor.fetchone()

    TABLE_NAME=data[0]
    TOTAL_ROWS=data[1] if data[1] else "-"
    IN_TODAY=data[2] if data[2] else "-"
    START_DATE=data[3].strftime("%d-%m-%Y") if data[3] else "-"
    END_DATE=data[4].strftime("%d-%m-%Y") if data[4] else "-"
    LAST_UPDATE=data[5].strftime("%Y-%m-%d %H:%M:%S")if data[4] else "-"
    SIZE_GB = float(size[0]) if data else "-"



    report_data=[[TABLE_NAME,TOTAL_ROWS,IN_TODAY,START_DATE,END_DATE,LAST_UPDATE,SIZE_GB]]
    return report_data

total_report=[]
for i in d:
    data=report(i)
    total_report=total_report+data




#CREATION OF PDF AND SAVING THE PDF  IN LOCAL SYSTEM

def pdf_creation():
    total=[]
    for i,j in enumerate(total_report,start=1):
        total.append([i]+j)


    headers=["SRNO","TABLE_NAME","ROWS","IN_TODAY","START_DATE","END_DATE","LAST_UPDATE","SIZE_GB"]
    data = [headers] + total
    f =datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path=fr"D:\report_{f}.pdf"
    doc = SimpleDocTemplate(file_path,
        pagesize=landscape(letter),
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20)

    styles = getSampleStyleSheet()

    date_title=datetime.datetime.now().strftime("%d-%m-%Y")
    title = Paragraph(f"Daily Database Report {date_title} {total_size}GB", styles['Title'])


    table = Table(data,colWidths=[40, 120, 80, 80, 80, 80, 100, 60])

    table.setStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ])
    elements = []
    elements.append(title)
    elements.append(Spacer(1, 20))  # space after title
    elements.append(table)
    doc.build(elements)
    return file_path


import smtplib
from email.message import EmailMessage

def send_email_with_attachment(file_path):
    sender_email = os.getenv("EMAIL_SECONDARY")
    app_password = os.getenv("APP_PASSWORD_SECONDARY")
    receiver_email = "stockstreets14@gmail.com"

    msg = EmailMessage()
    msg['Subject'] = "Daily DB Report"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    msg.set_content("THIS IS YOUR DAILY REPORT ")

    # Attach PDF
    with open(file_path, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(file_path)

    msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)

    # Send email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, app_password)
        smtp.send_message(msg)

    print("Email sent successfully!")

file_path=pdf_creation()
send_email_with_attachment(file_path)




