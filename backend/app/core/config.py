"""
============================================================================
 core/config.py — Application Configuration
============================================================================

PURPOSE:
  This file loads and validates all configuration settings from environment
  variables (the .env file). It's the SINGLE SOURCE OF TRUTH for config.

WHY IT EXISTS:
  Instead of scattering os.getenv() calls throughout our code, we centralize
  all configuration here. This means:
  - If a setting changes, we update it in ONE place
  - We get automatic validation (e.g., if DATABASE_URL is missing, we get
    a clear error at startup, not a cryptic crash later)
  - Type safety: settings are properly typed (str, int, etc.)

HOW IT INTERACTS:
  - Used by core/database.py to get the DATABASE_URL
  - Used by core/security.py to get JWT settings
  - Used by main.py to configure the FastAPI app

CONCEPT — Pydantic BaseSettings:
  Pydantic is a library that validates data. BaseSettings is a special class
  that automatically reads values from environment variables or .env files.
  If a required variable is missing, it throws a helpful error.
============================================================================
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Each attribute becomes a setting. Pydantic reads from:
    1. Environment variables (highest priority)
    2. The .env file (if env_file is specified)
    3. Default values (lowest priority)
    """

    # ---- Database Settings ----
    # The connection string tells SQLAlchemy how to connect to the database.
    # We are using PostgreSQL exclusively for this project.
    DATABASE_URL: str = "postgresql://kw_user:kw_password@localhost:5432/knowledge_workspace"

    # ---- JWT (JSON Web Token) Settings ----
    # SECRET_KEY: A secret string used to sign tokens. In production,
    # this should be a long random string that only the server knows.
    JWT_SECRET_KEY: str = "your-super-secret-key-change-this-in-production"

    # ALGORITHM: The cryptographic algorithm for signing tokens.
    # HS256 (HMAC-SHA256) is the most common choice.
    JWT_ALGORITHM: str = "HS256"

    # How long a token stays valid (in minutes)
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ---- App Settings ----
    APP_NAME: str = "Knowledge Workspace"
    DEBUG: bool = True

    class Config:
        """
        Meta-configuration for the Settings class.

        env_file: tells Pydantic to look for a .env file for values
        env_file_encoding: ensures proper reading of the file
        """
        env_file = ".env"
        env_file_encoding = "utf-8"


# ============================================================================
# Create a single settings instance to be imported throughout the app.
# This pattern is called a "singleton" — we only need ONE settings object.
#
# Usage in other files:
#   from app.core.config import settings
#   print(settings.DATABASE_URL)
# ============================================================================
settings = Settings()
