"""FastAPI uygulama giriş noktası.

Vercel'de bu dosya `pyproject.toml`'daki `tool.vercel.entrypoint = "api.main:app"`
ile tekil giriş noktası (Python function) olarak kullanılır.
"""
import os
from pathlib import Path

from fastapi import FastAPI

from api.routers import auth, polls

app = FastAPI(title="Kararsızım API")

app.include_router(auth.router)
app.include_router(polls.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Yerel geliştirmede statik frontend'i de aynı origin'den (uvicorn) servis et.
# Vercel'de public/ klasörü platform/CDN seviyesinde otomatik sunulur — kendi
# app.mount() ile sunmamak gerekiyor (bkz. Vercel FastAPI dokümantasyonu), bu
# yüzden Vercel'in enjekte ettiği VERCEL ortam değişkeni varken bu blok atlanır.
if not os.environ.get("VERCEL"):
    from fastapi.staticfiles import StaticFiles

    PUBLIC_DIR = Path(__file__).resolve().parents[1] / "public"
    if PUBLIC_DIR.exists():
        app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="public")
