import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Finance dashboard", layout="wide")

st.title("Simple finance dashboard")
st.caption("Pick a ticker and range — data from Yahoo Finance.")

with st.sidebar:
    ticker = st.text_input("Ticker", value="AAPL").upper().strip()
    period = st.selectbox("Range", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)


@st.cache_data(ttl=300)
def load_history(symbol: str, range_key: str) -> pd.DataFrame:
    t = yf.Ticker(symbol)
    df = t.history(period=range_key, auto_adjust=True)
    if df.empty:
        raise ValueError(f"No data returned for {symbol!r}. Check the ticker.")
    return df


if not ticker:
    st.warning("Enter a ticker symbol in the sidebar.")
    st.stop()

try:
    data = load_history(ticker, period)
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

latest = float(data["Close"].iloc[-1])
prev = float(data["Close"].iloc[-2]) if len(data) > 1 else latest
chg = latest - prev
pct = (chg / prev * 100) if prev else 0.0

c1, c2, c3 = st.columns(3)
c1.metric(f"{ticker} last close", f"${latest:,.2f}", f"{chg:+.2f} ({pct:+.2f}%)")
c2.metric("Rows", len(data))
c3.metric("Date span", f"{data.index.min().date()} → {data.index.max().date()}")

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["Close"],
        mode="lines",
        name="Close",
        line=dict(width=2),
    )
)
fig.update_layout(
    height=450,
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    hovermode="x unified",
    template="plotly_white",
)
st.plotly_chart(fig, use_container_width=True)

with st.expander("Raw OHLCV (last 10 rows)"):
    st.dataframe(data.tail(10), use_container_width=True)
