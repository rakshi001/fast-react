"""
============================================================================
 dependencies/database.py — Database Session Dependency
============================================================================

PURPOSE:
  Provides a database session to each API route that needs one.

WHY IT EXISTS:
  Every API route that touches the database needs a "session" — a
  connection to talk to PostgreSQL. This dependency:
  1. Creates a session at the start of a request
  2. Makes it available to the route handler
  3. Automatically closes it when the request is done

HOW IT INTERACTS:
  - Used by API routes via FastAPI's Depends() system
  - Creates sessions from the factory in core/database.py

CONCEPT — FastAPI Dependencies:
  Dependencies are functions that run BEFORE your route handler.
  They prepare things your route needs (database sessions, current user,
  etc.) and inject them as parameters.

  Example usage in a route:
    @router.get("/items")
    def get_items(db: Session = Depends(get_db)):
        # db is already created and will be closed automatically
        return db.query(Item).all()

CONCEPT — yield (Generator Pattern):
  The `yield` keyword makes this a "generator" function.
  - Code BEFORE yield runs at request START (create session)
  - Code AFTER yield runs at request END (close session via finally)
  - This pattern is called "dependency with cleanup"
============================================================================
"""

from app.core.database import SessionLocal
from sqlalchemy.orm import Session


def get_db():
    """
    Yields a database session for a single request.

    Input:  None
    Output: Yields a SQLAlchemy Session

    How it works:
    1. SessionLocal() creates a new database session
    2. yield db — temporarily returns the session to the route
    3. finally: db.close() — runs after the route finishes,
       whether it succeeded or threw an error

    The `finally` block is crucial: without it, a crash in the
    route would leave the database connection open (a "leak"),
    eventually exhausting all available connections.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
