# ============================================================================
# Backend Dockerfile
# ============================================================================
#
# PURPOSE:
#   This file provides the instructions to build a Docker "Image" for our
#   Python FastAPI backend. An image is like a snapshot of a computer that
#   has our code and all the tools needed to run it.
#
# HOW IT WORKS:
#   Docker reads these instructions from top to bottom. Each instruction
#   creates a "layer." Docker caches these layers to make future builds faster.
# ============================================================================

# 1. Base Image: Start with a lightweight version of Linux that has Python 3.12 installed.
FROM python:3.12-slim

# 2. Install 'uv': uv is an extremely fast Python package installer written in Rust.
# Instead of downloading it with curl/apt, we copy the pre-compiled binary
# directly from its official image.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Work Directory: Inside the container, set /app as our working folder.
# All subsequent COPY and RUN commands will happen inside this folder.
WORKDIR /app

# 4. Copy Dependencies: We copy our dependency list FIRST.
# Why? Docker caches layers. If we copy the whole source code first,
# Docker would reinstall dependencies every time we change a single line of code.
# By copying only these files first, Docker caches the installation step unless these files change.
COPY pyproject.toml uv.lock ./

# 5. Install Dependencies: Run 'uv' to install everything defined in our lock file.
# --frozen ensures it installs exactly what's in uv.lock, without trying to update anything.
RUN uv sync --frozen

# 6. Copy Source Code: Now we copy the rest of our application code into the container.
COPY . .

# 7. Expose Port: Explain to Docker that this container listens on port 8000.
# (Note: This is just documentation; port mapping is actually handled by docker-compose)
EXPOSE 8000

# 8. Command: The default command to run when the container starts.
# We tell uvicorn to listen on '0.0.0.0' (all network interfaces) so it can accept 
# connections from outside the container (like from our frontend container).
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

