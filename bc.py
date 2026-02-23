import streamlit as st
import requests
import yfinance as yf
import time
from datetime import datetime

# 1. 페이지 설정 및 다크모드 커스텀 디자인
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

# 2. 데이터 호출 함수 (오류 방지 및 안정성 극대화)
def fetch_market_data():
    results = {
        "upbit": 0.0, "binance": 0.0, "premium": 0.0, "rate": 1447.07,
        "nq_html": "데이터 연결 중...", "cp_html": "데이터 연결 중...",
        "update": datetime.now().strftime('%H:%M:%S')
    }
    
    try:
        # A. 실시간 환율 (에러 대비 기본값 설정)
        try:
            rate_res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5).json()
            if rate_res.get('result') == 'success':
                results["rate"] = float(rate_res['rates']['KRW'])
        except: pass

        # B. 업비트 시세
        u_res = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-BTC", timeout=5).json()
        results["upbit"] = float(u_res[0]['trade_price'])

        # C. 바이낸스 시세 ($0.00 해결을 위한 다중 경로)
        for url in ["https://api.binance.com/api/v3/ticker/price", "https://api1.binance.com/api/v3/ticker/price"]:
            try:
                b_res = requests.get(f"{url}?symbol=BTCUSDT", timeout=5).json()
                if 'price' in b_res:
                    results["binance"] = float(b_res['price'])
                    break
            except: continue
        
        # D. 김치 프리미엄 계산
        if results["binance"] > 0:
            krw_binance = results["binance"] * results["rate"]
            results["premium"] = ((results["upbit"] / krw_binance) - 1) * 100

        # E. 나스닥 상세 정보 (YF)
        for ticker, key in [("NQ=F", "nq_html"), ("^IXIC", "cp_html")]:
            try:
                tk = yf.Ticker(ticker)
                hist = tk.history(period="2d")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2]
                    change = current - prev
                    pct = (change / prev) * 100
                    
                    color = "up" if change >= 0 else "down"
                    arrow = "▲" if change >= 0 else "▼"
                    name = "NASDAQ 100 FUTURES (YF)" if "NQ" in ticker else "NASDAQ COMPOSITE (YF)"
                    
                    results[key] = f'''
                    <div class="nasdaq-label">{name}</div>
                    <div class="nasdaq-value {color}">{current:,.2f} ({change:+,.2f} {pct:+.2f}% {arrow})</div>
                    '''
            except:
                results[key] = f'<div class="nasdaq-label">데이터 동기화 중...</div>'

    except: pass
    return results

# 3. 화면 UI 출력
data = fetch_market_data()

col1, col2 = st.columns(2)
with col1:
    st.metric("UPBIT BTC", f"{data['upbit']:,.0f} KRW")
    st.metric("K-PREMIUM", f"{data['premium']:+.2f} %")

with col2:
    st.metric("BINANCE BTC", f"$ {data['binance']:,.2f}")
    st.metric("실시간 환율 (USD/KRW)", f"{data['rate']:,.2f}")

st.divider()
st.subheader("📊 NASDAQ Realtime (YF)")

# 나스닥 섹션 출력 (디자인 적용)
st.markdown(f'''
    <div class="nasdaq-container">
        {data["nq_html"]}
        {data["cp_html"]}
    </div>
''', unsafe_allow_html=True)

st.caption(f"최종 업데이트: {data['update']} (15초 자동 갱신)")

# 4. 자동 갱신 (오류 방지를 위해 정교하게 작성)
time.sleep(15)
st.rerun()
