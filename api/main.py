"""FastAPI uygulama giriş noktası."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.routers import auth, polls

app = FastAPI(title="Kararsızım API")

app.include_router(auth.router)
app.include_router(polls.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Yerel geliştirmede statik frontend'i de aynı origin'den servis et (Vercel'de
# statik dosyalar ayrıca /public üzerinden sunulacak — bkz. Faz 4).
PUBLIC_DIR = Path(__file__).resolve().parents[1] / "public"
if PUBLIC_DIR.exists():
    app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="public")
