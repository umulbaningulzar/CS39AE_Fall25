# 4_Crypto_Live.py
import time
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="📡 Live Crypto (CoinGecko)", page_icon="📡", layout="wide")
st.title("📡 Live Crypto (CoinGecko)")
st.caption("Cached fetch, short session history, auto-refresh, tidy chart + metrics.")

# --- Styling: prevent blink during reruns
st.markdown("""
<style>
  [data-testid="stPlotlyChart"], .stPlotlyChart, .stElementContainer { transition: none !important; opacity: 1 !important; }
</style>
""", unsafe_allow_html=True)

# --- Config
COINS = ["bitcoin", "ethereum"]
VS = "usd"
HEADERS = {"User-Agent": "msudenver-dataviz-class/1.0", "Accept": "application/json"}

def build_url(ids):
    return f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies={VS}"

API_URL = build_url(COINS)

SAMPLE_DF = pd.DataFrame(
    [{"coin": "bitcoin", VS: 68000}, {"coin": "ethereum", VS: 3500}]
)

# --- Cache fetch (polite + fast)
@st.cache_data(ttl=300, show_spinner=False)
def fetch_prices(url: str):
    try:
        resp = requests.get(url, timeout=10, headers=HEADERS)
        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After", "a bit")
            return None, f"429 Too Many Requests — try again after {retry_after}s"
        resp.raise_for_status()
        data = resp.json()
        df = pd.DataFrame(data).T.reset_index().rename(columns={"index": "coin"})
        return df, None
    except requests.RequestException as e:
        return None, f"Network/HTTP error: {e}"

# --- Auto Refresh Controls
st.subheader("🔁 Auto Refresh Settings")
refresh_sec = st.slider("Refresh every (sec)", 10, 120, 30)
auto_refresh = st.toggle("Enable auto-refresh", value=False)
st.caption(f"Last refreshed at: {time.strftime('%H:%M:%S')}")

# --- Session history (short window)
if "crypto_hist" not in st.session_state:
    st.session_state.crypto_hist = pd.DataFrame(columns=["time", "coin", VS])

df, err = fetch_prices(API_URL)
if err:
    st.warning(f"{err}\nShowing sample data so the demo continues.")
    df = SAMPLE_DF.copy()

# append to history (long format)
now = pd.Timestamp.utcnow()
hist_rows = []
for _, row in df.iterrows():
    hist_rows.append({"time": now, "coin": row["coin"], VS: float(row[VS])})
st.session_state.crypto_hist = pd.concat([st.session_state.crypto_hist, pd.DataFrame(hist_rows)], ignore_index=True)

# keep only last 60 points (about one hour if every ~60s)
st.session_state.crypto_hist = st.session_state.crypto_hist.tail(60)

# --- Metrics
st.subheader("Current Prices")
cols = st.columns(len(COINS))
for i, c in enumerate(COINS):
    cur = df.loc[df["coin"] == c, VS].iloc[0]
    prev = st.session_state.crypto_hist.query("coin == @c").iloc[:-1][VS].tail(1)
    delta = None if prev.empty else cur - float(prev.values[0])
    cols[i].metric(label=c.capitalize(), value=f"{cur:,.2f} {VS.upper()}", delta=None if delta is None else f"{delta:,.2f}")

# --- Chart (line over time from history)
st.subheader("Prices Over Time")
line = px.line(
    st.session_state.crypto_hist,
    x="time", y=VS, color="coin",
    labels={"time": "Time (UTC)", VS: VS.upper()},
    title=f"CoinGecko live {VS.upper()} prices"
)
st.plotly_chart(line, use_container_width=True)

# --- Raw table (optional)
with st.expander("Show recent history table"):
    st.dataframe(st.session_state.crypto_hist.sort_values("time", ascending=False), use_container_width=True)

# Auto-refresh loop
if auto_refresh:
    time.sleep(refresh_sec)
    fetch_prices.clear()      # allow fresh API call after TTL if needed
    st.rerun()
