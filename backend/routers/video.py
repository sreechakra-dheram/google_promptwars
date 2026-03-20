from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.video_service import extract_frames, encode_image, apply_pii_masking
from backend.services.gemini_service import analyze_frames
from core.config import settings
import tempfile
import os

router = APIRouter()

# --- Security constants ---
MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB
ALLOWED_CONTENT_TYPES = {"video/mp4", "video/avi", "video/x-msvideo", "video/quicktime", "video/webm"}
ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".webm"}


@router.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    # --- Validate API key exists (don't leak details) ---
    api_key = settings.gemini_api_key
    if not api_key:
        raise HTTPException(status_code=503, detail="Analysis service temporarily unavailable")

    # --- Validate file type ---
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    if ext and ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported content type for video upload")

    # --- Read with size limit ---
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size: {MAX_UPLOAD_BYTES // (1024*1024)} MB")

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext or ".mp4") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        frames = extract_frames(tmp_path, num_frames=3)
        if not frames:
            raise HTTPException(status_code=400, detail="Could not extract frames from video")

        # Apply PII masking before sending to AI
        masked_frames = [apply_pii_masking(f) for f in frames]
        pil_images = [encode_image(f) for f in masked_frames]
        result = analyze_frames(pil_images, api_key)

        return {
            "success": result.get("success", False),
            "data": result.get("data", None),
            "error": result.get("error", None),
            "frames_processed": len(frames)
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal analysis error")
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
