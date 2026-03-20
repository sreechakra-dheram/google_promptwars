import streamlit as st
import requests
import pandas as pd

def render_dashboard(uploaded_file):
    with st.spinner("Uploading and analyzing video via Sentinel Engine..."):
        file_bytes = uploaded_file.getvalue()
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/analyze",
                files={"file": (uploaded_file.name, file_bytes, uploaded_file.type)}
            )
            data = response.json()
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")
            return

        if not data.get("success"):
            st.error(f"Analysis failed: {data.get('error')}")
            return

        analysis_results = data.get("data", {})
        
        accident_detected = analysis_results.get("accident_detected", False)
        severity = analysis_results.get("severity_score", 0)
        pii_flag = analysis_results.get("pii_detected", False)
        
        if accident_detected and severity > 3:
            st.error("🚨 CRITICAL ACCIDENT DETECTED - DISPATCHING NOW")
        else:
            st.success("✅ ALL CLEAR - NO CRITICAL INCIDENTS")
            
        if pii_flag:
            st.info("🛡️ Privacy Shield Active (PII Masked in backend processing logs)")
            
        st.markdown("---")
        col_map, col_logs = st.columns(2)
        
        with col_map:
            st.subheader("🗺️ Inferred Coordinates")
            lat = analysis_results.get("latitude", 37.7749)
            lon = analysis_results.get("longitude", -122.4194)
            if lat and lon:
                df_map = pd.DataFrame({'lat': [lat], 'lon': [lon]})
                st.map(df_map, zoom=14)
                
        with col_logs:
            st.subheader("📋 System Logs (Structured JSON)")
            st.json(analysis_results)
