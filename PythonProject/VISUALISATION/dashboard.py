from sqlalchemy import create_engine, text
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os

# --- STEP 1: DB ENGINE ---
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

    # --- STEP 2: TIME RANGE ---
    one_year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

    # --- STEP 3: QUERY ---
    query = text("""
        SELECT T_DATE, CLOSE_PRICE
        FROM bhavcopy
        WHERE SYMBOL = :symbol
        AND T_DATE >= :date
        ORDER BY T_DATE ASC
    """)

    # --- STEP 4: LOAD DATA ---
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={
            "symbol": symbol,
            "date": one_year_ago
        })

    if df.empty:
        print(f"No data found for {symbol}")
        return

    # --- STEP 5: CLEAN DATA ---
    df['T_DATE'] = pd.to_datetime(df['T_DATE'], errors='coerce')
    df = df.dropna(subset=['T_DATE'])
    df.set_index('T_DATE', inplace=True)
    df = df.sort_index()

    # --- STEP 6: MONTHLY DATA ---
    df_monthly = df.resample('ME').last()
    df_monthly['CLOSE_PRICE'] = df_monthly['CLOSE_PRICE'].ffill()

    # --- STEP 7: MOVING AVERAGES ---
    df['MA50'] = df['CLOSE_PRICE'].rolling(50).mean()
    df['MA200'] = df['CLOSE_PRICE'].rolling(200).mean()

    # --- STEP 8: MONTHLY RETURNS ---
    df_monthly['RETURNS'] = df_monthly['CLOSE_PRICE'].pct_change() * 100

    # --- STEP 9: RSI ---
    delta = df['CLOSE_PRICE'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # --- STEP 10: CREATE DASHBOARD ---
    fig, axs = plt.subplots(2, 2, figsize=(14, 8))

    # 📊 1. Monthly Trend
    axs[0, 0].plot(df_monthly.index, df_monthly['CLOSE_PRICE'], linewidth=2)
    axs[0, 0].set_title("Monthly Trend")
    axs[0, 0].grid(True, linestyle=':', alpha=0.5)

    # 📈 2. Moving Averages
    axs[0, 1].plot(df.index, df['CLOSE_PRICE'], label='Price')
    axs[0, 1].plot(df.index, df['MA50'], linestyle='--', label='MA50')
    axs[0, 1].plot(df.index, df['MA200'], linestyle='--', label='MA200')
    axs[0, 1].set_title("Moving Averages")
    axs[0, 1].legend()
    axs[0, 1].grid(True, linestyle=':', alpha=0.5)

    # 📉 3. Monthly Returns
    colors = ['green' if x >= 0 else 'red' for x in df_monthly['RETURNS']]

    axs[1, 0].bar(df_monthly.index, df_monthly['RETURNS'], color=colors, width=20)

    # Zero line
    axs[1, 0].axhline(0, linestyle='--')

    # Labels
    for i, v in enumerate(df_monthly['RETURNS']):
        axs[1, 0].text(df_monthly.index[i], v,
                       f"{v:.1f}%",
                       ha='center',
                       va='bottom' if v >= 0 else 'top',
                       fontsize=8)

    # Stats
    max_ret = df_monthly['RETURNS'].max()
    min_ret = df_monthly['RETURNS'].min()
    avg_ret = df_monthly['RETURNS'].mean()

    axs[1, 0].axhline(avg_ret, linestyle=':', label='Avg')

    axs[1, 0].set_title(
        f"Monthly Returns (%) | Best: {max_ret:.1f}% | Worst: {min_ret:.1f}%"
    )

    axs[1, 0].legend()
    axs[1, 0].grid(True, axis='y', linestyle=':', alpha=0.5)

    # 📊 4. RSI
    axs[1, 1].plot(df.index, df['RSI'], color='orange')
    axs[1, 1].axhline(70, linestyle='--', color='red')
    axs[1, 1].axhline(30, linestyle='--', color='green')
    axs[1, 1].set_title("RSI Indicator")
    axs[1, 1].grid(True, linestyle=':', alpha=0.5)

    # --- FORMAT X-AXIS FOR ALL ---
    for ax in axs.flat:
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        for label in ax.get_xticklabels():
            label.set_rotation(45)

    plt.tight_layout()

    # --- STEP 11: SAVE ---
    folder = "C:/Users/ADMIN/OneDrive/Desktop/VISUALISATION"
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, f"{symbol}_dashboard.png")

    plt.savefig(file_path, dpi=150)
    plt.close()

    return file_path
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def create_pdf(image_path, symbol):
    pdf_path = f"C:/Users/ADMIN/OneDrive/Desktop/VISUALISATION/{symbol}_report.pdf"

    doc = SimpleDocTemplate(pdf_path)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph(f"Stock Performance Report - {symbol}", styles['Title']))
    elements.append(Spacer(1, 12))

    # Insert full dashboard image
    elements.append(Image(image_path, width=500, height=300))

    doc.build(elements)


    return pdf_path




# --- EXECUTION ---
search_stock = "TCS"

image_generated = generate_stock_dashboard(search_stock)
pdf_generated = create_pdf(image_generated, search_stock)
if image_generated:
    pdf_generated = create_pdf(image_generated, search_stock)
    if os.path.exists(image_generated):
        os.remove(image_generated)
print(f"PDF: {pdf_generated}")
