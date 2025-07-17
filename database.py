from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment-based configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./customers.db"  # Default to SQLite for development
)

# Optimized engine with connection pooling
engine_kwargs = {
    "echo": False,  # Set to True only for debugging
}

# Add connection pooling for PostgreSQL/MySQL
if DATABASE_URL.startswith(("postgresql://", "mysql://")):
    engine_kwargs.update({
        "poolclass": QueuePool,
        "pool_size": 20,                 # Number of connections to maintain
        "max_overflow": 30,              # Additional connections when pool is full
        "pool_pre_ping": True,           # Verify connections before use
        "pool_recycle": 3600,            # Recycle connections every hour
        "connect_args": {
            "options": "-c statement_timeout=30000"  # 30 second timeout for PostgreSQL
        }
    })
elif DATABASE_URL.startswith("sqlite://"):
    # SQLite specific optimizations
    engine_kwargs.update({
        "connect_args": {
            "check_same_thread": False,
            "timeout": 30
        }
    })

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False        # Prevent lazy loading issues
)

Base = declarative_base()

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()