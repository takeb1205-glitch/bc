import streamlit as st
import requests
import yfinance as yf
import time
from datetime import datetime

# 페이지 설정 (다크모드 스타일)
st.set_page_config(page_title="Market Monitor", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #121212; }
    div[data-testid="stMetricValue"] { color: #F0B90B !important; font-size: 30px !important; }
    div[data-testid="stMetricDelta"] svg { display: none; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Market Monitor")

# 데이터 가져오기 함수
def fetch_data():
    try:
        # 업비트 & 바이낸스
        u_price = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-BTC").json()[0]['trade_price']
        b_price = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT").json()['price'])
        rate = 1400.0  # 고정 환율
        premium = ((u_price / (b_price * rate)) - 1) * 100

        # 나스닥 (yfinance)
        nq = yf.Ticker("NQ=F").history(period="1d")
        comp = yf.Ticker("^IXIC").history(period="1d")
        
        nq_val = f"{nq['Close'].iloc[-1]:,.2f}"
        comp_val = f"{comp['Close'].iloc[-1]:,.2f}"
        
        return u_price, premium, b_price, nq_val, comp_val
    except:
        return 0, 0, 0, "Error", "Error"

# UI 렌더링
u, p, b, nq, cp = fetch_data()

col1, col2 = st.columns(2)
col1.metric("UPBIT BTC", f"{u:,.0f} KRW")
col1.metric("K-PREMIUM", f"{p:+.2f} %")
col2.metric("BINANCE BTC", f"$ {b:,.2f}")
col2.metric("EXCHANGE RATE", "1,400.00")

st.divider()
st.subheader("📊 NASDAQ Realtime (15m Delayed)")
c1, c2 = st.columns(2)
c1.metric("100 FUTURES", nq)
c2.metric("COMPOSITE", cp)

st.caption(f"Last Update: {datetime.now().strftime('%H:%M:%S')} (Auto refresh)")

# 10초마다 자동 갱신
time.sleep(10)
st.rerun()