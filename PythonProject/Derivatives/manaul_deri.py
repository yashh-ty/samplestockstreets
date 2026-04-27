
import requests
import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
from SQL.Connectingmysql import cursor, mydb
import io

# -------- CONFIGURATION --------
START_DATE = "20-03-2026"
END_DATE = "30-03-2026"


# -------- PIPELINE FUNCTIONS --------

def get_date_range(start, end):
    s = datetime.strptime(start, "%d-%m-%Y")
    e = datetime.strptime(end, "%d-%m-%Y")
    # Returns a list of datetime objects for easier manipulation
    return [s + timedelta(days=x) for x in range((e - s).days + 1)]


def insert_to_mysql(df):
    try:
        # Prepare the SQL query
        sql = """INSERT INTO stock_streets.derivative_bhavcopy
                 (script, instrument, symbol, expiry_dt, strike_pr, option_typ,
                  price_open, price_high, price_low, price_close, settle_pr,
                  contracts, val_inlakh, open_int, chg_in_oi, T_DATE)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        # Convert DataFrame to list of tuples for bulk insertion
        records = [tuple(x) for x in df.values]

        cursor.executemany(sql, records)
        # It's better to commit here so data is saved per day
        mydb.commit()
        print(f"✅ Successfully inserted {len(records)} rows.")

    except Error as e:
        print(f"❌ Database Error: {e}")
        mydb.rollback()


def run_pipeline():
    date_objects = get_date_range(START_DATE, END_DATE)
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.nseindia.com/all-reports"
    }

    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)

    for dt in date_objects:
        # Format for URL: 13042026
        d_str = dt.strftime("%d%m%Y")
        # Format for MySQL: 2026-04-13
        db_date = dt.strftime("%Y-%m-%d")

        url = f"https://nsearchives.nseindia.com/content/trdops/FNO_BC{d_str}.DAT"
        print(f"🔄 Fetching {d_str}...", end=" ")

        try:
            response = session.get(url, headers=headers)
            if response.status_code != 200:
                print("⏭️ Skipped (Holiday/No File)")
                continue

            # Load into DataFrame
            df = pd.read_csv(io.BytesIO(response.content), header=None, engine='python')

            # Select original columns (Indices 0 to 21)
            df_final = df[[0, 1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 15, 16, 17, 18]].copy()

            # Data Cleaning: Strip spaces
            for col in df_final.columns:
                if df_final[col].dtype == 'object':
                    df_final[col] = df_final[col].str.strip()

            # --- ADDING THE T_DATE COLUMN ---
            # This adds db_date to every row in the dataframe
            df_final['T_DATE'] = db_date

            # Push to MySQL
            insert_to_mysql(df_final)

        except Exception as e:
            print(f"❌ Processing Failed: {e}")


# -------- EXECUTION --------
run_pipeline()
cursor.close()
mydb.close()
print("\n🚀 Pipeline completed.")