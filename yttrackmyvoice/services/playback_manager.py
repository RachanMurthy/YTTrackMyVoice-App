import os
import simpleaudio as sa
from yttrackmyvoice.database import SessionLocal
from yttrackmyvoice.database.models import LabelName, EmbeddingLabel, EmbeddingTimestamp, Segment

class PlaybackManager:
    def __init__(self, project):
        self.project = project
        self.session = SessionLocal()

    def play_segments_by_label(self, label_name):
        try:
            label = self.session.query(LabelName).filter_by(label_name=label_name).first()
            if not label:
                print(f"Label '{label_name}' does not exist.")
                return

            embedding_labels = self.session.query(EmbeddingLabel).filter_by(label_id=label.label_id).all()
            if not embedding_labels:
                print(f"No embeddings found for label '{label_name}'.")
                return

            embedding_ids = [el.embedding_id for el in embedding_labels]

            embedding_timestamps = self.session.query(EmbeddingTimestamp).filter(
                EmbeddingTimestamp.embedding_id.in_(embedding_ids)
            ).all()

            if not embedding_timestamps:
                print(f"No embedding timestamps found for label '{label_name}'.")
                return

            segment_ids = list(
                set(
                    et.embedding.segment_id
                    for et in embedding_timestamps
                    if et.embedding and et.embedding.segment
                )
            )

            if not segment_ids:
                print(f"No segments found for label '{label_name}'.")
                return

            segments = self.session.query(Segment).filter(Segment.segment_id.in_(segment_ids)).all()

            if not segments:
                print(f"No segments found for label '{label_name}'.")
                return

            file_paths = [segment.file_path for segment in segments]

            if not file_paths:
                print(f"No audio files found for label '{label_name}'.")
                return

            for file_path in file_paths:
                if os.path.exists(file_path):
                    print(f"Playing segment: {file_path}")
                    try:
                        wave_obj = sa.WaveObject.from_wave_file(file_path)
                        play_obj = wave_obj.play()
                        play_obj.wait_done()
                    except Exception as e:
                        print(f"Failed to play {file_path}: {e}")
                else:
                    print(f"File not found: {file_path}")
        except Exception as e:
            print(f"An error occurred while playing segments: {e}")
        finally:
            self.session.close() 