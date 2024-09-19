from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'

    project_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    project_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    urls = relationship("URL", back_populates="project", cascade="all, delete, delete-orphan")
    audio_files = relationship("AudioFile", back_populates="project", cascade="all, delete, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.project_id}, name='{self.project_name}', path='{self.project_path}', created_at={self.created_at})>"

class URL(Base):
    __tablename__ = 'urls'

    url_id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Changed from id to url_id
    project_id = Column(Integer, ForeignKey('projects.project_id'), nullable=False)
    url = Column(String(2083), nullable=False)  # 2083 is the maximum URL length

    # Relationships
    project = relationship("Project", back_populates="urls")
    audio_files = relationship("AudioFile", back_populates="url", cascade="all, delete, delete-orphan")

    def __repr__(self):
        return f"<URL(url_id={self.url_id}, project_id={self.project_id}, url='{self.url}')>"

class AudioFile(Base):
    __tablename__ = 'audio_files'

    audio_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.project_id'), nullable=False)
    url_id = Column(Integer, ForeignKey('urls.url_id'), nullable=False)  # Foreign Key updated to url_id
    url_name = Column(String(255), nullable=False)  # folder name inside project
    file_name = Column(String(255), nullable=False)  # file name inside url_name_folder
    audio_path = Column(String(500), nullable=False)  # full path to the audio file
    audio_folder_path = Column(String(500), nullable=False)  # full path to the audio folder
    duration_seconds = Column(DECIMAL(10, 2), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    project = relationship("Project", back_populates="audio_files")
    url = relationship("URL", back_populates="audio_files")
    segments = relationship("Segment", back_populates="audio_file", cascade="all, delete, delete-orphan")

    def __repr__(self):
        return (f"<AudioFile(id={self.audio_id}, project_id={self.project_id}, url_id={self.url_id}, "
                f"url_name='{self.url_name}', file_name='{self.file_name}', audio_path='{self.audio_path}', "
                f"duration_seconds={self.duration_seconds}, created_at={self.created_at})>")

class Segment(Base):
    __tablename__ = 'segments'

    segment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    audio_id = Column(Integer, ForeignKey('audio_files.audio_id', ondelete='CASCADE'), nullable=False)
    start_time = Column(DECIMAL(10, 2), nullable=False)  # in seconds
    end_time = Column(DECIMAL(10, 2), nullable=False)    # in seconds
    duration = Column(DECIMAL(10, 2), nullable=False)    # in seconds
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)      # audio_files.file_name + _ + (0,1,2,…n)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    audio_file = relationship("AudioFile", back_populates="segments")

    def __repr__(self):
        return (f"<Segment(id={self.segment_id}, audio_id={self.audio_id}, start_time={self.start_time}, "
                f"end_time={self.end_time}, duration={self.duration}, file_path='{self.file_path}', "
                f"file_name='{self.file_name}', created_at={self.created_at})>")
