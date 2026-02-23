import streamlit as st
import requests
import yfinance as yf
import time
from datetime import datetime

# 1. 페이지 설정 및 다크모드 스타일 (기존 완벽 유지)
st.set_page_config(page_title="Market Monitor", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #121212; }
    div[data-testid="stMetricValue"] { color: #F0B90B !important; font-size: 26px !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #848E9C !important; font-size: 14px !important; }
    .stApp { background-color: #121212; }
    .nasdaq-container { margin-top: 10px; text-align: left; }
    .nasdaq-label { color: #848E9C; font-size: 14px; font-weight: bold; margin-bottom: 2px; }
    .nasdaq-value { font-size: 24px; font-weight: bold; margin-bottom: 15px; }
    .up { color: #0ECB81; } .down { color: #F6465D; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Market Monitor")

# 2. 나스닥 데이터 호출 함수 (기존 완벽 유지)
def get_nasdaq_info(ticker_symbol):
    try:
        tk = yf.Ticker(ticker_symbol)
        hist = tk.history(period="5d")
        
        if hist is None or hist.empty or len(hist) < 2:
            return '<div class="nasdaq-value" style="color:#848E9C;">장 마감 또는 데이터 지연</div>'

        current_price = float(hist['Close'].iloc[-1])
        prev_close = float(hist['Close'].iloc[-2])
        
        if prev_close == 0:
            return '<div class="nasdaq-value" style="color:#848E9C;">계산 오류 (이전 가격 0)</div>'
            
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100
        
        color_class = "up" if change >= 0 else "down"
        arrow = "▲" if change >= 0 else "▼"
        
        return f'<div class="nasdaq-value {color_class}">{current_price:,.2f} ({change:+,.2f} {change_pct:+.2f}% {arrow})</div>'
    except Exception as e:
        return '<div class="nasdaq-value" style="color:#F6465D;">연결 오류 (재시도 중)</div>'

# 3. 코인 및 환율 데이터 호출 함수 (🔥 코인베이스로 교체)
def fetch_market_data():
    results = {
        "upbit": 0.0, 
        "coinbase": 0.0, # 바이낸스 대신 코인베이스 변수 사용
        "premium": 0.0, 
        "rate": 1400.0,  
        "update": datetime.now().strftime('%H:%M:%S')
    }
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    # A. 실시간 환율
    try:
        rate_res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=3).json()
        if rate_res.get('result') == 'success':
            results["rate"] = float(rate_res['rates']['KRW'])
    except: pass

    # B. 업비트 코인
    try:
        u_res = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-BTC", headers=headers, timeout=3).json()
        results["upbit"] = float(u_res[0]['trade_price'])
    except: pass

    # C. 🔥 코인베이스 코인 (바이낸스 대체, API 접근이 훨씬 유연합니다)
    try:
        cb_res = requests.get("https://api.coinbase.com/v2/prices/BTC-USD/spot", headers=headers, timeout=4).json()
        if 'data' in cb_res and 'amount' in cb_res['data']:
            results["coinbase"] = float(cb_res['data']['amount'])
    except: pass

    # D. 프리미엄 계산
    if results["upbit"] > 0 and results["coinbase"] > 0:
        krw_coinbase = results["coinbase"] * results["rate"]
        results["premium"] = ((results["upbit"] / krw_coinbase) - 1) * 100

    return results

# 4. 화면 UI 렌더링 (COINBASE로 텍스트 변경)
data = fetch_market_data()

col1, col2 = st.columns(2)
with col1:
    st.metric("UPBIT BTC", f"{data['upbit']:,.0f} KRW")
    st.metric("K-PREMIUM", f"{data['premium']:+.2f} %")
    
with col2:
    st.metric("COINBASE BTC", f"$ {data['coinbase']:,.2f}") # 라벨 변경
    st.metric("REALTIME EXCHANGE RATE", f"{data['rate']:,.2f} KRW")

st.divider()
st.subheader("📊 NASDAQ Realtime (YF)")

# 나스닥 데이터 불러오기
nq_html = get_nasdaq_info("NQ=F")
cp_html = get_nasdaq_info("^IXIC")

# 나스닥 UI 출력
st.markdown(f"""
    <div class="nasdaq-container">
        <div class="nasdaq-label">NASDAQ 100 FUTURES (YF)</div>
        {nq_html}
        <div class="nasdaq-label">NASDAQ COMPOSITE (YF)</div>
        {cp_html}
    </div>
""", unsafe_allow_html=True)

st.caption(f"Last Update: {data['update']} (15s Auto Refresh)")

# 5. 자동 새로고침
time.sleep(15)
st.rerun()
