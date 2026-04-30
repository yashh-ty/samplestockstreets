import datetime
from SQL.Connectingmysql import mydb
cursor=mydb.cursor()
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os


def column_exists(table_name, column_name):
    query = """
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'stock_streets'
    AND TABLE_NAME = %s
    AND COLUMN_NAME = %s
    """
    cursor.execute(query, (table_name,"created_at"))
    return cursor.fetchone()[0] > 0


def report(table_name):
    d={"bulk_deal":"DATE","bhavcopy":"T_DATE","block_deal":"T_DATE","derivative_bhavcopy":"T_DATE","pe":"T_DATE",
       "index_api_data":"index_date","mutual_fund_nav":"nav_date"

    }
    if column_exists(table_name, 'created_at'):
        last_update_query = "MAX(created_at)"
    else:
        last_update_query = "NULL"

    value=d[table_name]
    selectData= f'''SELECT
        '{table_name}' AS Table_Name,
        COUNT(*) AS Total_rows,
        MIN({value}) AS START_DATE,
        MAX({value}) AS END_DATE,
        {last_update_query} as LAST_UPDATE
        FROM stock_streets.{table_name}
    ;'''

    cursor.execute(selectData)
    data=cursor.fetchone()

    TABLENAME=data[0]
    TOTALROWS=data[1]
    START_DATE=data[2].strftime("%d-%m-%Y") if data[2] else None
    END_DATE=data[3].strftime("%d-%m-%Y") if data[3] else None
    LAST_UPDATE=data[4].strftime("%Y-%m-%d %H:%M:%S")if data[4] else None
    LOCALORVPS="LOCAL_DB"
    REPORT_DATE=datetime.datetime.now().strftime("%d-%m-%Y")


    report_data=[[TABLENAME,TOTALROWS,START_DATE,END_DATE,LAST_UPDATE,REPORT_DATE,LOCALORVPS]]
    return report_data

bhavcopy=report('bhavcopy')
bulk=report('bulk_deal')
block=report('block_deal')
derivative=report('derivative_bhavcopy')
pe=report('pe')
fiiderivatives=report('fii_derivatives_stats')
fiidii=report('fii_dii')
index_api_data=report('index_api_data')
mutual_fund_nav=report('mutual_fund_nav')



#CREATION OF PDF AND SAVING THE PDF  IN LOCAL SYSTEM

def pdf_creation():
    rows=bhavcopy+bulk+block+derivative+pe+fiiderivatives+mutual_fund_nav
    total=[]
    for i,j in enumerate(rows,start=1):
        total.append([i]+j)





    headers=["SRNO","TABLENAME","TOTALROWS","START_DATE","END_DATE","LAST_UPDATE","REPORT_DATE","LOCALORVPS"]
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
    title = Paragraph(f"Daily Database Report-{date_title}", styles['Title'])


    table = Table(data,colWidths=[40, 120, 80, 80, 80, 120, 100, 80])

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
    # sender_email = os.getenv("EMAIL_SECONDARY")
    # app_password = os.getenv("APP_PASSWORD_SECONDARY")
    sender_email="s422yashrajshilwant@gmail.com"
    app_password="rcyx jqxr dxtv wota"
    receiver_email = "yashrajshilwant@gmail.com"

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




