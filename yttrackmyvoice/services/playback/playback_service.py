import os
import simpleaudio as sa
from yttrackmyvoice.database import SessionLocal
from yttrackmyvoice.database.models import FinalSegment, LabelName, EmbeddingLabel, EmbeddingTimestamp

class PlaybackService:
    def play_segments_by_label(self, label_name):
        """
        Play all final audio segments associated with the specified speaker label.

        Parameters:
        - label_name (str): The name of the speaker label.

        Returns:
        - None
        """
        session = SessionLocal()
        try:
            # Retrieve the label by name
            label = session.query(LabelName).filter_by(label_name=label_name).first()
            if not label:
                print(f"Label '{label_name}' does not exist.")
                return

            label_id = label.label_id
            print(f"Found label ID: {label_id} for label name: '{label_name}'")

            # Directly retrieve FinalSegments using label_id
            final_segments = session.query(FinalSegment).filter_by(label_id=label_id).all()

            if not final_segments:
                print(f"No final segments found for label '{label_name}'.")
                return

            # Retrieve file paths from FinalSegments
            file_paths = [fs.file_path for fs in final_segments if fs.file_path]

            if not file_paths:
                print(f"No audio files found for label '{label_name}'.")
                return

            print(f"Found {len(file_paths)} audio files to play for label '{label_name}'")

            # Play each file
            for file_path in file_paths:
                if os.path.exists(file_path):
                    print(f"Playing final segment: {file_path}")
                    try:
                        wave_obj = sa.WaveObject.from_wave_file(file_path)
                        play_obj = wave_obj.play()
                        play_obj.wait_done()  # Wait until playback is finished
                    except Exception as e:
                        print(f"Failed to play {file_path}: {e}")
                else:
                    print(f"File not found: {file_path}")

        except Exception as e:
            print(f"An error occurred while playing segments: {e}")
        finally:
            session.close() 