# Knowledge Workspace

A full-stack productivity application where users can organize their notes into projects.

## Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Frontend   | React, TypeScript, Vite, Zustand, shadcn/ui |
| Backend    | Python, FastAPI, SQLAlchemy, Pydantic |
| Database   | PostgreSQL (via Docker)           |

## Architecture

```
User → React UI → Zustand Store → Axios API Client
         ↕ HTTP (REST)
FastAPI Routes → Pydantic Validation → Service Layer → Repository Layer → SQLAlchemy → PostgreSQL
```
## Getting Started

### Prerequisites
- Node.js 18+, pnpm
- Python 3.10+, uv
- Docker & Docker Compose

### Running the Application

This entire full-stack application is completely dockerized. You do not need to start the frontend, backend, or database separately.

```bash
# From the fastReact root directory:
docker compose up --build
```

**Services will be available at:**
- 🎨 **Frontend (React):** http://localhost:5173
- ⚙️ **Backend API:** http://localhost:8000
- 📖 **API Interactive Docs (Swagger):** http://localhost:8000/docs
- 🗄️ **Database Manager (Adminer):** http://localhost:8080 (System: PostgreSQL, Server: db, User: kw_user, Pass: kw_password)

## Project Structure

```
fastReact/
├── frontend/          # React + TypeScript + Vite application
├── backend/           # FastAPI + Python application
├── docker-compose.yml # Orchestrates Frontend, Backend, PostgreSQL, and Adminer
└── README.md
```
