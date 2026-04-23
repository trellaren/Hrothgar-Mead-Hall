# Database configuration and initialization using SQLAlchemy + SQLite
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database path - store in the web directory
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mead_hall.db')
DATABASE_URL = f'sqlite:///{DB_PATH}'

# Create engine with JSON compatibility settings
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class System(Base):
    """Database model for clustering systems."""
    __tablename__ = 'systems'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default='active')
    nodes = Column(String(1024), default='[]')  # JSON string stored as text
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert system to dictionary."""
        import json
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'nodes': json.loads(self.nodes) if self.nodes else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data):
        """Create system from dictionary."""
        import json
        return cls(
            name=data.get('name', 'New System'),
            status=data.get('status', 'active'),
            nodes=json.dumps(data.get('nodes', [])),
        )

    @classmethod
    def from_create_dict(cls, data):
        """Create system from creation data (without id)."""
        import json
        return cls(
            name=data.get('name', 'New System'),
            status=data.get('status', 'active'),
            nodes=json.dumps(data.get('nodes', [])),
        )


def init_db():
    """Initialize the database, creating all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """Get a database session (generator-free version for simple usage)."""
    return SessionLocal()