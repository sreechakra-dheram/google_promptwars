from fastapi import FastAPI
from backend.routers import video
import uvicorn

app = FastAPI(title="Sentinel Bridge API")

app.include_router(video.router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
