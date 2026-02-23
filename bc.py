import streamlit as st
import requests
import yfinance as yf
import time
from datetime import datetime

# 1. 페이지 설정 (아이폰 사파리 가독성 최적화)
st.set_page_config(page_title="Market Monitor", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #121212; }
    div[data-testid="stMetricValue"] { color: #F0B90B !important; font-size: 28px !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #848E9C !important; font-size: 14px !important; }
    .stApp { background-color: #121212; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Market Monitor")

# 2. 데이터 호출 함수
def fetch_market_data():
    results = {
        "upbit": 0, "binance": 0, "premium": 0,
        "nq": "Updating...", "comp": "Updating...", "update": datetime.now().strftime('%H:%M:%S')
    }
    
    try:
        # 업비트 시세
        u_res = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-BTC", timeout=5).json()
        results["upbit"] = float(u_res[0]['trade_price'])

        # 바이낸스 시세 (에러 방지용 구조 변경)
        b_res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5).json()
        if 'price' in b_res:
            results["binance"] = float(b_res['price'])
        else:
            results["binance"] = 0

        # 김치 프리미엄 (환율 1400원 기준)
        if results["binance"] > 0:
            rate = 1400.0
            results["premium"] = ((results["upbit"] / (results["binance"] * rate)) - 1) * 100

        # 나스닥 데이터 (yfinance)
        try:
            # yfinance 라이브러리의 한계로 데이터가 늦게 올 수 있음
            nq_ticker = yf.Ticker("NQ=F")
            nq_val = nq_ticker.fast_info['last_price']
            results["nq"] = f"{nq_val:,.2f}"
            
            cp_ticker = yf.Ticker("^IXIC")
            cp_val = cp_ticker.fast_info['last_price']
            results["comp"] = f"{cp_val:,.2f}"
        except:
            pass

    except Exception as e:
        pass # 에러 메시지를 화면에 띄우지 않고 조용히 재시도
        
    return results

# 3. 화면 표시
data = fetch_market_data()

col1, col2 = st.columns(2)
with col1:
    st.metric("UPBIT BTC", f"{data['upbit']:,.0f} KRW")
    st.metric("K-PREMIUM", f"{data['premium']:+.2f} %")

with col2:
    st.metric("BINANCE BTC", f"$ {data['binance']:,.2f}")
    st.metric("EXCHANGE RATE", "1,400.00")

st.divider()
st.subheader("📊 NASDAQ Realtime (Delayed)")

c1, c2 = st.columns(2)
c1.metric("100 FUTURES", data["nq"])
c2.metric("COMPOSITE", data["comp"])

st.caption(f"Last Update: {data['update']} (15s Auto Refresh)")

# 4. 자동 갱신
time.sleep(15)
st.rerun()

