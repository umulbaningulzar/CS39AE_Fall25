import streamlit as st

st.title("👋 My Bio")

# ---------- TODO: Replace with your own info ----------
NAME = "Umulbanin Gulzar"
PROGRAM = "B.S. in Computer Science"
INTRO = (
    "Hi! I'm Umulbanin Gulzar, a Computer Science major who loves learning how technology can solve real-world problems."
    "I'm especially interested in app development and data visualization, and I enjoy exploring creative ways to make information more engaging and useful."
)
FUN_FACTS = [
    "I love designing and coding user-friendly applications.",
    "I’m learning more about data analytics and software engineering.",
    "I want to build technology that helps communities and makes a positive impact."
]
PHOTO_PATH = "your_photo.jpg"  # Put a file in repo root or set a URL

# ---------- Layout ----------
col1, col2 = st.columns([1, 2], vertical_alignment="center")

with col1:
    try:
        st.image(PHOTO_PATH, caption=NAME, use_container_width=True)
    except Exception:
        st.info("Add a photo named `your_photo.jpg` to the repo root, or change PHOTO_PATH.")
with col2:
    st.subheader(NAME)
    st.write(PROGRAM)
    st.write(INTRO)

st.markdown("### Fun facts")
for i, f in enumerate(FUN_FACTS, start=1):
    st.write(f"- {f}")

st.divider()
st.caption("Edit `pages/1_Bio.py` to customize this page.")
