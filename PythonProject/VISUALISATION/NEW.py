# from sqlalchemy import create_engine, text
# import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# from datetime import datetime, timedelta
# import os
# from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet
#
#
# # --- DB ENGINE ---
# def get_engine():
#     return create_engine(
#         "mysql+pymysql://root:Shankar%40123@127.0.0.1/stock_streets",
#         pool_size=10,
#         max_overflow=20,
#         pool_recycle=1800,
#         echo=False
#     )
#
#
# def generate_stock_dashboard(symbol):
#     engine = get_engine()
#
#     one_year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
#
#     query = text("""
#         SELECT T_DATE, CLOSE_PRICE
#         FROM bhavcopy
#         WHERE SYMBOL = :symbol
#         AND T_DATE >= :date
#         ORDER BY T_DATE ASC
#     """)
#
#     with engine.connect() as conn:
#         df = pd.read_sql(query, conn, params={
#             "symbol": symbol,
#             "date": one_year_ago
#         })
#
#     if df.empty:
#         print(f"No data found for {symbol}")
#         return None
#
#     # --- CLEAN ---
#     df['T_DATE'] = pd.to_datetime(df['T_DATE'], errors='coerce')
#     df = df.dropna(subset=['T_DATE'])
#     df.set_index('T_DATE', inplace=True)
#     df = df.sort_index()
#
#     # --- MONTHLY ---
#     df_monthly = df.resample('ME').last()
#     df_monthly['CLOSE_PRICE'] = df_monthly['CLOSE_PRICE'].ffill()
#
#     # --- MOVING AVG ---
#     df['MA50'] = df['CLOSE_PRICE'].rolling(50).mean()
#     df['MA200'] = df['CLOSE_PRICE'].rolling(200).mean()
#
#     # --- RETURNS ---
#     df_monthly['RETURNS'] = df_monthly['CLOSE_PRICE'].pct_change() * 100
#
#     # --- RSI ---
#     delta = df['CLOSE_PRICE'].diff()
#     gain = delta.clip(lower=0)
#     loss = -delta.clip(upper=0)
#
#     avg_gain = gain.rolling(14).mean()
#     avg_loss = loss.rolling(14).mean()
#
#     rs = avg_gain / avg_loss
#     df['RSI'] = 100 - (100 / (1 + rs))
#
#     # --- CUMULATIVE RETURNS ---
#     df['DAILY_RET'] = df['CLOSE_PRICE'].pct_change()
#     df['CUM_RET'] = (1 + df['DAILY_RET']).cumprod()
#
#     # --- HEATMAP DATA ---
#     heatmap_data = df_monthly.copy()
#     heatmap_data['Year'] = heatmap_data.index.year
#     heatmap_data['Month'] = heatmap_data.index.strftime('%b')
#
#     heatmap_pivot = heatmap_data.pivot(index='Year', columns='Month', values='RETURNS')
#
#     month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
#     heatmap_pivot = heatmap_pivot.reindex(columns=month_order)
#
#     # --- CREATE DASHBOARD (3x2) ---
#     fig, axs = plt.subplots(3, 2, figsize=(16, 12))
#
#     # 1️⃣ Monthly Trend
#     axs[0, 0].plot(df_monthly.index, df_monthly['CLOSE_PRICE'])
#     axs[0, 0].set_title("Monthly Trend")
#
#     # 2️⃣ Moving Avg
#     axs[0, 1].plot(df.index, df['CLOSE_PRICE'], label='Price')
#     axs[0, 1].plot(df.index, df['MA50'], linestyle='--', label='MA50')
#     axs[0, 1].plot(df.index, df['MA200'], linestyle='--', label='MA200')
#     axs[0, 1].legend()
#     axs[0, 1].set_title("Moving Averages")
#
#
#
#     # 5️⃣ Cumulative Returns
#     axs[1, 0].plot(df.index, df['VALUE_RS'])
#     axs[1, 0].set_title(f"Investment Growth (₹{"initial_investment"} → ₹{df['VALUE_RS'].iloc[-1]:.2f})")
#     axs[1, 0].set_ylabel("Value in ₹")
#     last_value = df['VALUE_RS'].iloc[-1]
#
#     axs[1, 0].text(df.index[-1], last_value,
#                    f"₹{last_value:.2f}",
#                    fontsize=10,
#                    ha='right')
#
#     # 6️⃣ Heatmap
#     im = axs[1, 1].imshow(heatmap_pivot, aspect='auto')
#     axs[1, 1].set_title("Monthly Returns Heatmap")
#
#     axs[1, 1].set_xticks(range(len(heatmap_pivot.columns)))
#     axs[1, 1].set_xticklabels(heatmap_pivot.columns)
#
#     axs[1, 1].set_yticks(range(len(heatmap_pivot.index)))
#     axs[1, 1].set_yticklabels(heatmap_pivot.index)
#
#     for i in range(len(heatmap_pivot.index)):
#         for j in range(len(heatmap_pivot.columns)):
#             val = heatmap_pivot.iloc[i, j]
#             if not pd.isna(val):
#                 axs[1, 1].text(j, i, f"{val:.1f}", ha='center', va='center', fontsize=7)
#
#     fig.colorbar(im, ax=axs[2, 1])
#
#     # --- FORMAT ---
#     for ax in axs.flat:
#         ax.grid(True, linestyle=':', alpha=0.5)
#         if ax != axs[1, 1]:  # Skip heatmap
#             ax.xaxis.set_major_locator(mdates.MonthLocator())
#             ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
#             for label in ax.get_xticklabels():
#                 label.set_rotation(45)
#
#     plt.tight_layout()
#
#     # --- SAVE IMAGE ---
#     folder = "C:/Users/ADMIN/OneDrive/Desktop/VISUALISATION"
#     os.makedirs(folder, exist_ok=True)
#
#     file_path = os.path.join(folder, f"{symbol}_dashboard.png")
#     plt.savefig(file_path, dpi=150)
#     plt.close()
#
#     return file_path
#
#
# def create_pdf(image_path, symbol):
#     if image_path is None:
#         return None
#
#     pdf_path = f"C:/Users/ADMIN/OneDrive/Desktop/VISUALISATION/{symbol}_report.pdf"
#
#     doc = SimpleDocTemplate(pdf_path)
#     styles = getSampleStyleSheet()
#
#     elements = []
#     elements.append(Paragraph(f"Stock Performance Report - {symbol}", styles['Title']))
#     elements.append(Spacer(1, 12))
#     elements.append(Image(image_path, width=500, height=350))
#
#     doc.build(elements)
#
#     return pdf_path
#
#
# # --- EXECUTION ---
# search_stock = "TCS"
#
# image_generated = generate_stock_dashboard(search_stock)
#
# if image_generated:
#     pdf_generated = create_pdf(image_generated, search_stock)
#
#     if os.path.exists(image_generated):
#         os.remove(image_generated)
#
#     print(f"PDF created: {pdf_generated}")
# else:
#     print("Dashboard generation failed.")
from sqlalchemy import create_engine, text
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# --- DB ENGINE ---
def get_engine():
    return create_engine(
        "mysql+pymysql://root:Shankar%40123@127.0.0.1/stock_streets",
        pool_size=10,
        max_overflow=20,
        pool_recycle=1800,
        echo=False
    )


