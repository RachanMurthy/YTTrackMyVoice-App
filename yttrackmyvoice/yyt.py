import os
from sqlalchemy.exc import SQLAlchemyError
from .utils import (
    create_directory_if_not_exists,
    split_audio_file,
    get_key,
    extract_video_urls_from_playlist
)
from .database import SessionLocal
from .database.models import Project, URL, AudioFile, Segment, Embedding, EmbeddingTimestamp
from pytubefix import YouTube
from .embedder import store_embedding_and_timestamp
import numpy as np
from .download_audio import Downloader  # Import the Downloader class


class Yyt:
    def __init__(self, project_name):
        """
        Initializes the Yyt class by creating or retrieving a project.

        Parameters:
        - project_name: The name of the project to create or retrieve.
        """
        # Ensure the data directory exists
        create_directory_if_not_exists(get_key('DATA_DIRECTORY'))

        # Replace spaces in the project name with underscores
        self.project_name = project_name.replace(" ", "_")
        self.project = None  # Will hold the Project instance

        # Create or get the project upon initialization
        self._create_or_get_project()

    def _create_or_get_project(self):
        """
        Create a new project if it doesn't exist, or continue with the existing project.
        This method is called during initialization.
        """
        session = SessionLocal()
        try:
            # Check if the project already exists
            project = session.query(Project).filter_by(project_name=self.project_name).first()

            if project:
                print(f"\nContinuing with the existing project: {project.project_name}\n")
                self.project = project
            else:
                # Create a new project
                project_path = os.path.join(get_key('DATA_DIRECTORY'), self.project_name)
                new_project = Project(
                    project_name=self.project_name,
                    description="",
                    project_path=project_path
                )
                create_directory_if_not_exists(project_path)
                print(f"Project Folder ready: {project_path}")

                session.add(new_project)
                session.commit()
                session.refresh(new_project)
                self.project = new_project
                print(f"\nGreat! A new project '{new_project.project_name}' has been created with ID {new_project.project_id}.\n")
        except Exception as e:
            session.rollback()
            print(f"\nAn error occurred during project creation: {str(e)}")
            # Optionally, re-raise the exception or handle it appropriately
        finally:
            session.close()

    def add_urls(self, url_list):
        """
        Add new URLs to the project and display existing ones.

        Parameters:
        - url_list: A list of YouTube URLs to add to the project.
        """
        session = SessionLocal()
        try:
            # Ensure the project is attached to the session
            session.add(self.project)
            session.refresh(self.project)

            # Display existing URLs
            urls = session.query(URL).filter_by(project_id=self.project.project_id).all()
            if urls:
                print(f"The project '{self.project_name}' contains the following URLs:\n")
                for url_entry in urls:
                    print(f"- {url_entry.url}")
            else:
                print(f"The project '{self.project_name}' has no saved URLs.")

            # Add new URLs
            for url in url_list:
                existing_url = session.query(URL).filter_by(url=url, project_id=self.project.project_id).first()
                if existing_url:
                    print(f"URL already exists: {url}")
                    continue

                try:
                    yt = YouTube(url)
                except Exception as e:
                    print(f"Failed to process the YouTube URL '{url}'. Error details: {e}.")
                    continue

                new_url = URL(
                    project_id=self.project.project_id,
                    url=url,
                    title=yt.title,
                    author=yt.author,
                    views=yt.views,
                    description=yt.description
                )
                session.add(new_url)
                print(f"Added new URL: {url}")

            session.commit()
            print(f"URLs successfully updated for project '{self.project_name}'.")
        except Exception as e:
            session.rollback()
            print(f"An error occurred while managing URLs: {e}")
        finally:
            session.close()

    def add_playlists(self, playlist_list):
        """
        Extracts video URLs from YouTube playlists and adds them to the project.

        Parameters:
        - playlist_list: A list of playlist URLs.
        """
        playlist_urls = []
        for playlist in playlist_list:
            playlist_urls.extend(extract_video_urls_from_playlist(playlist))

        self.add_urls(playlist_urls)

    def download_all_audio(self):
        """
        Downloads audio for all URLs associated with the project.
        """
        session = SessionLocal()
        try:
            # Ensure the project is attached to the session
            session.add(self.project)
            session.refresh(self.project)

            urls = session.query(URL).filter_by(project_id=self.project.project_id).all()

            if not urls:
                print(f"No URLs found for project '{self.project_name}'. Please add URLs first.")
                return

            downloader = Downloader()

            for url_record in urls:
                url_id = url_record.url_id
                downloader.download_youtube_audio(url_id)
        finally:
            session.close()

    def segment_all_audio(self, segment_length_ms=2 * 60 * 1000):
        """
        Splits audio files associated with the project into segments.

        Parameters:
        - segment_length_ms: The length of each segment in milliseconds.
        """
        session = SessionLocal()
        try:
            # Ensure the project is attached to the session
            session.add(self.project)
            session.refresh(self.project)

            audio_files = session.query(AudioFile).filter_by(project_id=self.project.project_id).all()

            if not audio_files:
                print(f"No audio files found for project '{self.project_name}'. Please add audio files first.")
                return

            for audio_file in audio_files:
                audio_file_id = audio_file.audio_id
                audio_file_path = audio_file.audio_path
                audio_segments = session.query(Segment).filter_by(audio_id=audio_file_id).first()

                if audio_segments:
                    print(f"Audio segments already exist for '{audio_file_path}'")
                    continue

                split_audio_file(audio_file_id, segment_length_ms)
        finally:
            session.close()

    def embed_all_audio(self):
        """
        Generates embeddings for all audio segments associated with the project.
        """
        session = SessionLocal()
        try:
            # Ensure the project is attached to the session
            session.add(self.project)
            session.refresh(self.project)

            audio_files = session.query(AudioFile).filter_by(project_id=self.project.project_id).all()

            if not audio_files:
                print(f"No audio files found for project '{self.project_name}'. Please add audio files first.")
                return

            for audio_file in audio_files:
                segment_files = session.query(Segment).filter_by(audio_id=audio_file.audio_id).all()
                for segment_file in segment_files:
                    segment_id = segment_file.segment_id
                    segment_file_path = segment_file.file_path
                    segment_embeddings = session.query(Embedding).filter_by(segment_id=segment_id).first()

                    if segment_embeddings:
                        print(f"Embeddings already exist for '{segment_file_path}'")
                        continue

                    store_embedding_and_timestamp(segment_id)
        finally:
            session.close()

    @staticmethod
    def retrieve_all_embeddings():
        """
        Retrieves all embeddings and their corresponding timestamps from the database.

        Returns:
        - embeddings_list (List[np.ndarray]): A list of embedding vectors.
        - labels_list (List[Dict]): A list of dictionaries containing metadata.
        """
        session = SessionLocal()
        try:
            print("Retrieving all embeddings from the database.")

            embeddings = session.query(Embedding).all()
            if not embeddings:
                print("No embeddings found in the database.")
                return [], []

            embeddings_list = []
            labels_list = []

            for embedding in embeddings:
                embedding_vector = np.frombuffer(embedding.vector, dtype=np.float32)

                timestamps = session.query(EmbeddingTimestamp).filter_by(embedding_id=embedding.embedding_id).all()

                timestamp_list = []
                for ts in timestamps:
                    timestamp_info = { 
                        'start_time': ts.start_time,
                        'end_time': ts.end_time,
                        'created_at': ts.created_at
                    }
                    timestamp_list.append(timestamp_info)

                embedding_info = {
                    'embedding_id': embedding.embedding_id,
                    'segment_id': embedding.segment_id,
                    'timestamps': timestamp_list,
                    'created_at': embedding.created_at
                }

                embeddings_list.append(embedding_vector)
                labels_list.append(embedding_info)

            print(f"Total embeddings retrieved: {len(embeddings_list)}")
            return embeddings_list, labels_list
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            return [], []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return [], []
        finally:
            session.close()
