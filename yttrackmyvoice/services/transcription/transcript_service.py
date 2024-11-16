from yttrackmyvoice.database import SessionLocal
from yttrackmyvoice.database.models import Segment, Transcript, FinalSegment, LabelName, EmbeddingTimestamp, EmbeddingLabel
import os
import whisper

class TranscriptService:
    def __init__(self, project, model_name="base"):
        self.project = project
        self.model = whisper.load_model(model_name)

    def transcribe_final_segments(self):
        """
        Transcribes audio segments in the 'FinalSegments' directory using Whisper
        and stores the transcriptions and final segments in the database.
        """
        session = SessionLocal()
        try:
            # Define the path to the FinalSegments directory
            project_path = self.project.project_path
            final_segments_dir = os.path.join(project_path, "FinalSegments")

            if not os.path.isdir(final_segments_dir):
                print(f"FinalSegments directory not found at path: {final_segments_dir}")
                return

            # Iterate over all audio files in FinalSegments
            for filename in os.listdir(final_segments_dir):
                if filename.endswith(".wav"):
                    file_path = os.path.join(final_segments_dir, filename)

                    # Extract timestamp_id from filename (assuming format: segment_{timestamp_id}.wav)
                    try:
                        timestamp_id_str = filename.split("_")[1].split(".")[0]
                        timestamp_id = int(timestamp_id_str)
                    except (IndexError, ValueError):
                        print(f"Filename '{filename}' does not match the expected format. Skipping.")
                        continue

                    # Check if transcription already exists for this timestamp_id
                    existing_transcript = session.query(Transcript).filter_by(timestamp_id=timestamp_id).first()
                    if existing_transcript:
                        print(f"Transcript already exists for timestamp_id {timestamp_id}. Skipping.")
                        continue

                    # Transcribe the audio file using Whisper
                    print(f"Transcribing '{filename}'...")
                    try:
                        result = self.model.transcribe(file_path)
                        transcription = result["text"].strip()
                        print(f"Transcription for timestamp_id {timestamp_id}: {transcription}")
                    except Exception as e:
                        print(f"An error occurred while transcribing '{filename}': {e}")
                        continue

                    # Create a new Transcript record
                    new_transcript = Transcript(
                        timestamp_id=timestamp_id,
                        text=transcription
                    )
                    session.add(new_transcript)
                    session.commit()
                    print(f"Transcription stored for timestamp_id {timestamp_id}.")

                    # **Add FinalSegment to Database**
                    try:
                        # Determine the label_id for this transcription
                        label_id = self.get_label_id_for_transcription(timestamp_id)
                        if label_id is None:
                            print(f"No valid label found for timestamp_id {timestamp_id}. Skipping FinalSegment creation.")
                            continue

                        # Define the new FinalSegment file path
                        # For example, you might copy or move the original segment to create a FinalSegment
                        # Here, we'll assume that the FinalSegment file is the same as the original for simplicity
                        final_segment_file_path = file_path  # Modify as needed

                        new_final_segment = FinalSegment(
                            label_id=label_id,
                            file_path=final_segment_file_path
                        )
                        session.add(new_final_segment)
                        session.commit()
                        print(f"FinalSegment added with ID {new_final_segment.final_segment_id} for timestamp_id {timestamp_id}.")

                    except Exception as e:
                        session.rollback()
                        print(f"An error occurred while adding FinalSegment for timestamp_id {timestamp_id}: {e}")

            print("All eligible audio segments have been transcribed and stored.")

        except Exception as e:
            session.rollback()
            print(f"An error occurred during transcription: {e}")
        finally:
            session.close()

    def get_label_id_for_transcription(self, timestamp_id):
        session = SessionLocal()
        try:
            # Retrieve the EmbeddingTimestamp record
            embedding_timestamp = session.query(EmbeddingTimestamp).filter_by(timestamp_id=timestamp_id).first()
            if not embedding_timestamp:
                print(f"No EmbeddingTimestamp found for timestamp_id {timestamp_id}.")
                return None
            
            # Retrieve the label associated with the embedding
            embedding_id = embedding_timestamp.embedding_id
            embedding_label = session.query(EmbeddingLabel).filter_by(embedding_id=embedding_id).first()
            if not embedding_label:
                print(f"No EmbeddingLabel found for embedding_id {embedding_id}.")
                return None

            # Retrieve the label name associated with the label
            label_id = embedding_label.label_id
            label_name_record = session.query(LabelName).filter_by(label_id=label_id).first()
            if not label_name_record:
                print(f"No LabelName found for label_id {label_id}.")
                return None

            label_name = label_name_record.label_name
            print(f"Label Name: {label_name}")
            return label_id
        except Exception as e:
            print(f"Error retrieving label_id for timestamp_id {timestamp_id}: {e}")
            return None
        finally:
            session.close()