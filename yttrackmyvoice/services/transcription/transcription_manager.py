from .transcript_service import TranscriptService

class TranscriptionManager:
    def __init__(self, project):
        self.project = project
        self.transcript_service = TranscriptService(self.project)

    def transcribe_segments(self):
        self.transcript_service.transcribe_final_segments()
