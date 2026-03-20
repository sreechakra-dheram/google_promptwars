from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.video_service import extract_frames, encode_image
from backend.services.gemini_service import analyze_frames
from core.config import settings
import tempfile
import os

router = APIRouter()

@router.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    api_key = settings.gemini_api_key
    if not api_key:
        raise HTTPException(status_code=500, detail="Server misconfigured: Gemini API Key is missing")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        frames = extract_frames(tmp_path, num_frames=3)
        if not frames:
            raise HTTPException(status_code=400, detail="Could not extract frames")
        
        pil_images = [encode_image(f) for f in frames]
        result = analyze_frames(pil_images, api_key)

        
        return {
            "success": result.get("success", False),
            "data": result.get("data", None),
            "error": result.get("error", None),
            "frames_processed": len(frames)
        }
    finally:
        os.remove(tmp_path)
