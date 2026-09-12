"""FastAPI uygulama giriş noktası."""
from fastapi import FastAPI

from api.routers import auth

app = FastAPI(title="Kararsızım API")

app.include_router(auth.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
