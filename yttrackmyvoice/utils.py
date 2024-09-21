from pytubefix import Playlist
from pydub import AudioSegment
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from .database import SessionLocal
from .database.models import Project, URL, AudioFile, Segment
from math import ceil
import os

def create_directory_if_not_exists(directory_path):
    """
    Creates a directory if it does not already exist.
    
    Args:
        directory_path (str): The path of the directory to be created.
    
    Returns:
        bool: True if the directory was created, False if it already exists.
    """
    # Check if the directory does not exist
    if not os.path.exists(directory_path):
        # Create the directory, including any necessary parent directories
        os.makedirs(directory_path, exist_ok=True)
        # Print message confirming directory creation
        print(f"Directory created: {directory_path}")
        return True  # Return True indicating directory was created
    else:
        # Print message if the directory already exists
        print(f"Directory already exists: {directory_path}")
        return False  # Return False indicating the directory already existed


def extract_video_urls_from_playlist(playlist_url):
    """
    Given a YouTube playlist URL, this function returns a list of video URLs.

    Args:
        playlist_url (str): The URL of the YouTube playlist.

    Returns:
        list: A list of video URLs from the playlist.
    """
    try:
        # Create a Playlist object using pytubefix
        playlist = Playlist(playlist_url)

        # Extract all video URLs from the playlist
        video_urls = [video.watch_url for video in playlist.videos]

        return video_urls
    
    except Exception as e:
        # Handle any error that occurs during the playlist extraction
        print(f"An error occurred: {e}")
        return []


def get_key(secret_key):
    """
    Fetches a secret key from the environment variables using dotenv.

    Args:
        secret_key (str): The name of the environment variable.

    Returns:
        str: The value of the requested secret key, or None if not found.
    """
    # Load the .env file to access environment variables
    load_dotenv()

    # Access and return the secret key
    key = os.getenv(secret_key)

    return key


def export_segment(input_file, start_ms, end_ms, output_file, format="wav"):
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


def split_audio_file(audio_id, segment_length_ms, format="wav"):
    """
    Split an audio file into fixed-length segments and store the segment details in the database.

    Parameters:
    - audio_id (int): The ID of the audio file in the database.
    - segment_length_ms (int): Length of each segment in milliseconds (default is 10 minutes).
    - format (str): Audio format for the output segments (default is "wav").

    Returns:
    - Segment: The last segment created (or None if an error occurred).
    """
    # Open a new database session
    session = SessionLocal()
    audio_record = session.query(AudioFile).filter_by(audio_id=audio_id).first()  # Fetch the audio file record from the database

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
                segment = audio[start_ms:end_ms]
                
                # Generate the file name for the segment and export it
                segment_file_name = f"segment_{i + 1}.{format}"
                segment_file_path = os.path.join(segments_dir, segment_file_name)
                segment.export(segment_file_path, format=format)
                print(f"Exported: {segment_file_path}")

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
        return new_segment  # Return the last segment created

    except Exception as e:
        # Handle any error that occurs during the process
        print(f"Error splitting audio file: {e}")
        return None
