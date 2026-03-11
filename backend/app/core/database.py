"""
============================================================================
 core/database.py — Database Connection & Session Management
============================================================================

PURPOSE:
  This file sets up the connection between our Python code and the database.
  It creates the "engine" (the connection pool) and the "session" (how we
  talk to the database in each request).
  
  We use SQLite for development (simple file-based DB, no setup needed).
  For production, you'd switch to PostgreSQL by changing DATABASE_URL.

WHY IT EXISTS:
  Every web request that needs data will need a database session. This file
  provides a reusable way to create and manage those sessions.

HOW IT INTERACTS:
  - Reads DATABASE_URL from core/config.py
  - Provides `Base` class to models/ (each model inherits from it)
  - Provides `get_db()` to dependencies/ (each API route gets a session)

CONCEPT — SQLAlchemy ORM:
  SQLAlchemy is an ORM (Object-Relational Mapper). Instead of writing SQL:
    SELECT * FROM users WHERE id = 1
  We write Python:
    db.query(User).filter(User.id == 1).first()

  The ORM translates Python objects to SQL queries and back. This gives us:
  - Type safety and editor autocomplete
  - Protection against SQL injection attacks
  - Database-agnostic code (easy to switch from PostgreSQL to MySQL)

CONCEPT — Engine vs Session:
  Engine: The connection POOL — manages multiple connections to the database.
          Think of it as the "highway" to the database.
  Session: A single "conversation" with the database for one request.
          Think of it as one "car" on that highway.
============================================================================
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
from app.core.config import settings

# ============================================================================
# Create the SQLAlchemy Engine
# ============================================================================
# The engine manages a POOL of database connections.
# When our app starts, it doesn't open a connection immediately — it waits
# until the first query, then creates connections as needed.
#
# SQLite special handling:
#   1. check_same_thread=False: SQLite only allows one thread by default,
#      but FastAPI uses multiple threads. This flag is safe because
#      SQLAlchemy manages connections properly.
#   2. Absolute path: We resolve the relative DB path to an absolute one
#      so the file is always created in the backend/ directory.
# ============================================================================
connect_args = {}
database_url = settings.DATABASE_URL

engine = create_engine(
    database_url,
    connect_args=connect_args,
)

# ============================================================================
# Create a Session Factory
# ============================================================================
# SessionLocal is not a session itself — it's a FACTORY that creates sessions.
# Each time we call SessionLocal(), we get a new session.
#
# autocommit=False: We control when changes are saved (explicit commits)
# autoflush=False: We control when Python objects sync to the database
#
# These settings give us full control over when data is read/written,
# which is important for handling errors properly (we can rollback).
# ============================================================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,  # Connect this session factory to our engine
)

# ============================================================================
# Create the Base Class for Models
# ============================================================================
# Every database model (User, Project, Note) will inherit from this Base.
# It gives them the ability to map Python classes to database tables.
#
# When we later call Base.metadata.create_all(engine), SQLAlchemy reads
# all classes that inherit from Base and creates their tables in the database.
# ============================================================================
Base = declarative_base()
