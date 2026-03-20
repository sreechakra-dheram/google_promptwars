import streamlit as st
from frontend.components.sidebar import render_sidebar
from frontend.components.dashboard import render_dashboard

st.set_page_config(page_title="Sentinel Bridge", page_icon="🚨", layout="wide")

st.markdown("""
<style>
body { background-color: #0e1117; color: #FAFAFA; }
.stApp { background-color: #0e1117; }
</style>
""", unsafe_allow_html=True)

st.title("🚨 Sentinel Bridge")
st.subheader("High-fidelity, life-saving accident detection dashboard")

uploaded_file, simulate_clicked = render_sidebar()

if simulate_clicked and uploaded_file:
    render_dashboard(uploaded_file)
elif not uploaded_file:
    st.info("Please upload a CCTV video file to begin the simulation.")
