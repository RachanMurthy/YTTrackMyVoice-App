from yttrackmyvoice.services.url.url_manager import URLManager
from yttrackmyvoice.services.audio.audio_manager import AudioManager
from yttrackmyvoice.services.embedding.embedding_manager import EmbeddingManager
from yttrackmyvoice.services.label.label_manager import LabelManager
from yttrackmyvoice.services.transcription.transcription_manager import TranscriptionManager
from yttrackmyvoice.services.playback.playback_manager import PlaybackManager
from yttrackmyvoice.services.project.project_manager import ProjectManager
class Yyt2:
    def __init__(self, project_name):
        """
        Initializes the Yyt2 class by setting up all necessary managers.
        
        Parameters:
        - project_name (str): The name of the project.
        """
        # Create or get the project upon initialization
        self.project_manager = ProjectManager(project_name)
        self.project = self.project_manager.initialize_project()

        self.url_manager = URLManager(self.project)
        self.audio_manager = AudioManager(self.project)
        self.embedding_manager = EmbeddingManager(self.project)
        self.transcription_manager = TranscriptionManager(self.project)
        self.label_manager = LabelManager()
        self.playback_manager = PlaybackManager()


    def add_urls(self, url_list):
        """
        Adds a list of YouTube URLs to the project.
        
        Parameters:
        - url_list (list): List of YouTube video URLs.
        """
        self.url_manager.add_urls(url_list)

    def add_playlists(self, playlist_list):
        """
        Adds a list of YouTube playlists to the project.
        
        Parameters:
        - playlist_list (list): List of YouTube playlist URLs.
        """
        self.url_manager.add_playlists(playlist_list)

    def download_all_audio(self):
        """
        Downloads all audio files associated with the project's URLs.
        """
        self.audio_manager.download_all_audio()

    def segment_all_audio(self, segment_length_ms=30 * 60 * 1000):
        """
        Segments all downloaded audio files into specified lengths.
        
        Parameters:
        - segment_length_ms (int): Length of each audio segment in milliseconds.
        """
        self.audio_manager.segment_all_audio(segment_length_ms)

    def embed_all_audio(self):
        """
        Generates embeddings for all audio segments.
        """
        self.embedding_manager.embed_all_audio()

    def cluster_and_label_embeddings(self, distance_threshold=1.0):
        """
        Clusters embeddings and assigns labels to speakers.
        
        Parameters:
        - distance_threshold (float): Threshold for clustering.
        """
        self.label_manager.cluster_and_label_embeddings(distance_threshold)

    def get_label_info(self, label_name):
        """
        Retrieves detailed information for a specific label.
        
        Parameters:
        - label_name (str): The name of the label.
        """
        self.label_manager.get_label_info(label_name)

    def list_labels(self):
        """
        Lists all existing labels in the project.
        """
        self.label_manager.list_labels()

    def update_label_name(self, old_label_name, new_label_name):
        """
        Updates the name of an existing label.
        
        Parameters:
        - old_label_name (str): The current name of the label.
        - new_label_name (str): The new name for the label.
        """
        self.label_manager.update_label_name(old_label_name, new_label_name)

    def segment_audio_using_embeddings_timestamps(self):
        """
        Segments audio based on embedding timestamps.
        """
        self.audio_manager.segment_audio_using_embeddings_timestamps()

    def play_segments_by_label(self, label_name):
        """
        Plays all audio segments associated with a specific label.
        
        Parameters:
        - label_name (str): The name of the label to play audio segments for.
        """
        self.playback_manager.play_segments_by_label(label_name)

    def retrieve_all_embeddings(self):
        """
        Retrieves all embeddings along with their associated labels.
        
        Returns:
        - embeddings (list): List of embedding vectors.
        - labels (list): List of dictionaries containing embedding metadata.
        """
        embeddings, labels = self.embedding_manager.retrieve_embeddings_for_all()
        return embeddings, labels

    def transcribe_final_segments(self):
        """
        Transcribes all final audio segments using the transcription service.
        """
        self.transcription_manager.transcribe_segments() 