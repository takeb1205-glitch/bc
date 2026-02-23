import streamlit as st
import requests
import yfinance as yf
import time
from datetime import datetime

# 1. 페이지 설정 및 다크모드 디자인 커스텀
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

# 2. 실시간 데이터 호출 함수 (안정성 극대화)
def fetch_market_data():
    results = {
        "upbit": 0.0, "binance": 0.0, "premium": 0.0, "rate": 1447.07,
        "nq": "데이터 연결 중...", "cp": "데이터 연결 중...",
        "update": datetime.now().strftime('%H:%M:%S')
    }
    
    try:
        # A. 실시간 환율 (에러 발생 시 기존 값 유지)
        try:
            rate_res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5).json()
            if rate_res.get('result') == 'success':
                results["rate"] = float(rate_res['rates']['KRW'])
        except: pass

        # B. 업비트 시세
        u_res = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-BTC", timeout=5).json()
        results["upbit"] = float(u_res[0]['trade_price'])

        # C. 바이낸스 시세 (연결 실패 대비 다중 경로 사용)
        try:
            b_res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5).json()
            results["binance"] = float(b_res['price'])
        except:
            # 예비 경로
            b_res = requests.get("https://api1.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5).json()
            results["binance"] = float(b_res['price'])
        
        # D. 김치 프리미엄 계산
        if results["binance"] > 0:
            krw_binance = results["binance"] * results["rate"]
            results["premium"] = ((results["upbit"] / krw_binance) - 1) * 100

        # E. 나스닥 데이터 상세 (yfinance 안정화 방식)
        for ticker, label in [("NQ=F", "nq"), ("^IXIC", "cp")]:
            try:
                tk = yf.Ticker(ticker)
                # fast_info 대신 history를 사용하여 안정적으로 데이터 추출
                hist = tk.history(period="2d")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2]
                    change = current - prev
                    pct = (change / prev) * 100
                    
                    color = "up" if change >= 0 else "down"
                    arrow = "▲" if change >= 0 else "▼"
                    name = "NASDAQ 100 FUTURES (YF)" if label == "nq" else "NASDAQ COMPOSITE (YF)"
                    
                    results[label] = f'''
                    <div class="nasdaq-label">{name}</div>
                    <div class="nasdaq-value {color}">{current:,.2f} ({change:+,.2f} {pct:+.2f}% {arrow})</div>
                    '''
            except:
                results[label] = f'<div class="nasdaq-label">데이터 확인 중...</div>'

    except Exception as e:
        pass
        
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

# 나스닥 섹션 (HTML 렌더링)
st.markdown(f'<div class="nasdaq-container">{data["nq"]}{data["cp"]}</div>', unsafe_allow_html=True)

st.caption(f"최종 업데이트: {data['update']} (15초 자동 갱신)")

# 15초 후 새로고침
time.sleep(15)
st.rerun()567890
