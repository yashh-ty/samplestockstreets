



# -----------
import requests
import pandas as pd
from datetime import datetime, timedelta
from io import StringIO
from SQL.Connectingmysql import mydb
from Index_api_data.index_api_lastupdated import last_date_record

# ---------------- NSE DOWNLOAD ----------------
def download_index_bhavcopy(session, date):
    date_str = date.strftime("%d%m%Y")
    url = f"https://nsearchives.nseindia.com/content/indices/ind_close_all_{date_str}.csv"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/csv",
        "Referer": "https://www.nseindia.com/"
    }

    response = session.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ No data for {date_str}")
        return None

    df = pd.read_csv(StringIO(response.text))
    df["DATE"] = date.strftime("%Y-%m-%d")

    return df


# ---------------- CLEAN DATA ----------------
def clean_dataframe(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[()%/.]", "", regex=True)
    )

    df = df.rename(columns={
        "index_name": "index_name",
        "index_date": "index_date",
        "open_index_value": "open",
        "high_index_value": "high",
        "low_index_value": "low",
        "closing_index_value": "close",
        "points_change": "change_points",
        "change": "change_percent",
        "turnover_rs_cr": "turnover_cr"
    })

    df["index_date"] = pd.to_datetime(df["index_date"], format="%d-%m-%Y")

    numeric_cols = [
        "open", "high", "low", "close",
        "change_points", "change_percent",
        "volume", "turnover_cr",
        "pe", "pb", "div_yield"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Final cleanup of NaN in the dataframe itself
    df = df.where(pd.notnull(df), None)

    return df


# ---------------- INSERT BATCH ----------------
def insert_batch(cursor, data_batch):
    query = """
    INSERT INTO index_api_data (
        index_name, index_date,
        open, high, low, close,
        change_points, change_percent,
        volume, turnover_cr,
        pe, pb, div_yield
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        open = VALUES(open),
        high = VALUES(high),
        low = VALUES(low),
        close = VALUES(close),
        change_points = VALUES(change_points),
        change_percent = VALUES(change_percent),
        volume = VALUES(volume),
        turnover_cr = VALUES(turnover_cr),
        pe = VALUES(pe),
        pb = VALUES(pb),
        div_yield = VALUES(div_yield)
    """
    cursor.executemany(query, data_batch)


# ---------------- MAIN PIPELINE ----------------
def run_pipeline(from_date, to_date, batch_size=500):

    cursor = mydb.cursor()

    session = requests.Session()
    session.get("https://www.nseindia.com", headers={"User-Agent": "Mozilla/5.0"})

    current = from_date
    batch = []

    while current <= to_date:

        # Skip weekends
        if current.weekday() >= 5:
            current += timedelta(days=1)
            continue

        # print(f"📅 Processing {current}")

        df = download_index_bhavcopy(session, current)

        if df is not None:
            df = clean_dataframe(df)

            for _, row in df.iterrows():
                # FIX: Ensure nan is converted to None specifically during tuple creation
                # This prevents the 'nan can not be used with MySQL' error
                def fix(val):
                    return None if pd.isna(val) else val

                batch.append((
                    fix(row.get("index_name")),
                    row.get("index_date").date() if pd.notnull(row.get("index_date")) else None,
                    fix(row.get("open")),
                    fix(row.get("high")),
                    fix(row.get("low")),
                    fix(row.get("close")),
                    fix(row.get("change_points")),
                    fix(row.get("change_percent")),
                    fix(row.get("volume")),
                    fix(row.get("turnover_cr")),
                    fix(row.get("pe")),
                    fix(row.get("pb")),
                    fix(row.get("div_yield"))
                ))

        # Batch insert
        if len(batch) >= batch_size:
            insert_batch(cursor, batch)
            mydb.commit()
            # print(f"✅ Inserted batch of {len(batch)}")
            batch.clear()

        current += timedelta(days=1)

    # Final batch
    if batch:
        insert_batch(cursor, batch)
        mydb.commit()
        # print(f"✅ Final batch inserted: {len(batch)}")


    # print("🎉 Data sync complete!")


start_date_input = last_date_record
end_date_input = datetime.today().date()

from_date = start_date_input
to_date = end_date_input

run_pipeline(from_date, to_date)

