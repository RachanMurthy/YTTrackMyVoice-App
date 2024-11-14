import os
from yttrackmyvoice.database import SessionLocal
from yttrackmyvoice.database.models import Project
from yttrackmyvoice.utils import create_directory_if_not_exists, get_key
from services.url_manager import URLManager
from services.audio_manager import AudioManager
from services.segment_manager import SegmentManager
from services.embedding_manager import EmbeddingManager
from services.label_manager import LabelManager
from services.transcription_manager import TranscriptionManager
from services.playback_manager import PlaybackManager

class Yyt:
    def __init__(self, project_name):
        """
        Initializes the Yyt class by creating or retrieving a project.
        
        Parameters:
        - project_name: The name of the project to create or retrieve.
        """
        create_directory_if_not_exists(get_key('DATA_DIRECTORY'))

        self.project_name = project_name.replace(" ", "_")
        self.project = None

        self._create_or_get_project()

        # Initialize service managers
        self.url_manager = URLManager(self.project)
        self.audio_manager = AudioManager(self.project)
        self.segment_manager = SegmentManager(self.project)
        self.embedding_manager = EmbeddingManager(self.project)
        self.label_manager = LabelManager()
        self.transcription_manager = TranscriptionManager(self.project)
        self.playback_manager = PlaybackManager(self.project)

    def _create_or_get_project(self):
        """
        Create a new project if it doesn't exist, or continue with the existing project.
        """
        session = SessionLocal()
        try:
            project = session.query(Project).filter_by(project_name=self.project_name).first()

            if project:
                print(f"\nContinuing with the existing project: {project.project_name}\n")
                self.project = project
            else:
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
        finally:
            session.close()

    # URL Management
    def add_urls(self, url_list):
        """
        Add new URLs to the project.
        """
        self.url_manager.add_urls(url_list)

    def add_playlists(self, playlist_list):
        """
        Add playlists to the project.
        """
        self.url_manager.add_playlists(playlist_list)

    # Audio Management
    def download_all_audio(self):
        """
        Download all audio files associated with the project.
        """
        self.audio_manager.download_all_audio()

    def segment_all_audio(self, segment_length_ms=2 * 60 * 1000):
        """
        Segment all audio files into smaller segments.
        
        Parameters:
        - segment_length_ms: Length of each segment in milliseconds.
        """
        self.audio_manager.segment_all_audio(segment_length_ms)

    # Embedding Management
    def embed_all_audio(self):
        """
        Generate embeddings for all audio segments.
        """
        self.embedding_manager.embed_all_audio()

    # Label Management
    def cluster_and_label_embeddings(self, distance_threshold=1):
        """
        Cluster and label embeddings.
        
        Parameters:
        - distance_threshold: The distance threshold for clustering.
        """
        self.label_manager.cluster_and_label_embeddings(distance_threshold)

    def list_labels(self):
        """
        List all existing labels.
        """
        self.label_manager.list_labels()

    def update_label_name(self, old_label_name, new_label_name):
        """
        Update the name of a label.
        """
        self.label_manager.update_label_name(old_label_name, new_label_name)

    def get_label_info(self, label_name):
        """
        Get detailed information about a label.
        """
        self.label_manager.get_label_info(label_name)

    # Transcription Management
    def transcribe_final_segments(self):
        """
        Transcribe all final audio segments.
        """
        self.transcription_manager.transcribe_final_segments()

    # Playback Management
    def play_segments_by_label(self, label_name):
        """
        Play all audio segments associated with a specific label.
        """
        self.playback_manager.play_segments_by_label(label_name) 