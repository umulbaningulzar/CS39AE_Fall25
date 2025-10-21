import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Pie Chart", page_icon="🥧")
st.title("🥧 Interactive Pie Chart")

# --- Locate CSV robustly ---
here = Path(__file__).resolve()
base_pages = here.parent                 # .../streamlit_CS/pages
base_app   = base_pages.parent           # .../streamlit_CS
repo_root  = base_app.parent             # .../<repo>

candidates = [
    base_app / "data" / "pie_demo.csv",                   # streamlit_CS/data/pie_demo.csv
    Path.cwd() / "streamlit_CS" / "data" / "pie_demo.csv",
    Path.cwd() / "data" / "pie_demo.csv",
    repo_root / "streamlit_CS" / "data" / "pie_demo.csv",
]

DATA_PATH = None
for p in candidates:
    if p.exists():
        DATA_PATH = p
        break

# last-resort search (handles odd working dirs)
if DATA_PATH is None:
    hits = list(Path.cwd().rglob("pie_demo.csv"))
    if hits:
        DATA_PATH = hits[0]

if DATA_PATH is None or not DATA_PATH.exists():
    st.error(
        "Missing data file `pie_demo.csv`.\n\n"
        "I looked in these locations:\n"
        + "\n".join(f"• {p}" for p in candidates)
        + "\n\nTip: ensure the file is committed at `streamlit_CS/data/pie_demo.csv`."
    )
    st.stop()

st.caption(f"Using data file: `{DATA_PATH}`")

# --- Load & validate ---
df = pd.read_csv(DATA_PATH)
if df.shape[1] < 2:
    st.error("CSV needs two columns: a category and a numeric value.")
    st.stop()

# --- Pick columns ---
cat_col = st.selectbox("Select category column:", df.columns, index=0)
num_candidates = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
if not num_candidates:
    st.error("No numeric column found for values.")
    st.stop()
val_col = st.selectbox("Select numeric column:", num_candidates, index=0)

# --- Title & options ---
chart_title = st.text_input("Enter chart title:", value="How I Spend My Week")
sort_opt = st.checkbox("Sort slices descending", value=True)

# --- Aggregate & sort ---
agg = df.groupby(cat_col, as_index=False)[val_col].sum()
if sort_opt:
    agg = agg.sort_values(val_col, ascending=False)

# --- Plot (with percentage labels) ---
fig = px.pie(
    agg, names=cat_col, values=val_col, hole=0.25, title=chart_title
)
fig.update_traces(textposition="inside", texttemplate="%{label}<br>%{percent:.1%}")

st.plotly_chart(fig, use_container_width=True)
st.caption("Edit `streamlit_CS/data/pie_demo.csv` or the title above, then refresh to see updates.")
