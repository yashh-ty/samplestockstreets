import requests
import pandas as pd
import io
from datetime import datetime, timedelta
from SQL.Connectingmysql import cursor, mydb

# -------- CONFIGURATION --------
START_DATE = "20-03-2026"
END_DATE = "30-03-2026"


def get_date_list(start, end):
    s = datetime.strptime(start, "%d-%m-%Y")
    e = datetime.strptime(end, "%d-%m-%Y")
    # FII URLs need "15-Apr-2026" format
    return [(s + timedelta(days=x)) for x in range((e - s).days + 1)]


def clean_fii_df(content, current_date):
    """Cleans the messy Excel structure into a clean DataFrame"""
    # engine='xlrd' is required for .xls files
    df = pd.read_excel(io.BytesIO(content), engine='xlrd', skiprows=2)

    # Define clean column names
    col_names = [
        "particulars", "buy_contracts", "buy_value_cr",
        "sell_contracts", "sell_value_cr", "oi_contracts", "oi_value_cr"
    ]

    # Remove the second header row and rename
    df = df[df.iloc[:, 0] != "No. of contracts"]
    df.columns = col_names

    # Cut off everything from "Notes:" onwards
    mask = df['particulars'].str.contains("Notes:", na=False)
    if mask.any():
        df = df.iloc[:df[mask].index[0]]

    # Drop empty rows and strip text
    df = df.dropna(subset=["particulars"])
    df['particulars'] = df['particulars'].str.strip()

    # Add the date column (requested)
    df['report_date'] = current_date.strftime("%Y-%m-%d")

    return df


def insert_fii_to_mysql(df):
    try:
        sql = """INSERT INTO fii_derivatives_stats
                 (Indices, buy_contracts, buy_value_cr, sell_contracts,
                  sell_value_cr, oi_contracts, oi_value_cr, report_date)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

        # Convert all numbers to standard Python types to avoid MySQL errors
        records = [tuple(x) for x in df.values]

        cursor.executemany(sql, records)
        mydb.commit()
        print(f"✅ Inserted {len(records)} rows.")
    except Exception as e:
        mydb.rollback()
        print(f"❌ DB Error: {e}")


def run_fii_pipeline():
    dates = get_date_list(START_DATE, END_DATE)
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.nseindia.com/"}
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)

    for dt in dates:
        # URL format: fii_stats_15-Apr-2026.xls
        date_str = dt.strftime("%d-%b-%Y")
        url = f"https://nsearchives.nseindia.com/content/fo/fii_stats_{date_str}.xls"

        print(f"🔄 Fetching FII Stats for {date_str}...", end=" ")

        response = session.get(url, headers=headers)
        if response.status_code != 200:
            print("⏭️ Skipped (Holiday/No File)")
            continue

        try:
            df_cleaned = clean_fii_df(response.content, dt)
            insert_fii_to_mysql(df_cleaned)
        except Exception as e:
            print(f"❌ Failed to process: {e}")


run_fii_pipeline()
cursor.close()
mydb.close()
print("\n🚀 FII Pipeline Complete!")