
import requests
import re
from datetime import datetime, timedelta, date
from SQL.Connectingmysql import cursor, mydb
from Mutual_fund.mutual_lastupdated import last_date_record

AMFI_URL = "https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt={date}"

# ================================
# 📅 USER INPUT (Corrected)
# ================================
# Keep these as date objects! Python cannot add days to a string.
start_date = last_date_record
end_date = date.today()

# ================================
# 📥 FETCH DATA
# ================================
def fetch_data(date_str):
    url = AMFI_URL.format(date=date_str)
    # Using headers to prevent AMFI from blocking the automated request
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text.split("\n")

# ================================
# 🧠 PARSE DATA
# ================================
def parse_data(lines):
    data = []
    current_amc = None
    ended_type = None
    investment_type = None
    fund_type = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 🎯 CATEGORY
        if "Schemes" in line:
            ended_type = line.split("(")[0].strip()
            match = re.search(r"\((.*?)\)", line)
            if match:
                category_text = match.group(1).strip()
                parts = [x.strip() for x in category_text.split(" - ")]
                if len(parts) == 1:
                    investment_type = parts[0]
                    fund_type = None
                else:
                    investment_type = parts[0]
                    fund_type = parts[1]
            continue

        # 🎯 DATA ROW
        if re.match(r"^\d+", line):
            parts = line.split(";")
            if len(parts) >= 8:
                try:
                    # Convert '13-Apr-2026' back to a date object for SQL
                    nav_date = datetime.strptime(parts[7], "%d-%b-%Y").date()
                except:
                    continue

                data.append((
                    int(parts[0]),                        # scheme_code
                    parts[1],                             # scheme_name
                    parts[2] if parts[2] else None,       # isin_div_payout
                    parts[3] if parts[3] else None,       # isin_growth
                    float(parts[4]) if parts[4] and parts[4] != 'N.A.' else None,
                    float(parts[5]) if parts[5] and parts[5] != 'N.A.' else None,
                    float(parts[6]) if parts[6] and parts[6] != 'N.A.' else None,
                    nav_date,
                    current_amc,
                    ended_type.replace("Schemes", "").strip() if ended_type else None,
                    investment_type,
                    fund_type
                ))
            continue

        # 🎯 AMC NAME
        if ";" not in line and not re.match(r"^\d+", line):
            current_amc = line.strip()

    return data

# ================================
# 🗄️ DB INSERT
# ================================
def insert_to_db(connection, data):
    if not data:
        return 0

    query = """
    INSERT INTO mutual_fund_nav (
        scheme_code, scheme_name,
        isin_div_payout, isin_growth,
        net_asset_value, repurchase_price, sale_price,
        nav_date,
        amc_name,
        ended_type, investment_type, fund_type
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        scheme_name = VALUES(scheme_name),
        net_asset_value = VALUES(net_asset_value),
        nav_date = VALUES(nav_date);
    """

    cursor.executemany(query, data)
    connection.commit()
    return cursor.rowcount

# ================================
# 🔁 MAIN PIPELINE LOOP
# ================================
def run_pipeline():
    conn = mydb
    current_date = start_date

    while current_date <= end_date:
        # Convert the object to string here for the API request
        date_str_api = current_date.strftime("%d-%b-%Y")
        print(f"📅 Processing: {date_str_api}")

        try:
            lines = fetch_data(date_str_api)
            parsed_data = parse_data(lines)

            if parsed_data:
                count = insert_to_db(conn, parsed_data)
                print(f"✅ Processed {len(parsed_data)} schemes.")
            else:
                print(f"⚠️ No data found for {date_str_api} (Market might be closed).")

        except Exception as e:
            print(f"❌ Error for {date_str_api}: {e}")

        # Move to the next day
        current_date += timedelta(days=1)


    print("🎯 BULK DOWNLOAD COMPLETE!")

run_pipeline()