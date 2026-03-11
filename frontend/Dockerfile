# ============================================================================
# Frontend Dockerfile
# ============================================================================
#
# PURPOSE:
#   This file builds the Docker Image for our React (Vite) frontend.
#
# HOW IT WORKS:
#   Just like the backend, it sets up an environment, installs dependencies,
#   and tells Docker how to run the development server.
# ============================================================================

# 1. Base Image: Start with a lightweight version of Linux that has Node.js v20 installed.
FROM node:20-slim

# 2. Enable pnpm: Node comes with a tool called Corepack that manages package managers.
# We enable it and tell it to use 'pnpm', which is faster and more disk-efficient than npm.
RUN corepack enable && corepack prepare pnpm@latest --activate

# 3. Work Directory: Set /app as the folder where our code will live inside the container.
WORKDIR /app

# 4. Copy Dependencies: Copy our package.json and lockfile FIRST to utilize Docker caching.
COPY package.json pnpm-lock.yaml ./

# 5. Install Dependencies: Run pnpm to install all the React/Tailwind/Zustand packages.
RUN pnpm install

# 6. Copy Source Code: Copy all our React components, styles, and config files.
COPY . .

# 7. Expose Port: Document that Vite runs on port 5173.
EXPOSE 5173

# 8. Command: Run the Vite development server.
# The '--host 0.0.0.0' binding is crucial. Vite normally only listens on 'localhost' inside
# its own container. By setting it to 0.0.0.0, it allows your host computer's browser
# to access the server running inside the isolated Docker container.
CMD ["pnpm", "run", "dev", "--host", "0.0.0.0"]

