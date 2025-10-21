import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Pie Chart", page_icon="🥧")
st.title("🥧 Interactive Pie Chart")

# ✅ Corrected path (works both locally & on Streamlit Cloud)
BASE_DIR = Path(__file__).resolve().parents[1]   # goes up from /pages to /streamlit_CS
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "pie_demo.csv"

# Load data
if not DATA_PATH.exists():
    st.error(f"Missing data file: {DATA_PATH}")
    st.stop()

df = pd.read_csv(DATA_PATH)

# Validate data
if df.shape[1] < 2:
    st.error("CSV must have at least two columns: a category and a numeric value.")
    st.stop()

# Let the user choose columns
cat_col = st.selectbox("Select category column:", df.columns, index=0)
num_candidates = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
if not num_candidates:
    st.error("No numeric column found for values.")
    st.stop()
val_col = st.selectbox("Select numeric column:", num_candidates, index=0)

# Input for chart title
chart_title = st.text_input("Enter chart title:", value="How I Spend My Week")

# Optional sort toggle
sort_opt = st.checkbox("Sort slices descending", value=True)
agg = df.groupby(cat_col, as_index=False)[val_col].sum()
if sort_opt:
    agg = agg.sort_values(val_col, ascending=False)

# Create the pie chart
fig = px.pie(agg, names=cat_col, values=val_col, hole=0.25, title=chart_title)
st.plotly_chart(fig, use_container_width=True)

st.caption("💡 Tip: Edit the CSV file (streamlit_CS/data/pie_demo.csv) or change the title above, then refresh to see updates!")
