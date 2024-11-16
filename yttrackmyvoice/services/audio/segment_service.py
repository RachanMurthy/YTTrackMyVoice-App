import os
from yttrackmyvoice.database import SessionLocal
from yttrackmyvoice.database.models import AudioFile, Segment, EmbeddingTimestamp, Embedding
from yttrackmyvoice.utils import create_directory_if_not_exists
from yttrackmyvoice.services.audio.segmenter import Segmenter

class AudioSegmentService:
    def __init__(self, project):
        self.project = project

    def segment_all_audio(self, segment_length_ms):
        """
        Splits audio files associated with the project into segments.

        Parameters:
        - segment_length_ms: The length of each segment in milliseconds.
        """
        session = SessionLocal()
        try:
            # Ensure the project is attached to the session
            session.add(self.project)
            session.refresh(self.project)

            audio_files = session.query(AudioFile).filter_by(project_id=self.project.project_id).all()

            if not audio_files:
                print(f"No audio files found for project '{self.project_name}'. Please add audio files first.")
                return

            segmenter = Segmenter()  # Create an instance of the Segmenter class

            for audio_file in audio_files:
                audio_file_id = audio_file.audio_id
                audio_file_path = audio_file.audio_path
                audio_segments = session.query(Segment).filter_by(audio_id=audio_file_id).first()

                if audio_segments:
                    print(f"Audio segments already exist for '{audio_file_path}'")
                    continue

                segmenter.split_audio_file(audio_file_id, segment_length_ms)
        finally:
            session.close()

    def segment_audio_using_embeddings_timestamps(self):
        """
        Segments audio files based on the EmbeddingTimestamps table.
        Each segment is saved with a filename corresponding to its timestamp ID
        in a separate 'segments' directory at the same level as the audio folders.
        """
        session = SessionLocal()
        try:
            print("Starting audio segmentation using EmbeddingTimestamps.")

            # Retrieve all EmbeddingTimestamps
            embedding_timestamps = session.query(EmbeddingTimestamp).all()
            if not embedding_timestamps:
                print("No EmbeddingTimestamps found in the database.")
                return

            segmenter = Segmenter()  # Utilize the existing Segmenter class

            # Define a top-level 'segments' directory within the project path
            project_path = self.project.project_path
            segments_dir = os.path.join(project_path, "FinalSegments")
            create_directory_if_not_exists(segments_dir)
            print(f"Segments directory ready: {segments_dir}")

            for et in embedding_timestamps:
                embedding_id = et.embedding_id
                timestamp_id = et.timestamp_id
                start_time = et.start_time
                end_time = et.end_time

                # Retrieve the associated embedding and segment to get the audio file path
                embedding = session.query(Embedding).filter_by(embedding_id=embedding_id).first()
                if not embedding:
                    print(f"Embedding with ID {embedding_id} not found.")
                    continue

                segment = embedding.segment
                if not segment:
                    print(f"Segment associated with Embedding ID {embedding_id} not found.")
                    continue

                audio_file_path = segment.file_path

                # Define output file path using timestamp_id within the top-level 'segments' directory
                output_filename = f"segment_{timestamp_id}.wav"
                output_file_path = os.path.join(segments_dir, output_filename)

                # Convert start_time and end_time from seconds to milliseconds
                start_ms = int(start_time * 1000)
                end_ms = int(end_time * 1000)

                # Export the segment
                segmenter.export_segment(
                    input_file=audio_file_path,
                    start_ms=start_ms,
                    end_ms=end_ms,
                    output_file=output_file_path,
                    format="wav"
                )

                print(f"Segmented audio saved as {output_file_path}")

        except Exception as e:
            session.rollback()
            print(f"An error occurred during audio segmentation: {e}")
        finally:
            session.close()