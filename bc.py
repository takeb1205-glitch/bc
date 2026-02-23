import streamlit as st
import requests
import yfinance as yf
import time
from datetime import datetime

# 1. 페이지 설정 및 다크모드 스타일 유지
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

# 2. 실시간 환율 및 시장 데이터 호출 함수
def fetch_market_data():
    results = {
        "upbit": 0.0, "binance": 0.0, "premium": 0.0, "rate": 1400.0,
        "update": datetime.now().strftime('%H:%M:%S')
    }
    
    try:
        # A. 실시간 환율 가져오기
        rate_res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5).json()
        if rate_res.get('result') == 'success':
            results["rate"] = float(rate_res['rates']['KRW'])

        # B. 업비트 가격
        u_res = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-BTC", timeout=5).json()
        results["upbit"] = float(u_res[0]['trade_price'])

        # C. 바이낸스 가격 (안정성 강화)
        # 여러 API 엔드포인트 중 가장 안정적인 v3 사용
        b_res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5).json()
        if 'price' in b_res:
            results["binance"] = float(b_res['price'])
        
        # D. 김치 프리미엄 계산
        if results["binance"] > 0 and results["upbit"] > 0:
            krw_binance = results["binance"] * results["rate"]
            results["premium"] = ((results["upbit"] / krw_binance) - 1) * 100

    except Exception as e:
        st.error(f"데이터 연동 중 오류 발생: {e}")
        
    return results

# 3. 나스닥 상세 정보 (이미지 요청 반영)
def get_nasdaq_info(ticker_symbol, label_name):
    try:
        tk = yf.Ticker(ticker_symbol)
        fast = tk.fast_info
        current_price = fast['last_price']
        prev_close = fast['previous_close']
        
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100
        
        color_class = "up" if change >= 0 else "down"
        arrow = "▲" if change >= 0 else "▼"
        
        return f'''
        <div class="nasdaq-label">{label_name}</div>
        <div class="nasdaq-value {color_class}">{current_price:,.2f} ({change:+,.2f} {change_pct:+.2f}% {arrow})</div>
        '''
    except:
        return f'<div class="nasdaq-label">{label_name}</div><div class="nasdaq-value" style="color:white;">연결 중...</div>'

# 4. 화면 UI 출력
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

# 나스닥 섹션 (이미지 레이아웃 반영)
nq_html = get_nasdaq_info("NQ=F", "NASDAQ 100 FUTURES (YF)")
cp_html = get_nasdaq_info("^IXIC", "NASDAQ COMPOSITE (YF)")

st.markdown(f'<div class="nasdaq-container">{nq_html}{cp_html}</div>', unsafe_allow_html=True)

st.caption(f"최종 업데이트: {data['update']} (15초 자동 갱신)")

# 15초 후 자동 새로고침
time.sleep(15)
st.rerun()
