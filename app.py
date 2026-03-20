import streamlit as st
import cv2
import tempfile
import time
import os
import json
import pandas as pd
from gtts import gTTS
import google.generativeai as genai

# --- CONFIGURATION ---
st.set_page_config(page_title="Sentinel Bridge", page_icon="🚨", layout="wide")

st.markdown("""
<style>
/* Custom Dark Theme Styles for Vibe */
body {
    background-color: #0e1117;
    color: #FAFAFA;
}
.stApp {
    background-color: #0e1117;
}
.status-card-red {
    background-color: #ff4b4b;
    color: white;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    box-shadow: 0 0 15px #ff4b4b;
    animation: flash 1.5s infinite;
}
.status-card-green {
    background-color: #00cc66;
    color: white;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
}
@keyframes flash {
  0%   {box-shadow: 0 0 10px #ff4b4b;}
  50%  {box-shadow: 0 0 30px #ff4b4b;}
  100% {box-shadow: 0 0 10px #ff4b4b;}
}
.privacy-badge {
    background-color: #1f77b4;
    color: white;
    padding: 5px 10px;
    border-radius: 5px;
    font-weight: bold;
    display: inline-block;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# --- SECURITY AGENT ---
def apply_pii_masking(frame):
    """
    Simulates a security agent blurring PII (faces/license plates).
    For the hackathon, we apply a distinct blur to simulate face and license plate masking.
    """
    h, w = frame.shape[:2]
    masked_frame = frame.copy()
    
    # Blur human-height regions
    roi = masked_frame[int(h*0.1):int(h*0.5), int(w*0.3):int(w*0.7)]
    if roi.size > 0:
        masked_frame[int(h*0.1):int(h*0.5), int(w*0.3):int(w*0.7)] = cv2.GaussianBlur(roi, (51, 51), 0)
    
    # Blur bottom region for license plates
    roi2 = masked_frame[int(h*0.7):h, :]
    if roi2.size > 0:
        masked_frame[int(h*0.7):h, :] = cv2.GaussianBlur(roi2, (51, 51), 0)
        
    return masked_frame

# --- ANALYSIS AGENT ---
def analyze_frames_with_gemini(frames, api_key):
    """
    Uses Gemini multimodal reasoning to output structured JSON of emergency incident details.
    """
    genai.configure(api_key=api_key)
    
    # Use flash model as requested in the task description requirements
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = '''
    You are an emergency response expert analyzing CCTV footage frames.
    Analyze the provided images (Pre-impact, Impact, Aftermath) left to right in chronological order.
    Determine if an accident occurred.
    Return ONLY a highly structured JSON object.
    
    Format required:
    {
      "incident_type": "string (e.g., 'Vehicle Collision', 'None')",
      "vehicle_count": 2,
      "severity_score": 8,
      "required_units": ["Ambulance", "Police"],
      "pii_detected": true,
      "accident_detected": true,
      "latitude": 37.7749,
      "longitude": -122.4194
    }
    '''
    
    import PIL.Image
    pil_images = [PIL.Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)) for f in frames]
    
    try:
        response = model.generate_content([prompt, pil_images[0], pil_images[1], pil_images[2]], 
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        data = json.loads(response.text)
        return data
    except Exception as e:
        st.error(f"Gemini Analysis Error: {e}")
        return {
            "incident_type": "Unknown",
            "vehicle_count": 0,
            "severity_score": 0,
            "required_units": ["None"],
            "pii_detected": False,
            "accident_detected": False,
            "latitude": 37.7749,
            "longitude": -122.4194
        }

# --- UI LOGIC ---
st.title("🚨 Sentinel Bridge")
st.subheader("High-fidelity, life-saving accident detection dashboard")

st.sidebar.header("Live Feed Control")
api_key = st.sidebar.text_input("Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))

uploaded_file = st.sidebar.file_uploader("Upload CCTV Video", type=["mp4", "avi", "mov"])

if uploaded_file and api_key:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    tfile.close()

    st.sidebar.video(tfile.name)
    st.sidebar.success("Feed connected.")
    
    if st.sidebar.button("Simulate Live Feed & Analyze"):
        with st.spinner("Processing CCTV feed at 1 FPS..."):
            cap = cv2.VideoCapture(tfile.name)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Sample 3 frames
            frames = []
            if total_frames > 3:
                frame_indices = [max(int(total_frames*0.1), 0), max(int(total_frames*0.5), 0), min(int(total_frames*0.9), total_frames-1)]
                for idx in frame_indices:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                    ret, frame = cap.read()
                    if ret:
                        frames.append(frame)
            else:
                # Video too short, grab first frame 3 times
                ret, frame = cap.read()
                if ret:
                    frames = [frame, frame, frame]
            cap.release()
            
            if len(frames) == 3:
                st.info("Frames extracted. Invoking Designer & Security Agents...")
                
                analysis_results = analyze_frames_with_gemini(frames, api_key)
                pii_flag = analysis_results.get("pii_detected", False)
                
                # Render UI
                processed_frames = [apply_pii_masking(f) if pii_flag else f for f in frames]
                accident_detected = analysis_results.get("accident_detected", False)
                severity = analysis_results.get("severity_score", 0)
                
                if accident_detected and severity > 3:
                    st.markdown('<div class="status-card-red">CRITICAL ACCIDENT DETECTED - DISPATCHING NOW</div>', unsafe_allow_html=True)
                    try:
                        tts = gTTS(text="CRITICAL ACCIDENT DETECTED - DISPATCHING NOW.", lang='en')
                        audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                        tts.save(audio_file.name)
                        st.audio(audio_file.name, autoplay=True)
                    except Exception as e:
                        st.error(f"TTS Error: {e}")
                else:
                    st.markdown('<div class="status-card-green">ALL CLEAR - NO CRITICAL INCIDENTS</div>', unsafe_allow_html=True)
                
                if pii_flag:
                     st.markdown('<div class="privacy-badge">🛡️ Privacy Shield Active (PII Masked)</div>', unsafe_allow_html=True)
                
                st.markdown("---")
                st.subheader("📷 Frame Analysis")
                col1, col2, col3 = st.columns(3)
                labels = ["Pre-impact", "Impact", "Aftermath"]
                cols = [col1, col2, col3]
                
                for col, frame, label in zip(cols, processed_frames, labels):
                    with col:
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        st.image(rgb_frame, caption=label, use_container_width=True)
                
                st.markdown("---")
                col_map, col_logs = st.columns(2)
                
                with col_map:
                    st.subheader("🗺️ Inferred Coordinates")
                    lat = analysis_results.get("latitude", 37.7749)
                    lon = analysis_results.get("longitude", -122.4194)
                    if lat and lon:
                        df_map = pd.DataFrame({'lat': [lat], 'lon': [lon]})
                        st.map(df_map, zoom=14)
                    else:
                        st.warning("No location data found.")
                        
                with col_logs:
                    st.subheader("📋 System Logs (Structured JSON)")
                    st.json(analysis_results)
            else:
                st.error("Could not extract enough frames from the video. Please try a different file.")
elif not api_key:
    st.warning("Please enter your Gemini API Key in the sidebar to proceed.")
else:
    st.info("Please upload a CCTV video file to begin the simulation.")
