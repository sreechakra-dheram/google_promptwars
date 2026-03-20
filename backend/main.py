from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from backend.routers import video
import uvicorn
import time
from backend.db.firestore_client import db
from pydantic import BaseModel
from typing import Dict, Any, List
from google import genai
from core.config import settings
from gtts import gTTS
import io

app = FastAPI(title="Sentinel Bridge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(video.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": time.time(),
        "cameras_online": 6, 
        "incidents_today": 0 
    }

@app.get("/cameras")
def get_cameras():
    if not db: return []
    docs = db.collection("cameras").stream()
    return [doc.to_dict() for doc in docs]

@app.get("/cameras/{cam_id}")
def get_camera(cam_id: str):
    if not db: return {}
    doc = db.collection("cameras").document(cam_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Camera not found")
    return doc.to_dict()

class IncidentItem(BaseModel):
    data: Dict[str, Any]

@app.post("/cameras/{cam_id}/incident")
def create_incident(cam_id: str, incident: IncidentItem):
    if not db: return {"success": False}
    doc_ref = db.collection("incidents").document()
    doc_data = incident.data
    doc_data["cam_id"] = cam_id
    doc_data["timestamp"] = time.time()
    doc_ref.set(doc_data)
    return {"id": doc_ref.id, "success": True}

@app.get("/incidents")
def get_incidents():
    if not db: return []
    # from google.cloud import firestore import below to avoid circular if needed
    from google.cloud import firestore
    docs = db.collection("incidents").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(20).stream()
    return [doc.to_dict() for doc in docs]

class AssistantRequest(BaseModel):
    message: str
    context: Dict[str, Any]

@app.post("/assistant")
def assistant_endpoint(req: AssistantRequest):
    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = f"""You are Sentinel AI, an emergency dispatch assistant for government road safety operators.
Current active incident context: {req.context}
Answer concisely. If asked about dispatch status, units, ETA, or location — answer from context.
If asked something outside your scope, say: "Please contact the field unit directly."
User message: {req.message}"""

    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt
    )
    return {"response": response.text}

class BroadcastRequest(BaseModel):
    cam_id: str
    incident_type: str
    severity: int
    address: str
    units: List[str]

@app.post("/broadcast")
def broadcast_endpoint(req: BroadcastRequest):
    current_time = time.strftime("%H:%M:%S")
    unit_summary = ", ".join(req.units) if req.units else "No units"
    sentence = f"At {current_time}, AI analysis of {req.cam_id} detected a {req.incident_type} near {req.address} with severity {req.severity}/10. {unit_summary} have been dispatched."
    
    tts = gTTS(text=sentence, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return StreamingResponse(fp, media_type="audio/mpeg")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
