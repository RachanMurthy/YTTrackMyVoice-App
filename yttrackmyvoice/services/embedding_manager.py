from yttrackmyvoice.embed_audio import Embedder
from yttrackmyvoice.database import SessionLocal
from yttrackmyvoice.database.models import AudioFile, Segment, Embedding

class EmbeddingManager:
    def __init__(self, project):
        self.project = project
        self.session = SessionLocal()
        self.embedder = Embedder()

    def embed_all_audio(self):
        try:
            self.session.add(self.project)
            self.session.refresh(self.project)

            audio_files = self.session.query(AudioFile).filter_by(project_id=self.project.project_id).all()

            if not audio_files:
                print(f"No audio files found for project '{self.project.project_name}'. Please add audio files first.")
                return

            for audio_file in audio_files:
                segment_files = self.session.query(Segment).filter_by(audio_id=audio_file.audio_id).all()
                for segment_file in segment_files:
                    segment_id = segment_file.segment_id
                    segment_file_path = segment_file.file_path
                    segment_embeddings = self.session.query(Embedding).filter_by(segment_id=segment_id).first()

                    if segment_embeddings:
                        print(f"Embeddings already exist for '{segment_file_path}'")
                        continue

                    self.embedder.store_embedding_and_timestamp(segment_id)
        finally:
            self.session.close() 