from yttrackmyvoice.database import SessionLocal
from yttrackmyvoice.database.models import AudioFile, Segment, Embedding
from yttrackmyvoice.services.embedding.embedder import Embedder

class EmbeddingService:
    def __init__(self, project):
        self.project = project

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
                print(f"No audio files found for project '{self.project.project_name}'. Please add audio files first.")
                return

            embedder = Embedder()  # Create an instance of the Embedder class

            for audio_file in audio_files:
                segment_files = session.query(Segment).filter_by(audio_id=audio_file.audio_id).all()
                for segment_file in segment_files:
                    segment_id = segment_file.segment_id
                    segment_file_path = segment_file.file_path
                    segment_embeddings = session.query(Embedding).filter_by(segment_id=segment_id).first()

                    if segment_embeddings:
                        print(f"Embeddings already exist for '{segment_file_path}'")
                        continue

                    embedder.store_embedding_and_timestamp(segment_id)
        finally:
            session.close()
