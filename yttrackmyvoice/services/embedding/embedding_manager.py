from .embedding_service import EmbeddingService

class EmbeddingManager:
    def __init__(self, project):
        self.embedding_service = EmbeddingService(project)

    def embed_all_audio(self):
        self.embedding_service.embed_all_audio()