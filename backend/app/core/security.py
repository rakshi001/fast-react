"""
============================================================================
 core/security.py — Password Hashing & JWT Token Management
============================================================================

PURPOSE:
  This file handles two critical security operations:
  1. Password hashing — storing passwords safely (never in plain text!)
  2. JWT tokens — creating and verifying login tokens

WHY IT EXISTS:
  Security logic is centralized here so that:
  - We use the SAME hashing algorithm everywhere
  - Token creation/verification logic is in ONE place
  - Other files (services, dependencies) just call simple functions

HOW IT INTERACTS:
  - Used by services/auth_service.py to hash passwords during registration
  - Used by services/auth_service.py to verify passwords during login
  - Used by services/auth_service.py to create JWT tokens after login
  - Used by dependencies/auth.py to verify tokens on protected routes

CONCEPT — Password Hashing:
  We NEVER store passwords as plain text. Instead, we "hash" them — a
  one-way mathematical transformation. "password123" becomes something like
  "$2b$12$LJ3m4ys...". You can't reverse a hash back to the original
  password, but you CAN check if a given password matches the hash.

CONCEPT — JWT (JSON Web Token):
  After login, the server gives the client a "token" — a signed string
  that contains the user's identity. On each subsequent request, the client
  sends this token, and the server verifies it was signed by us.
  
  Token structure: header.payload.signature
  - Header: algorithm used
  - Payload: user data (like user_id) + expiration time
  - Signature: proves the token wasn't tampered with
============================================================================
"""

from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt, JWTError
from app.core.config import settings


# ============================================================================
# Password Hashing with bcrypt
# ============================================================================
# bcrypt is the industry standard for password hashing because:
# - It's intentionally SLOW (making brute-force attacks impractical)
# - It includes a "salt" (random data added to each password before hashing)
# - It's adaptive (you can increase the work factor as hardware gets faster)
#
# We use the bcrypt library directly (rather than passlib) for better
# compatibility with modern Python versions.
# ============================================================================


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Input:  password (str) — the user's plain-text password
    Output: str — the hashed password (e.g., "$2b$12$...")

    How it works:
    1. gensalt() creates a random salt (unique per password)
    2. hashpw() combines the password + salt and hashes them
    3. We decode from bytes to string for database storage

    Why: We call this during user registration to store the hashed version.
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check if a plain-text password matches a stored hash.

    Input:  plain_password (str) — what the user typed in the login form
            hashed_password (str) — what's stored in our database
    Output: bool — True if they match, False otherwise

    Why: We call this during login to verify the user's credentials.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token.

    Input:  data (dict) — payload to encode in the token
            Typically: {"sub": user_id} where "sub" means "subject"
    Output: str — the encoded JWT token string

    How it works:
    1. We copy the input data (to avoid mutating the original)
    2. We add an expiration time (so tokens don't last forever)
    3. We sign the token with our SECRET_KEY
    4. We return the token string

    The client will send this token in the Authorization header:
      Authorization: Bearer <token>
    """
    to_encode = data.copy()

    # Set expiration time
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    # Sign and return the token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def verify_access_token(token: str) -> dict | None:
    """
    Verify and decode a JWT access token.

    Input:  token (str) — the JWT token string from the client
    Output: dict — the decoded payload (e.g., {"sub": 1, "exp": ...})
            None — if the token is invalid, expired, or tampered with

    Why: We call this on every protected route to verify the user's identity.
    The dependencies/auth.py file uses this to extract the current user.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        # Token is invalid, expired, or signature doesn't match
        return None
