import streamlit as st
import requests
import yfinance as yf
import time
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="Market Monitor", layout="centered")

# 2. 스타일 적용 (바이낸스 다크모드 유지)
st.markdown("""
    <style>
    .main { background-color: #121212; }
    div[data-testid="stMetricValue"] { color: #F0B90B !important; font-size: 28px !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #848E9C !important; font-size: 14px !important; }
    .stApp { background-color: #121212; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Market Monitor")

# 3. 데이터 호출 함수 (보안 및 에러 방지 강화)
def fetch_market_data():
    results = {
        "upbit": 0, "binance": 0, "premium": 0,
        "nq": "N/A", "comp": "N/A", "update": datetime.now().strftime('%H:%M:%S')
    }
    
    try:
        # 업비트 시세
        u_res = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-BTC", timeout=5).json()
        results["upbit"] = float(u_res[0]['trade_price'])

        # 바이낸스 시세
        b_res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5).json()
        results["binance"] = float(b_res['price'])

        # 김치 프리미엄 (환율 1400원 기준)
        rate = 1400.0
        results["premium"] = ((results["upbit"] / (results["binance"] * rate)) - 1) * 100

        # 나스닥 데이터 (yfinance가 에러 날 경우를 대비해 예외 처리)
        try:
            # 선물 지수
            nq_data = yf.download("NQ=F", period="1d", interval="1m", progress=False)
            if not nq_data.empty:
                val = nq_data['Close'].iloc[-1]
                results["nq"] = f"{float(val):,.2f}"
            
            # 종합 지수
            cp_data = yf.download("^IXIC", period="1d", interval="1m", progress=False)
            if not cp_data.empty:
                val = cp_data['Close'].iloc[-1]
                results["comp"] = f"{float(val):,.2f}"
        except:
            results["nq"] = "Updating..."
            results["comp"] = "Updating..."

    except Exception as e:
        st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
        
    return results

# 4. 데이터 실행 및 화면 표시
data = fetch_market_data()

col1, col2 = st.columns(2)
with col1:
    st.metric("UPBIT BTC", f"{data['upbit']:,.0f} KRW")
    st.metric("K-PREMIUM", f"{data['premium']:+.2f} %")

with col2:
    st.metric("BINANCE BTC", f"$ {data['binance']:,.2f}")
    st.metric("EXCHANGE RATE", "1,400.00")

st.divider()
st.subheader("📊 NASDAQ Realtime (15m Delayed)")

c1, c2 = st.columns(2)
c1.metric("100 FUTURES", data["nq"])
c2.metric("COMPOSITE", data["comp"])

st.caption(f"Last Update: {data['update']} (15s Auto Refresh)")

# 5. 자동 갱신 (15초)
time.sleep(15)
st.rerun()
