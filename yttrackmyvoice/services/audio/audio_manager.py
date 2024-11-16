from .download_service import AudioDownloadService
from .segment_service import AudioSegmentService

class AudioManager:
    def __init__(self, project):
        self.download_service = AudioDownloadService(project)
        self.segment_service = AudioSegmentService(project)

    def download_all_audio(self):
        self.download_service.download_all_audio()

    def segment_all_audio(self, segment_length_ms):
        self.segment_service.segment_all_audio(segment_length_ms)

    def segment_audio_using_embeddings_timestamps(self):
        self.segment_service.segment_audio_using_embeddings_timestamps() 