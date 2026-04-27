import requests
import csv
from datetime import datetime,date
from io import StringIO
from SQL.Connectingmysql import cursor,mydb
from Block_d_Processor.block_last_updated import last_date_record
from tabulate import tabulate


start_date = last_date_record
end_date   = date.today()

# Validation
if start_date > end_date:
    print("❌ Start date cannot be greater than end date")
    exit()

# Convert for API
start_date_str = last_date_record.strftime("%d-%m-%Y")
end_date_str   = date.today().strftime("%d-%m-%Y")


# ==============================
# 🌐 FETCH DATA
# ==============================
def fetch_bulk_data(start_date, end_date):

    url = f"https://www.nseindia.com/api/historicalOR/bulk-block-short-deals?optionType=block_deals&from={start_date}&to={end_date}&csv=true"

    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.nseindia.com/"
    }

    try:
        # Step 1: Get cookies
        session.get("https://www.nseindia.com", headers=headers)

        # Step 2: Fetch CSV
        response = session.get(url, headers=headers, timeout=15)

        print("\n🌐 Status:", response.status_code)

        if response.status_code != 200 or "Date" not in response.text:
            print("❌ Blocked / Invalid response")
            print(response.text[:200])
            return None

        return response.text

    except Exception as e:
        print("❌ Fetch Error:", e)
        return None


# ==============================
# 📊 PARSE + CLEAN DATA
# ==============================
def parse_bulk_data(csv_text):

    csv_file = csv_file = StringIO(csv_text.lstrip('\ufeff'))
    csv_data = csv.reader(csv_file)

    header = next(csv_data)
    header = [col.strip().replace('"', '') for col in header]

    data_to_insert = []

    for row in csv_data:
        if not row or len(row) < 7:
            continue

        # ✅ Clean all columns
        row = [col.strip().replace('"', '') for col in row]

        try:
            def clean_num(val):
                val = val.replace(',', '').strip()
                if val in ("", "NA", "-", "N/A"):
                    return None
                return float(val)

            trade_date = datetime.strptime(row[0], "%d-%b-%Y").strftime("%Y-%m-%d")

            qty = clean_num(row[5])
            qty = int(qty) if qty is not None else None

            price = clean_num(row[6])

            data_to_insert.append((
                trade_date,
                row[1],
                row[2],
                row[3],
                row[4],
                qty,
                price,
                row[7] if len(row) > 7 else None
            ))

        except Exception as e:
            print("⚠️ Skipping row:", row, e)
            continue

    return data_to_insert


# ==============================
# 🚀 INSERT DATA (BATCH SAFE)
# ==============================
def insert_bulk_data(data):

    insert_query = '''
    INSERT INTO stock_streets.block_deal
    (T_DATE,SYMBOL,SECURITY_NAME,CLIENT_NAME,BUY_SELL,QTY,PRICE,REMARK)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        SYMBOL = VALUES(SYMBOL),
        SECURITY_NAME = VALUES(SECURITY_NAME),
        CLIENT_NAME = VALUES(CLIENT_NAME),
        BUY_SELL = VALUES(BUY_SELL),
        QTY = VALUES(QTY),
        PRICE = VALUES(PRICE),
        REMARK = VALUES(REMARK);
    '''

    batch_size = 500
    total = 0

    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        cursor.executemany(insert_query, batch)
        mydb.commit()
        total += len(batch)

    print("Inserted rows:", total)
    return total


# ==============================
# ▶️ MAIN EXECUTION
# ==============================

total_rows = 0
try:
    csv_text = fetch_bulk_data(start_date_str, end_date_str)

    if csv_text:
        parsed_data = parse_bulk_data(csv_text)

        if parsed_data:
            total_rows = insert_bulk_data(parsed_data)
            print(f"\n🎯 Total rows inserted: {total_rows}")
        else:
            print("⚠️ No data to insert")


except Exception as e:
    print("❌ Unexpected Error:", e)



