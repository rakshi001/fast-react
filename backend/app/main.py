"""
============================================================================
 main.py — FastAPI Application Entry Point
============================================================================

PURPOSE:
  This is where our FastAPI application is created and configured.
  Think of it as the "control room" that wires everything together:
  - Creates the FastAPI app instance
  - Configures middleware (CORS, etc.)
  - Mounts all API routers
  - Sets up database table creation

WHY IT EXISTS:
  Every FastAPI application needs an entry point — the file that
  `uvicorn` runs. This file should be THIN — it creates and configures
  the app, but the actual logic lives in the routers, services, etc.

HOW IT INTERACTS:
  - Imports and mounts routers from api/ directory
  - Uses core/database.py to create tables on startup
  - Run via: uvicorn app.main:app --reload

CONCEPT — CORS (Cross-Origin Resource Sharing):
  When your frontend (localhost:5173) makes a request to your backend
  (localhost:8000), the browser blocks it by default — they're on
  different "origins" (different ports count as different origins).

  CORS middleware tells the browser: "It's okay, I allow requests
  from these specific origins." Without this, the frontend can't
  talk to the backend at all.

CONCEPT — Middleware:
  Middleware is code that runs BETWEEN receiving a request and
  sending a response. It can modify requests, responses, or add
  functionality like logging, auth checks, or CORS headers.

CONCEPT — Lifespan Events:
  The `lifespan` function runs code at application startup and
  shutdown. We use it to create database tables on first run.
============================================================================
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, projects, notes

# Import ALL models so SQLAlchemy knows about them when creating tables.
# Without these imports, Base.metadata won't include our tables.
from app.models import user, project, note  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events — runs at startup and shutdown.

    - On startup: creates all database tables (if they don't exist)
    - On shutdown: (nothing for now, but this is where you'd close
      connections, flush caches, etc.)

    create_all() is safe to run multiple times — it only creates
    tables that don't already exist. It won't modify existing tables.
    
    In production, you'd use Alembic migrations instead of create_all(),
    but for development this is much simpler and faster.
    """
    # STARTUP: Create database tables
    print("🚀 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")

    yield  # The app runs here

    # SHUTDOWN: Cleanup (if needed)
    print("👋 Application shutting down...")


# ============================================================================
# Create the FastAPI Application
# ============================================================================
app = FastAPI(
    title=settings.APP_NAME,
    description="A productivity app for organizing notes into projects.",
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================================
# CORS Middleware Configuration
# ============================================================================
# allow_origins: Which frontend URLs can access our API
#   - ["*"] means "any origin" (fine for development)
#   - In production, you'd list specific origins:
#     ["https://myapp.com", "https://staging.myapp.com"]
#
# allow_credentials: Allow cookies and Authorization headers
# allow_methods: Which HTTP methods are allowed (GET, POST, PUT, DELETE, etc.)
# allow_headers: Which request headers are allowed
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Mount API Routers
# ============================================================================
# Each router handles a group of related endpoints.
# The prefix in the router (e.g., "/auth") determines the URL prefix.
#
# After mounting, our API has these endpoints:
#   POST   /auth/register
#   POST   /auth/login
#   GET    /auth/me
#   GET    /projects
#   POST   /projects
#   GET    /projects/{id}
#   PUT    /projects/{id}
#   DELETE /projects/{id}
#   GET    /projects/{project_id}/notes
#   POST   /projects/{project_id}/notes
#   GET    /notes/{id}
#   PUT    /notes/{id}
#   DELETE /notes/{id}
# ============================================================================
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(notes.router)


# ============================================================================
# Root Endpoint — Health Check
# ============================================================================
@app.get("/")
def root():
    """
    Simple health check endpoint.
    Useful for monitoring tools to verify the API is running.
    """
    return {
        "app": settings.APP_NAME,
        "status": "running",
        "docs": "/docs",
    }
