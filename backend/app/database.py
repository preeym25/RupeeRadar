"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool

from app.settings import get_settings

settings = get_settings()

# Create database engine with connection pooling
db_url = settings.database_url
is_sqlite = db_url.startswith("sqlite")

connect_args = {}
if is_sqlite:
    connect_args["check_same_thread"] = False
else:
    connect_args.update({
        'connect_timeout': 10,
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5
    })

engine = create_engine(
    db_url,
    poolclass=QueuePool if not is_sqlite else None,
    pool_size=10 if not is_sqlite else 5,
    max_overflow=20 if not is_sqlite else 10,
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Test connection before using
    echo=False,
    connect_args=connect_args
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables."""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all tables - use with caution in production!"""
    Base.metadata.drop_all(bind=engine)
