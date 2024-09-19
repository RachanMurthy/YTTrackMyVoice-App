import os
import re
from pytubefix import YouTube
from pytubefix.cli import on_progress
from pydub import AudioSegment
from .database import SessionLocal  # Import the session to interact with the database
from .database.models import Project, URL, AudioFile, Segment  # Import relevant models from the database
from .utils import create_directory_if_not_exists  # Utility function to create directories

def sanitize_filename(filename):
    """
    Sanitizes a string to be a valid filename by removing or replacing invalid characters.

    Parameters:
    - filename: The original filename string.

    Returns:
    - A sanitized filename string.
    """
    # Remove invalid characters for filenames using regex
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', filename)
    # Remove trailing dots and spaces
    sanitized = sanitized.rstrip('. ')
    return sanitized


def download_youtube_audio(url_id):
    """
    Downloads the audio stream from a YouTube video given its URL, converts it to a .wav file, 
    and returns the path to the .wav file along with the duration of the audio.

    Parameters:
    - url_id: The ID of the URL in the database.

    Returns:
    - AudioFile object containing the path to the converted .wav file and the duration, or None if an error occurred.
    """
    try:
        session = SessionLocal()  # Start a new session for database interaction
        # Retrieve the URL record from the database
        url_record = session.query(URL).filter_by(url_id=url_id).first()
        url = url_record.url  # Extract the actual YouTube URL from the record

        # Create a YouTube object and associate a progress callback
        yt = YouTube(url, on_progress_callback=on_progress)

        # Log the video title for reference
        print(f'Downloading: {yt.title}')
        
        # Filter for an audio-only stream in the .webm format
        audio_stream = yt.streams.filter(only_audio=True, file_extension='webm').first()

        # Get the audio file's format (e.g., 'webm', 'm4a')
        file_format = audio_stream.subtype

        # Sanitize the video title to generate a valid filename
        sanitized_title = sanitize_filename(yt.title)

        # Retrieve the associated project and its file path from the URL record
        project = url_record.project
        project_path = project.project_path

        # Generate a unique folder name based on the URL ID
        url_id = f"{url_record.url_id}"

        # Define the folder path for this URL's audio files
        audio_folder_path = os.path.join(project_path, url_id)

        # Ensure the folder exists by creating it if necessary
        create_directory_if_not_exists(audio_folder_path)
        print(f"Audio Folder ready: {audio_folder_path}")

        # Construct the audio file name using the sanitized title and format
        audio_file_name = f"{sanitized_title}.{file_format}"
        audio_file_path = os.path.join(audio_folder_path, audio_file_name)
        
        # Check if the file already exists to avoid re-downloading
        if os.path.exists(audio_file_path):
            print(f"File already exists: {audio_file_path}")
        else:
            # Download the audio in the specified format
            audio_stream.download(output_path=audio_folder_path, filename=audio_file_name)
            print(f"Downloaded audio file: {audio_file_path} in {file_format} format")
        
        # Convert the .webm file to .wav format
        wav_file_name = f"{sanitized_title}.wav"
        wav_file_path = os.path.join(audio_folder_path, wav_file_name)

        # Perform the conversion only if the .wav file doesn't already exist
        if not os.path.exists(wav_file_path):
            try:
                # Call the helper function to convert the .webm file to .wav
                convert_webm_to_wav(audio_file_path, wav_file_path)
                
                # Load the .wav file to get its duration using pydub
                audio_segment = AudioSegment.from_wav(wav_file_path)
                duration = audio_segment.duration_seconds  # Duration in seconds

                # Create a new AudioFile record and associate it with the URL and project
                audio_file = AudioFile(
                    project_id=project.project_id,
                    url_id=url_id,  # Associate with the specific URL 
                    audio_path=wav_file_path,
                    audio_folder_path=audio_folder_path,
                    duration_seconds=duration
                )
                # Add the new audio file record to the database
                session.add(audio_file)
                session.commit()  # Commit the changes to the database
            except Exception as e:
                # Roll back the transaction in case of any error
                session.rollback()
                print(f"\nAn error occurred: {str(e)}")
        else:
            print(f"Converted .wav file already exists: {wav_file_path}")
        
        return audio_file  # Return the audio file record

    except Exception as e:
        # Handle any exceptions that occur during the download or conversion process
        print(f"An error occurred: {e}")
        return None  # Return None if any error occurs


def convert_webm_to_wav(input_filepath, output_filepath):
    """
    Converts a .webm audio file to a .wav file.

    Parameters:
    - input_filepath: The path to the input .webm file.
    - output_filepath: The path where the .wav file will be saved.

    Returns:
    - The path to the .wav file.
    """
    # Load the .webm file using pydub's AudioSegment
    audio = AudioSegment.from_file(input_filepath, format="webm")
    
    # Export the audio file in .wav format
    audio.export(output_filepath, format="wav")
    print(f"Converted {input_filepath} to {output_filepath}")
    return output_filepath  # Return the path of the converted file
