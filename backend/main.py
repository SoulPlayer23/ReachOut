from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from routers.agent import router as agent_router
from routers.auth import router as auth_router
from routers.gmail import router as gmail_router
from routers.history import router as history_router
from routers.onboarding import router as onboarding_router
from routers.sources import router as sources_router

app = FastAPI(title="ReachOut", version="0.1.0")

app.include_router(auth_router)
app.include_router(gmail_router)
app.include_router(onboarding_router)
app.include_router(sources_router)
app.include_router(history_router)
app.include_router(agent_router)


@app.get("/health")
def health():
    return {"status": "ok"}


# Serve built React frontend if the static directory exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_frontend(full_path: str):
        return FileResponse(os.path.join(static_dir, "index.html"))
