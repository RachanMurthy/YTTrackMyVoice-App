import os
from math import ceil
from pydub import AudioSegment
from .utils import create_directory_if_not_exists
from .database import SessionLocal
from .database.models import AudioFile, Segment


class Segmenter:
    def __init__(self):
        pass

    def export_segment(self, input_file, start_ms, end_ms, output_file, format="wav"):
        """
        Export a segment of an audio file between start_ms and end_ms.

        Parameters:
        - input_file (str): Path to the input audio file.
        - start_ms (int): Start time in milliseconds.
        - end_ms (int): End time in milliseconds.
        - output_file (str): Path to the output audio file.
        - format (str): Audio format for the output file (default is "wav").

        Returns:
        - None
        """
        try:
            # Load the input audio file using pydub
            audio = AudioSegment.from_file(input_file)
            # Extract the segment from start_ms to end_ms
            segment = audio[start_ms:end_ms]
            # Export the segment to the specified file and format
            segment.export(output_file, format=format)
            print(f"Exported segment to {output_file} from {start_ms / 1000}s to {end_ms / 1000}s")
        except Exception as e:
            # Handle any error that occurs during the export process
            print(f"Error exporting segment: {e}")

    def split_audio_file(self, audio_id, segment_length_ms, format="wav"):
        """
        Split an audio file into fixed-length segments and store the segment details in the database.

        Parameters:
        - audio_id (int): The ID of the audio file in the database.
        - segment_length_ms (int): Length of each segment in milliseconds.
        - format (str): Audio format for the output segments (default is "wav").

        Returns:
        - None
        """
        # Open a new database session
        session = SessionLocal()
        audio_record = session.query(AudioFile).filter_by(audio_id=audio_id).first()  # Fetch the audio file record from the database

        if not audio_record:
            print(f"No audio record found with audio_id: {audio_id}")
            session.close()
            return

        try:
            # Retrieve the audio file path and folder path from the audio record
            audio_file_path = audio_record.audio_path
            audio_folder_path = audio_record.audio_folder_path

            # Create a subdirectory to store the split segments
            segments_dir = os.path.join(audio_folder_path, "segments")
            create_directory_if_not_exists(segments_dir)

            # Load the audio file using pydub
            audio = AudioSegment.from_file(audio_file_path)
            total_length_ms = len(audio)  # Get the total length of the audio file in milliseconds

            # Calculate the number of segments needed
            num_segments = ceil(total_length_ms / segment_length_ms)

            try:
                # Loop over the number of segments and export each one
                for i in range(num_segments):
                    start_ms = i * segment_length_ms
                    end_ms = min((i + 1) * segment_length_ms, total_length_ms)
                    segment_file_name = f"segment_{i + 1}.{format}"
                    segment_file_path = os.path.join(segments_dir, segment_file_name)

                    # Export the segment
                    self.export_segment(audio_file_path, start_ms, end_ms, segment_file_path, format=format)

                    # Calculate the duration of the segment in seconds
                    duration_seconds = (end_ms - start_ms) / 1000

                    # Create a new Segment object and store it in the database
                    new_segment = Segment(
                        audio_id=audio_record.audio_id,
                        start_time=start_ms,
                        end_time=end_ms,
                        duration=duration_seconds,
                        file_path=segment_file_path
                    )
                    session.add(new_segment)
                    session.commit()  # Commit the segment to the database

            except Exception as e:
                # Rollback the transaction in case of an error
                session.rollback()
                print(f"An error occurred while splitting the audio file: {e}")
            finally:
                # Close the session once finished
                session.close()

            print(f"Audio file '{audio_file_path}' has been split into {num_segments} segments.")

        except Exception as e:
            # Handle any error that occurs during the process
            print(f"Error splitting audio file: {e}")
            session.close()
            return
