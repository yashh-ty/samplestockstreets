import requests
import csv
from datetime import datetime, timedelta
from io import StringIO
from PE_d_Processor.pe_d_lastupdated import last_date_record
from SQL.Connectingmysql import mydb, cursor

start_date = last_date_record # convert to string
end_date = datetime.today().date()

# ==============================
# 🌐 FETCH + INSERT FUNCTION
# ==============================
def fetch_and_insert_pe(date):
    date_str = date.strftime("%d%m%y")
    url = f"https://nsearchives.nseindia.com/content/equities/peDetail/PE_{date_str}.csv"

    # ✅ Create session (important for NSE)
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/csv",
        "Referer": "https://www.nseindia.com/"
    }

    try:
        # ✅ Step 1: Get NSE cookies
        session.get("https://www.nseindia.com", headers=headers)

        # ✅ Step 2: Fetch CSV
        response = session.get(url, headers=headers, timeout=10)

        print(f"\n📅 Processing: {date.strftime('%d-%m-%Y')}")
        print("Status:", response.status_code)

        # ❌ If blocked or invalid
        if response.status_code != 200 or "SYMBOL" not in response.text:
            print("❌ Invalid / Blocked response")
            print(response.text[:200])  # debug preview
            return 0

        # ==============================
        # 📊 PARSE CSV
        # ==============================
        csv_file = StringIO(response.text)
        csv_data = csv.reader(csv_file)

        header = next(csv_data)
        print("Header:", header)

        insert_query = '''
            INSERT INTO stock_streets.PE
            (SYMBOL, SYMBOL_PE, ADJUSTED_PE, T_DATE)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                SYMBOL_PE = VALUES(SYMBOL_PE),
                ADJUSTED_PE = VALUES(ADJUSTED_PE),
                T_DATE = VALUES(T_DATE);
        '''

        data_to_insert = []

        for row in csv_data:
            if len(row) < 3:
                continue

            if not row or row[0].strip() == "":
                continue

            # ✅ CLEAN VALUES
            def clean_value(val):
                val = val.strip()
                if val in ("", "NA", "-", "N/A"):
                    return None
                return float(val)

            try:
                symbol_pe = clean_value(row[1])
                adjusted_pe = clean_value(row[2])
            except:
                continue  # skip bad rows

            formatted_date = date.strftime("%Y-%m-%d")

            data_to_insert.append((
                row[0].strip(),  # SYMBOL
                symbol_pe,
                adjusted_pe,
                formatted_date
            ))
        print("Rows prepared:", len(data_to_insert))

        # ==============================
        # 🚀 BULK INSERT
        # ==============================
        if data_to_insert:
            cursor.executemany(insert_query, data_to_insert)

        return len(data_to_insert)

    except Exception as e:
        print(f"⚠️ Error on {date.strftime('%d-%m-%Y')}: {e}")
        return 0


# ==============================
# 🔁 LOOP THROUGH DATE RANGE
# ==============================
total_rows = 0
current_date = start_date

while current_date <= end_date:
    rows = fetch_and_insert_pe(current_date)
    total_rows += rows
    current_date += timedelta(days=1)


# ==============================
# 💾 COMMIT & CLOSE
# ==============================
try:
    mydb.commit()
    print("\n✅ Changes committed to DB")
except Exception as e:
    print(f"\n❌ Commit error: {e}")


print(f"\n🎯 Total rows inserted: {total_rows}")
