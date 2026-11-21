from fastapi import FastAPI

import app.models
from app.auth.router import router as auth_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok"}