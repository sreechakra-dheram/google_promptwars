import streamlit as st

def render_sidebar():
    st.sidebar.header("Live Feed Control")
    uploaded_file = st.sidebar.file_uploader("Upload CCTV Video", type=["mp4", "avi", "mov"])
    
    simulate_clicked = False
    if uploaded_file:
        st.sidebar.video(uploaded_file)
        st.sidebar.success("Feed connected.")
        simulate_clicked = st.sidebar.button("Simulate Live Feed & Analyze")
        
    return uploaded_file, simulate_clicked
