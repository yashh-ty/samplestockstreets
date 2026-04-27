from tabulate import tabulate
from Bhavcopy_downloader.bhavcopy_report import bhavcopy_report_data
from Bulk_d_Processor.bulk_report import bulk_report_data
from Block_d_Processor.block_report import block_report_data
from Derivatives.derivatives_report import derivatives_report_data
from FII.fii_report import fii_report
from Index_api_data import index_api_report
from Mutual_fund.mutual_report import mutual_report_data
from PE_d_Processor.pe_report import pe_report_data

total=bhavcopy_report_data+bulk_report_data+block_report_data+derivatives_report_data+fii_report_data+index_api_report+mutual_report_data+pe_report_data
headers=["TABLENAME", "ROWS_INSERTED","START_DATE","END_DATE","LAST_UPDATE","DBORVPS"]
print(tabulate(total,headers=headers,tablefmt="grid"))