def generate_stock_dashboard(symbol):
    engine = get_engine()

    one_year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

    query = text("""
        SELECT T_DATE, CLOSE_PRICE
        FROM bhavcopy
        WHERE SYMBOL = :symbol
        AND T_DATE >= :date
        ORDER BY T_DATE ASC
    """)

    # --- LOAD DATA ---
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={
            "symbol": symbol,
            "date": one_year_ago
        })

    if df.empty:
        print(f"No data found for {symbol}")
        return None

    # --- CLEAN ---
    df['T_DATE'] = pd.to_datetime(df['T_DATE'], errors='coerce')
    df = df.dropna(subset=['T_DATE'])
    df.set_index('T_DATE', inplace=True)
    df = df.sort_index()

    # --- MONTHLY DATA ---
    df_monthly = df.resample('ME').last()
    df_monthly['CLOSE_PRICE'] = df_monthly['CLOSE_PRICE'].ffill()

    # --- MOVING AVERAGES ---
    df['MA50'] = df['CLOSE_PRICE'].rolling(50).mean()
    df['MA200'] = df['CLOSE_PRICE'].rolling(200).mean()

    # --- MONTHLY RETURNS ---
    df_monthly['RETURNS'] = df_monthly['CLOSE_PRICE'].pct_change() * 100

    # --- RSI ---
    delta = df['CLOSE_PRICE'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # --- CUMULATIVE RETURNS (₹ BASED) ---
    df['DAILY_RET'] = df['CLOSE_PRICE'].pct_change()
    df['CUM_RET'] = (1 + df['DAILY_RET']).cumprod()

    initial_investment = 100  # change as needed
    df['VALUE_RS'] = df['CUM_RET'] * initial_investment

    # --- HEATMAP DATA ---
    heatmap_data = df_monthly.copy()
    heatmap_data['Year'] = heatmap_data.index.year
    heatmap_data['Month'] = heatmap_data.index.strftime('%b')

    heatmap_pivot = heatmap_data.pivot(index='Year', columns='Month', values='RETURNS')

    month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    heatmap_pivot = heatmap_pivot.reindex(columns=month_order)

    # --- CREATE DASHBOARD (2x2 CLEAN LAYOUT) ---
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))

    # 1️⃣ Monthly Trend
    axs[0, 0].plot(df_monthly.index, df_monthly['CLOSE_PRICE'])
    axs[0, 0].set_title("Monthly Trend")

    # 2️⃣ Moving Averages
    axs[0, 1].plot(df.index, df['CLOSE_PRICE'], label='Price')
    axs[0, 1].plot(df.index, df['MA50'], linestyle='--', label='MA50')
    axs[0, 1].plot(df.index, df['MA200'], linestyle='--', label='MA200')
    axs[0, 1].legend()
    axs[0, 1].set_title("Moving Averages")

    # 3️⃣ Investment Growth (₹)
    axs[1, 0].plot(df.index, df['VALUE_RS'])

    last_value = df['VALUE_RS'].iloc[-1]

    axs[1, 0].set_title(
        f"Investment Growth (₹{initial_investment} → ₹{last_value:.2f})"
    )
    axs[1, 0].set_ylabel("Value in ₹")

    # Annotate last value
    axs[1, 0].text(df.index[-1], last_value,
                   f"₹{last_value:.2f}",
                   fontsize=10,
                   ha='right')

    # 4️⃣ Heatmap
    im = axs[1, 1].imshow(heatmap_pivot, aspect='auto')
    axs[1, 1].set_title("Monthly Returns Heatmap")

    axs[1, 1].set_xticks(range(len(heatmap_pivot.columns)))
    axs[1, 1].set_xticklabels(heatmap_pivot.columns)

    axs[1, 1].set_yticks(range(len(heatmap_pivot.index)))
    axs[1, 1].set_yticklabels(heatmap_pivot.index)

    for i in range(len(heatmap_pivot.index)):
        for j in range(len(heatmap_pivot.columns)):
            val = heatmap_pivot.iloc[i, j]
            if not pd.isna(val):
                axs[1, 1].text(j, i, f"{val:.1f}", ha='center', va='center', fontsize=7)

    fig.colorbar(im, ax=axs[1, 1])

    # --- FORMAT ---
    for ax in axs.flat:
        ax.grid(True, linestyle=':', alpha=0.5)

        if ax != axs[1, 1]:  # skip heatmap
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

            for label in ax.get_xticklabels():
                label.set_rotation(45)

    plt.tight_layout()

    # --- SAVE IMAGE ---
    folder = "C:/Users/ADMIN/OneDrive/Desktop/VISUALISATION"
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, f"{symbol}_dashboard.png")
    plt.savefig(file_path, dpi=150)
    plt.close()

    return file_path


def create_pdf(image_path, symbol):
    if image_path is None:
        return None

    pdf_path = f"C:/Users/ADMIN/OneDrive/Desktop/VISUALISATION/{symbol}_report.pdf"

    doc = SimpleDocTemplate(pdf_path)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph(f"Stock Performance Report - {symbol}", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Image(image_path, width=500, height=350))

    doc.build(elements)

    return pdf_path


# --- EXECUTION ---
search_stock = "TCS"

image_generated = generate_stock_dashboard(search_stock)

if image_generated:
    pdf_generated = create_pdf(image_generated, search_stock)

    if os.path.exists(image_generated):
        os.remove(image_generated)

    print(f"✅ PDF created: {pdf_generated}")
else:
    print("❌ Dashboard generation failed.")
