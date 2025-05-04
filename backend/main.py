from fastapi import FastAPI
from src.auth.routes import auth_router
from src.events.routes import events_router
from src.errors import register_all_errors
from fastapi.middleware.cors import CORSMiddleware

version = "v1"

description = """
A REST API for a event management app
"""

version_prefix =f"/api/{version}"

app = FastAPI(
    title="Event Management App",
    description=description,
    version=version,
)

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

app.include_router(auth_router, prefix=f"{version_prefix}/auth", tags=["auth"])
app.include_router(events_router, prefix=f"{version_prefix}/event", tags=["event"])