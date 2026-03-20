from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from backend.routers import video
import uvicorn
import time
import html
import re
from backend.db.firestore_client import db
from pydantic import BaseModel, field_validator
from typing import Dict, Any, List
from google import genai
from core.config import settings
from gtts import gTTS
import io

app = FastAPI(title="Sentinel Bridge API", docs_url=None, redoc_url=None)

# --- Security: Restrict CORS origins ---
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# --- Security: Add security headers to all responses ---
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: blob:; "
        "media-src 'self' blob:; "
        "connect-src 'self'"
    )
    return response


# --- Global exception handler: never leak internals ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(video.router, prefix="/api/v1")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def serve_index():
    return FileResponse("static/index.html")


@app.get("/analyze")
def serve_analyze():
    return FileResponse("static/analyze.html")


@app.get("/health")
def health_check():
    cam_count = 0
    incident_count = 0
    if db:
        try:
            cams = list(db.collection("cameras").stream())
            cam_count = len(cams)
            online = sum(1 for c in cams if c.to_dict().get("status") in ("LIVE", "ALERT"))
        except Exception:
            online = 0
        try:
            incidents = list(db.collection("incidents").stream())
            incident_count = len(incidents)
        except Exception:
            pass
    else:
        online = 0

    return {
        "status": "ok",
        "timestamp": time.time(),
        "cameras_online": online,
        "cameras_total": cam_count,
        "incidents_today": incident_count,
    }


@app.get("/cameras")
def get_cameras():
    if not db:
        return []
    docs = db.collection("cameras").stream()
    return [doc.to_dict() for doc in docs]


@app.get("/cameras/{cam_id}")
def get_camera(cam_id: str):
    if not re.match(r"^[A-Za-z0-9_-]{1,20}$", cam_id):
        raise HTTPException(status_code=400, detail="Invalid camera ID format")
    if not db:
        return {}
    doc = db.collection("cameras").document(cam_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Camera not found")
    return doc.to_dict()


class IncidentItem(BaseModel):
    data: Dict[str, Any]


@app.post("/cameras/{cam_id}/incident")
def create_incident(cam_id: str, incident: IncidentItem):
    if not re.match(r"^[A-Za-z0-9_-]{1,20}$", cam_id):
        raise HTTPException(status_code=400, detail="Invalid camera ID format")
    if not db:
        return {"success": False, "detail": "Database unavailable"}
    doc_ref = db.collection("incidents").document()
    doc_data = incident.data
    doc_data["cam_id"] = cam_id
    doc_data["timestamp"] = time.time()
    doc_ref.set(doc_data)
    return {"id": doc_ref.id, "success": True}


@app.get("/incidents")
def get_incidents():
    if not db:
        return []
    from google.cloud import firestore
    docs = db.collection("incidents").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(20).stream()
    return [doc.to_dict() for doc in docs]


# --- Validated request models ---
class AssistantRequest(BaseModel):
    message: str
    context: Dict[str, Any]

    @field_validator("message")
    @classmethod
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        if len(v) > 1000:
            raise ValueError("Message too long (max 1000 chars)")
        return v.strip()


@app.post("/assistant")
def assistant_endpoint(req: AssistantRequest):
    if not settings.gemini_api_key:
        raise HTTPException(status_code=503, detail="Assistant service unavailable")

    # Sanitize user input before sending to AI
    safe_message = html.escape(req.message)
    safe_context = {k: html.escape(str(v)) if isinstance(v, str) else v for k, v in req.context.items()}

    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = f"""You are Sentinel AI, an emergency dispatch assistant for government road safety operators.
Current active incident context: {safe_context}
Answer concisely. If asked about dispatch status, units, ETA, or location — answer from context.
If asked something outside your scope, say: "Please contact the field unit directly."
User message: {safe_message}"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        return {"response": response.text}
    except Exception:
        raise HTTPException(status_code=502, detail="AI service error")


class BroadcastRequest(BaseModel):
    cam_id: str
    incident_type: str
    severity: int
    address: str
    units: List[str]

    @field_validator("cam_id")
    @classmethod
    def validate_cam_id(cls, v):
        if not re.match(r"^[A-Za-z0-9_-]{1,20}$", v):
            raise ValueError("Invalid camera ID")
        return v

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v):
        if v < 0 or v > 10:
            raise ValueError("Severity must be 0-10")
        return v

    @field_validator("incident_type")
    @classmethod
    def validate_incident_type(cls, v):
        if len(v) > 200:
            raise ValueError("Incident type too long")
        return v.strip()

    @field_validator("address")
    @classmethod
    def validate_address(cls, v):
        if len(v) > 300:
            raise ValueError("Address too long")
        return v.strip()


@app.post("/broadcast")
def broadcast_endpoint(req: BroadcastRequest):
    current_time = time.strftime("%H:%M:%S")
    unit_summary = ", ".join(req.units[:10]) if req.units else "No units"
    sentence = f"At {current_time}, AI analysis of {req.cam_id} detected a {req.incident_type} near {req.address} with severity {req.severity}/10. {unit_summary} have been dispatched."

    tts = gTTS(text=sentence, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return StreamingResponse(fp, media_type="audio/mpeg")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
