from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from .routers import sessions

app = FastAPI(title="Aeon Eye Tracking API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Svelte dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router, prefix="/api")

# mount compiled frontend
prerendered_dir = Path(__file__).parent.parent / "fe" / ".svelte-kit" / "output" / "prerendered" / "pages"
client_dir = Path(__file__).parent.parent / "fe" / ".svelte-kit" / "output" / "client"

if client_dir.exists():
    app.mount("/_app", StaticFiles(directory=client_dir / "_app"), name="assets")

if prerendered_dir.exists():
    app.mount("/", StaticFiles(directory=prerendered_dir, html=True), name="pages")

@app.get("/")
async def root():
    return {"message": "Hello World!"}
