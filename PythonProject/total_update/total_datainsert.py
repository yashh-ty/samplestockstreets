
from SQL.Connectingmysql import cursor, mydb
import time

from Bhavcopy_downloader import full_process_bhavcopy
time.sleep(3)

from Block_d_Processor import auto_block_d_upload
time.sleep(3)

from Bulk_d_Processor import auto_bulk_d_upload
time.sleep(3)

from Index_api_data import auto_index_api_upload
time.sleep(3)

from PE_d_Processor import auto_pe_d_upload
time.sleep(3)

from Mutual_fund import auto_mf


cursor.close()
mydb.close()


print("All processes complete. Connection closed.")