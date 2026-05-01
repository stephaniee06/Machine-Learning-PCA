from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings

app = FastAPI(
    title="PCA Anomaly Demo API",
    description="Upload CSV, run PCA-based anomaly detection, get 3D points and per-row explanations.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
   # allow_origins=settings.cors_origins,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    return {"message": "PCA Anomaly Demo API", "docs": "/docs"}
