from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

# Creating the declarative base for SQLAlchemy models
Base = declarative_base()

# Model for the Project table
class Project(Base):
    __tablename__ = 'projects'

    # Primary key and basic fields
    project_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_name = Column(String(255), unique=True, nullable=False)  # Each project must have a unique name
    description = Column(Text, nullable=True)  # Optional project description
    project_path = Column(String(255), nullable=True)  # Optional file path for project-related files
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # Automatically set to the current UTC time


    # One-to-many relationship with the URL and AudioFile tables
    urls = relationship("URL", back_populates="project", cascade="all, delete, delete-orphan")  # Cascade delete ensures associated URLs are deleted when a project is deleted
    audio_files = relationship("AudioFile", back_populates="project", cascade="all, delete, delete-orphan")  # Same cascade behavior for audio files

    def __repr__(self):
        # Useful for debugging and understanding object contents
        return f"<Project(id={self.project_id}, name='{self.project_name}', path='{self.project_path}', created_at={self.created_at})>"

# Model for the URL table
class URL(Base):
    __tablename__ = 'urls'

    # Primary key and foreign key for project association
    url_id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Changed from 'id' to 'url_id' for clarity
    project_id = Column(Integer, ForeignKey('projects.project_id'), nullable=False)  # Foreign key linking URLs to a project
    url = Column(String(2083), nullable=False)  # Storing the actual URL, 2083 is the maximum URL length

    # Additional metadata for the URL
    title = Column(String(255), nullable=True)  # Title of the video/URL
    author = Column(String(255), nullable=True)  # Author or channel name of the video
    views = Column(Integer, nullable=True)  # Number of views for the video
    description = Column(Text, nullable=True)  # Description of the video


    # One-to-many relationship with the AudioFile table and the Project table
    project = relationship("Project", back_populates="urls")  # Many URLs can belong to one project
    audio_files = relationship("AudioFile", back_populates="url", cascade="all, delete, delete-orphan")  # Cascade delete to remove audio files when a URL is deleted

    def __repr__(self):
        # Debug representation for the URL model
        return (f"<URL(url_id={self.url_id}, project_id={self.project_id}, url='{self.url}', "
                f"title='{self.title}', author='{self.author}', views={self.views})>")
    
# Model for the AudioFile table
class AudioFile(Base):
    __tablename__ = 'audio_files'

    # Primary key and foreign keys for project and URL association
    audio_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    audio_path = Column(String(500), nullable=False)  # Full file path to the audio file
    audio_folder_path = Column(String(500), nullable=False)  # Folder path containing the audio file
    
    # Foreign keys linking audio to a project and a URL
    project_id = Column(Integer, ForeignKey('projects.project_id'), nullable=False)
    url_id = Column(Integer, ForeignKey('urls.url_id'), nullable=False)  # Foreign key linking to the URL model

    # Duration of the audio file
    duration_seconds = Column(DECIMAL(10, 2), nullable=True)  # Storing the duration in seconds, allowing decimals
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # Automatically set to the current UTC time


    # Relationships with the Project and URL tables
    project = relationship("Project", back_populates="audio_files")  # Many audio files can belong to one project
    url = relationship("URL", back_populates="audio_files")  # Many audio files can belong to one URL
    
    # One-to-many relationship with the Segment table
    segments = relationship("Segment", back_populates="audio_file", cascade="all, delete, delete-orphan")  # Cascade delete to remove segments when an audio file is deleted

    def __repr__(self):
        # Debugging representation for the AudioFile model
        return (f"<AudioFile(id={self.audio_id}, project_id={self.project_id}, url_id={self.url_id}, "
                f"audio_path='{self.audio_path}', duration_seconds={self.duration_seconds}, created_at={self.created_at})>")

# Model for the Segment table
class Segment(Base):
    __tablename__ = 'segments'

    # Primary key and foreign key linking to the AudioFile table
    segment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    audio_id = Column(Integer, ForeignKey('audio_files.audio_id', ondelete='CASCADE'), nullable=False)  # Link to the audio file, with cascade delete
    start_time = Column(DECIMAL(10, 2), nullable=False)  # Start time of the segment, in seconds
    end_time = Column(DECIMAL(10, 2), nullable=False)    # End time of the segment, in seconds
    duration = Column(DECIMAL(10, 2), nullable=False)    # Duration of the segment, in seconds
    file_path = Column(String(500), nullable=False)      # Full file path to the segmented audio file
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # Automatically set to the current UTC time

    # Relationships
    audio_file = relationship("AudioFile", back_populates="segments")  # Many segments can belong to one audio file
    embeddings = relationship("Embedding", back_populates="segment", cascade="all, delete, delete-orphan")  # One segment has many embeddings

    def __repr__(self):
        return (f"<Segment(id={self.segment_id}, audio_id={self.audio_id}, "
                f"start_time={self.start_time}, end_time={self.end_time}, "
                f"duration={self.duration}, file_path='{self.file_path}', "
                f"created_at={self.created_at})>")

# Add a 'cluster_label' field to store cluster/group ID
class Embedding(Base):
    __tablename__ = 'embeddings'

    embedding_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    segment_id = Column(Integer, ForeignKey('segments.segment_id', ondelete='CASCADE'), nullable=False)  # Reference to Segment model
    vector = Column(LargeBinary, nullable=False)  # Embedding vector stored as binary data
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # Timestamp of embedding creation

    # Relationships
    segment = relationship("Segment", back_populates="embeddings")  # Each embedding belongs to one segment

    def __repr__(self):
        return (f"<Embedding(id={self.embedding_id}, segment_id={self.segment_id}, "
                f"created_at={self.created_at})>")