import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go

# Streamlit 페이지 설정
st.set_page_config(layout="wide")  # 페이지를 wide 모드로 설정

# 사이드바를 숨기는 CSS
hide_sidebar_style = """
        <style>
            .css-1d391kg {display: none;}
        </style>
        """
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

def get_market_codes():
    url = "https://api.upbit.com/v1/market/all"
    response = requests.get(url)
    market_data = response.json()
    market_codes = [market['market'] for market in market_data if market['market'].startswith('KRW')]  # KRW 마켓만 필터링
    return market_codes

def get_ohlcv_from_upbit(ticket='KRW-BTC'):
    url = f"https://api.upbit.com/v1/candles/days"
    querystring = {"market": ticket, "count": "1"}
    response = requests.request("GET", url, params=querystring)
    data = response.json()
    return data

def get_ohlcv_list_from_upbit(ticket='KRW-BTC', length=1):
    url = f"https://api.upbit.com/v1/candles/days"
    querystring = {"market": ticket, "count": f"{length}"}
    response = requests.request("GET", url, params=querystring)
    data = response.json()
    return data
def plot_candlestick_chart(ticket, length=20):
    data = get_ohlcv_list_from_upbit(ticket, length=length)
    if data:
        df = pd.DataFrame(data)
        fig = go.Figure(data=[go.Candlestick(x=df['candle_date_time_kst'],
                        open=df['opening_price'],
                        high=df['high_price'],
                        low=df['low_price'],
                        close=df['trade_price'])])

        fig.update_layout(title=f"{ticket} 캔들차트", xaxis_title='날짜', yaxis_title='가격',
                          xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

def plot_trend_daily(ticket):
    data = get_ohlcv_from_upbit(ticket)
    if data:
        opening_price = data[0]['opening_price']
        closing_price = data[0]['trade_price']
        trend = closing_price - opening_price
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=closing_price,
            delta={'reference': opening_price, 'relative': True},
            title={"text": f"{ticket} 일일 추세"}))
        st.plotly_chart(fig, use_container_width=True)

def plot_day_max_min(ticket):
    data = get_ohlcv_from_upbit(ticket)
    if data:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=['최고가', '최저가'],
                             y=[data[0]['high_price'], data[0]['low_price']],
                             marker_color=['green', 'red']))
        fig.update_layout(title=f"{ticket} 일일 최고가와 최저가")
        st.plotly_chart(fig, use_container_width=True)

def plot_volume_trend_daily(ticket):
    data = get_ohlcv_from_upbit(ticket)
    if data:
        high_price = data[0]['high_price']
        low_price = data[0]['low_price']
        volume = data[0]['candle_acc_trade_volume']
        opening_price = data[0]['opening_price']
        closing_price = data[0]['trade_price']
        trend = "상승" if closing_price > opening_price else "하락"

        card_html = """
        <style>
        .card {
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
            transition: 0.3s;
            width: 100%;
            border-radius: 5px;
            height: 100%;
        }

        .card:hover {
            box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
        }

        .container {
            padding: 2px 16px;
        }
        </style>
        """
        card_html += f"""
        <div class="card">
        <div class="container">
            <h4><b>거래량</b></h4> 
           <h3>{trend}</h3> 
            <p><b>{volume}</b></p> 
        </div>
        </div>
        """

        # Streamlit에 카드 스타일 콘텐츠 출력
        st.markdown(card_html, unsafe_allow_html=True)

def plot_price_width_volume_current_trend(ticket):
    data = get_ohlcv_from_upbit(ticket)
    if data:
        high_price = data[0]['high_price']
        low_price = data[0]['low_price']
        volume = data[0]['candle_acc_trade_volume']

        fig = go.Figure(data=[
            go.Bar(name='가격 범위', x=['최고가', '최저가'], y=[high_price, low_price]),
            go.Bar(name='거래량', x=['거래량'], y=[volume])
        ])
        fig.update_layout(title=f"{ticket} 가격 범위 및 거래량")
        st.plotly_chart(fig, use_container_width=True)

def display_show_table(ticket):
    # CSS를 사용하여 컬럼 너비 조정
    st.markdown(
        """
        <style>
        .dataframe {
            margin-top:10px;
            width: 100%;
        }
        .dataframe th, .dataframe td {
            font-size: 11px;
            padding: 10px 10px 10px 10px;  # 상, 우, 하, 좌 패딩 조정
            text-align: left;
        }
        
        .dataframe th {
            background-color: #f0f2f6;
            color: #000;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    data = get_ohlcv_list_from_upbit(ticket, length=5)
    if data:
        df = pd.DataFrame(data)
        st.write("### 거래 데이터 테이블")
        st.dataframe(df)

def main():

    st.title("Day Trend")
    #ticket = st.text_input("티켓을 입력하세요", value='KRW-BTC')
    # 업비트에서 티켓 목록 가져오기
    market_codes = get_market_codes()

    # 티켓 선택을 위한 드롭다운 메뉴 생성
    ticket = st.sidebar.selectbox("티켓을 선택하세요", market_codes, index=4)

    if ticket:

        # 컬럼 분리 설정
        col1,col2 = st.columns(2)
        
        with st.sidebar:
            plot_volume_trend_daily(ticket)
        
        with col1:
            plot_trend_daily(ticket)

        with col2:
            plot_candlestick_chart(ticket, length=60)

        col3, = st.columns(1)

        with col3:
            display_show_table(ticket)

if __name__ == "__main__":
    main()
