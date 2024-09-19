import os
import re
from pytubefix import YouTube
from pytubefix.cli import on_progress
from pydub import AudioSegment
from .database import SessionLocal  # Import the session
from .database.models import Project, URL, AudioFile, Segment  # Import the Project model
from .utils import create_directory_if_not_exists

def sanitize_filename(filename):
    """
    Sanitizes a string to be a valid filename by removing or replacing invalid characters.

    Parameters:
    - filename: The original filename string.

    Returns:
    - A sanitized filename string.
    """
    # Remove any invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', filename)
    # Remove trailing dots and spaces
    sanitized = sanitized.rstrip('. ')
    return sanitized


def download_youtube_audio(url_id):
    """
    Downloads the audio stream from a YouTube video given its URL, converts it to a .wav file, 
    and returns the path to the .wav file along with the duration of the audio.

    Parameters:
    - url: The YouTube video URL.
    - output_path: The directory where the original .webm audio file will be saved (default is the current directory).
    - wav_output_path: The directory where the converted .wav file will be saved (default is the current directory).

    Returns:
    - A tuple containing the path to the converted .wav file and the duration in seconds, or (None, None) if an error occurred.
    """
    try:
        session = SessionLocal()
        # Retrieve the project from the database
        url_record = session.query(URL).filter_by(url_id=url_id).first()
        url = url_record.url

        # Create a YouTube object with a progress callback
        yt = YouTube(url, on_progress_callback=on_progress)

        # Print the title of the video being downloaded
        print(f'Downloading: {yt.title}')
        
        # Attempt to filter for an audio-only stream (webm format)
        audio_stream = yt.streams.filter(only_audio=True, file_extension='webm').first()

        # Get the file format (e.g., 'webm', 'm4a')
        file_format = audio_stream.subtype

        # Sanitize the video title to create a safe filename
        sanitized_title = sanitize_filename(yt.title)

        project = url_record.project
        project_path = project.project_path

        # Generate a unique folder name based on URL ID
        url_id = f"{url_record.url_id}"

        # Define the folder path for this URL
        audio_folder_path = os.path.join(project_path, url_id)

        # Ensure the folder exists
        create_directory_if_not_exists(audio_folder_path)
        print(f"Audio Folder ready: {audio_folder_path}")

        # Construct the file name using the sanitized title and format
        audio_file_name = f"{sanitized_title}.{file_format}"
        audio_file_path = os.path.join(audio_folder_path, audio_file_name)
        
        # Check if the file already exists to avoid re-downloading
        if os.path.exists(audio_file_path):
            print(f"File already exists: {audio_file_path}")
        else:
            # Download the audio in the correct format
            audio_stream.download(output_path=audio_folder_path, filename=audio_file_name)
            print(f"Downloaded audio file: {audio_file_path} in {file_format} format")
        
        # Convert the .webm file to .wav
        wav_file_name = f"{sanitized_title}.wav"
        wav_file_path = os.path.join(audio_folder_path, wav_file_name)

        # Perform the conversion if the .wav file doesn't exist
        if not os.path.exists(wav_file_path):
            try:
                convert_webm_to_wav(audio_file_path, wav_file_path)
                # Load the .wav file with pydub to get the duration
                audio_segment = AudioSegment.from_wav(wav_file_path)
                duration = audio_segment.duration_seconds  # Duration in seconds

                # Create a new AudioFile record
                audio_file = AudioFile(
                    project_id=project.project_id,
                    url_id=url_id,  # Associate with the specific URL
                    url_name=sanitized_title, 
                    audio_path=wav_file_path,
                    audio_folder_path=audio_folder_path,
                    duration_seconds=duration
                )
                # Add the AudioFile to the session
                session.add(audio_file)
                session.commit()
            except Exception as e:
                # Catch any unforeseen errors and roll back the session
                session.rollback()
                print(f"\nAn error occurred: {str(e)}")
        else:
            print(f"Converted .wav file already exists: {wav_file_path}")
        
        return audio_file

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def convert_webm_to_wav(input_filepath, output_filepath):
    """
    Converts a .webm audio file to a .wav file.

    Parameters:
    - input_filepath: The path to the input .webm file.
    - output_filepath: The path where the .wav file will be saved.

    Returns:
    - The path to the .wav file.
    """
    # Load the .webm file
    audio = AudioSegment.from_file(input_filepath, format="webm")
    
    # Export as .wav
    audio.export(output_filepath, format="wav")
    print(f"Converted {input_filepath} to {output_filepath}")
    return output_filepath
