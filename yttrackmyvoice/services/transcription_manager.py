import os
import whisper
from yttrackmyvoice.database import SessionLocal
from yttrackmyvoice.database.models import Transcript, EmbeddingTimestamp
from yttrackmyvoice.utils import get_key

class TranscriptionManager:
    def __init__(self, project):
        self.project = project
        self.session = SessionLocal()
        self.model = None

    def load_whisper_model(self, model_size="base"):
        try:
            print("Loading Whisper model...")
            self.model = whisper.load_model(model_size)
            print("Whisper model loaded.")
        except Exception as e:
            print(f"Failed to load Whisper model: {e}")

    def transcribe_final_segments(self):
        try:
            if not self.model:
                self.load_whisper_model()

            project_path = self.project.project_path
            final_segments_dir = os.path.join(project_path, "FinalSegments")

            if not os.path.isdir(final_segments_dir):
                print(f"FinalSegments directory not found at path: {final_segments_dir}")
                return

            for filename in os.listdir(final_segments_dir):
                if filename.endswith(".wav"):
                    file_path = os.path.join(final_segments_dir, filename)

                    try:
                        timestamp_id_str = filename.split("_")[1].split(".")[0]
                        timestamp_id = int(timestamp_id_str)
                    except (IndexError, ValueError):
                        print(f"Filename '{filename}' does not match the expected format. Skipping.")
                        continue

                    existing_transcript = self.session.query(Transcript).filter_by(timestamp_id=timestamp_id).first()
                    if existing_transcript:
                        print(f"Transcript already exists for timestamp_id {timestamp_id}. Skipping.")
                        continue

                    print(f"Transcribing '{filename}'...")
                    try:
                        result = self.model.transcribe(file_path)
                        transcription = result["text"].strip()
                        print(f"Transcription for timestamp_id {timestamp_id}: {transcription}")
                    except Exception as e:
                        print(f"An error occurred while transcribing '{filename}': {e}")
                        continue

                    new_transcript = Transcript(
                        timestamp_id=timestamp_id,
                        text=transcription
                    )
                    self.session.add(new_transcript)
                    self.session.commit()
                    print(f"Transcription stored for timestamp_id {timestamp_id}.")

            print("All eligible audio segments have been transcribed and stored.")
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred during transcription: {e}")
        finally:
            self.session.close() 