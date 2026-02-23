streamlit as st

import requests

import yfinance as yf

import time

from datetime import datetime



# 1. 페이지 설정 및 다크모드 스타일

st.set_page_config(page_title="Market Monitor", layout="centered")



st.markdown("""

    <style>

    .main { background-color: #121212; }

    div[data-testid="stMetricValue"] { color: #F0B90B !important; font-size: 26px !important; font-weight: bold; }

    div[data-testid="stMetricLabel"] { color: #848E9C !important; font-size: 14px !important; }

    .stApp { background-color: #121212; }

    /* 나스닥 텍스트 커스텀 스타일 */

    .nasdaq-container { margin-top: 10px; text-align: left; }

    .nasdaq-label { color: #848E9C; font-size: 14px; font-weight: bold; margin-bottom: 2px; }

    .nasdaq-value { font-size: 24px; font-weight: bold; margin-bottom: 15px; }

    .up { color: #0ECB81; } .down { color: #F6465D; }

    </style>

    """, unsafe_allow_html=True)



st.title("🚀 Market Monitor")



# 2. 데이터 호출 함수

def get_nasdaq_info(ticker_symbol):

    try:

        tk = yf.Ticker(ticker_symbol)

        # 실시간 가격 및 전일 종가 가져오기

        fast = tk.fast_info

        current_price = fast['last_price']

        prev_close = fast['previous_close']

        

        change = current_price - prev_close

        change_pct = (change / prev_close) * 100

        

        color_class = "up" if change >= 0 else "down"

        arrow = "▲" if change >= 0 else "▼"

        

        return f'<div class="nasdaq-value {color_class}">{current_price:,.2f} ({change:+,.2f} {change_pct:+.2f}% {arrow})</div>'

    except:

        return '<div class="nasdaq-value" style="color:white;">Data N/A</div>'



def fetch_market_data():

    results = {"upbit": 0.0, "binance": 0.0, "premium": 0.0, "update": datetime.now().strftime('%H:%M:%S')}

    try:

        # 코인 데이터

        u_res = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-BTC", timeout=5).json()

        results["upbit"] = float(u_res[0]['trade_price'])

        b_res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5).json()

        results["binance"] = float(b_res['price'])

        results["premium"] = ((results["upbit"] / (results["binance"] * 1400.0)) - 1) * 100

    except:

        pass

    return results



# 3. 화면 UI 렌더링

data = fetch_market_data()



col1, col2 = st.columns(2)

with col1:

    st.metric("UPBIT BTC", f"{data['upbit']:,.0f} KRW")

    st.metric("K-PREMIUM", f"{data['premium']:+.2f} %")

with col2:

    st.metric("BINANCE BTC", f"$ {data['binance']:,.2f}")

    st.metric("EXCHANGE RATE", "1,400.00")



st.divider()

st.subheader("📊 NASDAQ Realtime (YF)")



# 나스닥 상세 지수 표시 (HTML 커스텀 디자인)

nq_html = get_nasdaq_info("NQ=F")

cp_html = get_nasdaq_info("^IXIC")



st.markdown(f"""

    <div class="nasdaq-container">

        <div class="nasdaq-label">NASDAQ 100 FUTURES (YF)</div>

        {nq_html}

        <div class="nasdaq-label">NASDAQ COMPOSITE (YF)</div>

        {cp_html}

    </div>

""", unsafe_allow_html=True)



st.caption(f"Last Update: {data['update']} (15s Auto Refresh)")



# 4. 자동 새로고침

time.sleep(15)

st.rerun()
