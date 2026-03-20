# 🚨 Sentinel Bridge

**High-fidelity, life-saving accident detection dashboard**

Sentinel Bridge is a comprehensive 2-tier application built for real-time emergency response. It processes CCTV video frames, uses Google's Gemini multimodal reasoning to determine accident severity, and displays results on a modern, dark-mode Streamlit dashboard.

## 🏗️ Architecture
- **Backend**: FastAPI (Handles video processing, OpenCV PII masking, and Gemini API integration)
- **Frontend**: Streamlit (Provides a reactive UI, file uploads, mapping, and structured JSON logs)

---

## 🚀 1. Running the Project Locally

### Prerequisites
- Python 3.10+ installed

### Installation Steps
1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd sentinel-bridge
   ```
2. **Set up a Virtual Environment:**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Command to Start Servers
For convenience, we provide a `start.bat` file for Windows:
```bash
.\start.bat
```

**To run them manually:**
1. Start the FastAPI Backend:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```
2. Start the Streamlit Frontend (in a new terminal):
   ```bash
   streamlit run frontend/app.py --server.port 8501
   ```
Once started, open `http://localhost:8501` in your browser.

---

## 🔐 2. Environment Variables Setup

The application securely manages sensitive data via a `.env` file. **Never commit your `.env` file to version control.**

1. **Create the `.env` file:** 
   Copy the provided `.env.example` template:
   ```bash
   cp .env.example .env
   ```
2. **Configure Required Keys:**
   Open the `.env` file and set the following required values:
   ```ini
   # Required: Get this from Google AI Studio
   GEMINI_API_KEY=your_actual_api_key_here
   ```

---

## 🛑 3. Git Ignore Configuration

We have included a secure `.gitignore` file to ensure sensitive keys and virtual environments are not leaked. 

If you accidentally committed your `.env` file or virtual environment folder earlier, run the following commands to untrack and safely remove them from the Git cache (without deleting the actual files on your machine):

```bash
# Remove .env from git cache
git rm --cached .env

# Remove venv folder from git cache
git rm -r --cached venv/

# Commit the removal
git commit -m "chore: remove sensitive tracking of .env and venv"
```

To verify that your `.env` is ignored, typing `git status` should no longer suggest adding the `.env` file.
