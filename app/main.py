from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from pathlib import Path

from .routes import sessions

app = FastAPI(title="Eye Tracking API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Svelte dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routes
app.include_router(sessions.router, prefix="/api")

# mount frontned
frontend_build_dir = Path(__file__).parent.parent / "fe" / "build"
assets_dir = frontend_build_dir / "_app"

if assets_dir.exists():
    app.mount("/_app", StaticFiles(directory=assets_dir), name="assets")

# root index
@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(frontend_build_dir / "index.html")


# Fallback for client-side routing
@app.get("/{full_path:path}", include_in_schema=False)
def spa_fallback():
    return FileResponse(frontend_build_dir / "index.html")
