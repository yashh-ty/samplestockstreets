

import requests
import os
import datetime
import time
import pandas as pd
import glob
import pathlib
import csv
import shutil  # For moving file
from Bhavcopy_downloader.Holidays2026 import holiday_list
from SQL.Connectingmysql import mydb
from Bhavcopy_downloader.bhavcopy_lastupdated import last_date

# Record the start time
start_time = time.time()
last_date_record=last_date()

# ----------------------To create urls of the bhavcopy files of the selected dates----------------------
def generate_urls(start_date, end_date, skip_dates):
    current_date = start_date
    urls = []

    while current_date <= end_date:
        # We use .date() for skip_dates comparison to stay consistent
        if current_date.weekday() not in [5, 6] and current_date.date() not in skip_dates:
            date_str = current_date.strftime("full_%d%m%Y.csv")
            url = f"https://archives.nseindia.com/products/content/sec_bhavdata_{date_str}"
            urls.append(url)
        current_date += datetime.timedelta(days=1)
    return urls


# ----------------------To download the bhavcopy files of the selected dates----------------------
def download_file(url, download_folder):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            file_name = url.split('/')[-1]
            file_path = os.path.join(download_folder, file_name)
            with open(file_path, 'wb') as file:
                file.write(response.content)
            # print(f"File downloaded: {file_path}")
        else:
            print(f"Failed to download {url}. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"An error occurred while downloading {url}: {e}")


def validate_dates(start_date, end_date):
    # This creates a datetime.datetime object (e.g., 2026-04-14 13:53:00)
    current_date = datetime.datetime.now()

    if end_date < start_date:
        print("Error: The end date cannot be earlier than the start date.")
        return False

    # Comparison happens here between two datetime objects
    if end_date > current_date:
        print(f"Error: The end date cannot be greater than today's date ({current_date.strftime('%d-%m-%Y')}).")
        return False

    return True


# ----------------------Input Modification for Type Consistency----------------------
try:
    if isinstance(last_date_record, datetime.date) and not isinstance(last_date_record, datetime.datetime):
        start_date = datetime.datetime.combine(last_date_record, datetime.time.min)
    else:
        start_date = last_date_record

    # Set end_date to the exact current moment to pass the 'end_date > current_date' check
    end_date = datetime.datetime.now()

    # print(f"Start Date: {start_date}")
    # print(f"End Date: {end_date}")

except ValueError:
    print("Error: Invalid date format.")
    exit()

# Validate the date range
if not validate_dates(start_date, end_date):
    exit()

# Holiday processing
skip_dates_input = holiday_list
skip_dates = set()
if skip_dates_input:
    for date_str in skip_dates_input:
        try:
            date_str = str(date_str).strip()
            # NSE filenames depend on day/month/year, so we store the date portion for logic
            skip_date = datetime.datetime.strptime(date_str, "%d%m%Y")
            skip_dates.add(skip_date.date())
        except ValueError:
            print(f"Invalid date format skipped: {date_str.strip()}")

urls_to_download = generate_urls(start_date, end_date, skip_dates)
download_folder = r"D:\bhavcopy"
os.makedirs(download_folder, exist_ok=True)

for url in urls_to_download:
    download_file(url, download_folder)

# ------------------To format the downloaded bhavcopy files--------------------
input_folder = r'D:\bhavcopy'
file_pattern = os.path.join(input_folder, 'sec_bhavdata_full_*.csv')
csv_files = glob.glob(file_pattern)

if not csv_files:
    print("No files found to process.")
else:
    for file_to_process in csv_files:
        df = pd.read_csv(file_to_process)
        df.columns = ['SYMBOL', 'SERIES', 'DATE1', 'PREV_CLOSE', 'OPEN_PRICE', 'HIGH_PRICE',
                      'LOW_PRICE', 'LAST_PRICE', 'CLOSE_PRICE', 'AVG_PRICE', 'TTL_TRD_QNTY',
                      'TURNOVER_LACS', 'NO_OF_TRADES', 'DELIV_QTY', 'DELIV_PER']

        # Clean spaces
        df = df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))

        columns_to_replace = ['PREV_CLOSE', 'OPEN_PRICE', 'HIGH_PRICE', 'LOW_PRICE',
                              'LAST_PRICE', 'CLOSE_PRICE', 'AVG_PRICE', 'TTL_TRD_QNTY',
                              'TURNOVER_LACS', 'NO_OF_TRADES', 'DELIV_QTY', 'DELIV_PER']
        df[columns_to_replace] = df[columns_to_replace].replace('-', 0)

        # Format date for SQL
        df['DATE1'] = pd.to_datetime(df['DATE1'], format='%d-%b-%Y').dt.strftime('%Y-%m-%d')

        output_folder = r"D:\bhavcopy\formatted"
        os.makedirs(output_folder, exist_ok=True)

        output_file = os.path.join(output_folder, os.path.basename(file_to_process))
        df.to_csv(output_file, index=False)

        # Remove original after formatting
        os.remove(file_to_process)
        # print(f"Formatted and moved: {output_file}")

# ------------------To upload the downloaded bhavcopy files--------------------
cursor = mydb.cursor()
csv_directory = pathlib.Path(r"D:\bhavcopy\formatted")
processed_directory = csv_directory / "processed"
processed_directory.mkdir(parents=True, exist_ok=True)

bhavcopy_files = list(csv_directory.glob("sec_bhavdata_full_*.csv"))
rows_inserted_bhavcopy = 0

for csv_file in bhavcopy_files:
    try:
        with open(csv_file, "r") as csv_path:
            csv_data = csv.reader(csv_path)
            next(csv_data)  # Skip Header

            for rows in csv_data:
                insert_data = '''INSERT INTO stock_streets.bhavcopy (SYMBOL, SERIES, T_DATE, PREV_CLOSE, OPEN_PRICE,
                                                                     HIGH_PRICE, LOW_PRICE, LAST_PRICE, CLOSE_PRICE,
                                                                     AVG_PRICE, TTL_TRD_QNTY, TURNOVER_LACS, \
                                                                     NO_OF_TRADES, DELIV_QTY, DELIV_PER)
                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                val = (rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7],
                       rows[8], rows[9], rows[10], rows[11], rows[12], rows[13], rows[14])
                cursor.execute(insert_data, val)
                rows_inserted_bhavcopy += 1

        shutil.move(str(csv_file), processed_directory / csv_file.name)
    except Exception as e:
        print(f"Error processing database upload for {csv_file.name}: {e}")

try:
    mydb.commit()
    # print("Changes committed to the database.")
except Exception as e:
    print(f"Error during SQL commit: {e}")


end_time = time.time()







