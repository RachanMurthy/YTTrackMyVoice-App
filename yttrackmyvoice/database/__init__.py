from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base  # Import your Base class

# Create engine for SQLite database
engine = create_engine('sqlite:///example.db', echo=False)

# Create all tables automatically when the package is imported
Base.metadata.create_all(engine)

# Optional: Create a configured "SessionLocal" class, used for each session
SessionLocal = sessionmaker(bind=engine)


