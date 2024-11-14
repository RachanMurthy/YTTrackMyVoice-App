import os
from yttrackmyvoice.utils import create_directory_if_not_exists
from yttrackmyvoice.audio_segmenter import Segmenter
from yttrackmyvoice.database import SessionLocal
from yttrackmyvoice.database.models import AudioFile, Segment, Embedding, EmbeddingTimestamp

class SegmentManager:
    def __init__(self, project):
        self.project = project
        self.session = SessionLocal()
        self.segmenter = Segmenter()

    def segment_all_audio(self, segment_length_ms=2 * 60 * 1000):
        try:
            self.session.add(self.project)
            self.session.refresh(self.project)

            audio_files = self.session.query(AudioFile).filter_by(project_id=self.project.project_id).all()

            if not audio_files:
                print(f"No audio files found for project '{self.project.project_name}'. Please add audio files first.")
                return

            for audio_file in audio_files:
                audio_file_id = audio_file.audio_id
                audio_file_path = audio_file.audio_path
                audio_segments = self.session.query(Segment).filter_by(audio_id=audio_file_id).first()

                if audio_segments:
                    print(f"Audio segments already exist for '{audio_file_path}'")
                    continue

                self.segmenter.split_audio_file(audio_file_id, segment_length_ms)
        finally:
            self.session.close()

    def segment_audio_using_embeddings_timestamps(self):
        try:
            print("Starting audio segmentation using EmbeddingTimestamps.")

            embedding_timestamps = self.session.query(EmbeddingTimestamp).all()
            if not embedding_timestamps:
                print("No EmbeddingTimestamps found in the database.")
                return

            segments_dir = os.path.join(self.project.project_path, "FinalSegments")
            create_directory_if_not_exists(segments_dir)
            print(f"Segments directory ready: {segments_dir}")

            for et in embedding_timestamps:
                embedding_id = et.embedding_id
                timestamp_id = et.timestamp_id
                start_time = et.start_time
                end_time = et.end_time

                embedding = self.session.query(Embedding).filter_by(embedding_id=embedding_id).first()
                if not embedding:
                    print(f"Embedding with ID {embedding_id} not found.")
                    continue

                segment = embedding.segment
                if not segment:
                    print(f"Segment associated with Embedding ID {embedding_id} not found.")
                    continue

                audio_file_path = segment.file_path
                output_filename = f"segment_{timestamp_id}.wav"
                output_file_path = os.path.join(segments_dir, output_filename)

                start_ms = int(start_time * 1000)
                end_ms = int(end_time * 1000)

                self.segmenter.export_segment(
                    input_file=audio_file_path,
                    start_ms=start_ms,
                    end_ms=end_ms,
                    output_file=output_file_path,
                    format="wav"
                )

                print(f"Segmented audio saved as {output_file_path}")
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred during audio segmentation: {e}")
        finally:
            self.session.close() 