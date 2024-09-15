import os
import re
from pytubefix import YouTube
from pytubefix.cli import on_progress
from pydub import AudioSegment

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


def download_youtube_audio(url, output_path='.', wav_output_path=None):
    """
    Downloads the audio stream from a YouTube video given its URL and converts it to a .wav file.

    Parameters:
    - url: The YouTube video URL.
    - output_path: The directory where the original .webm audio file will be saved (default is the current directory).
    - wav_output_path: The directory where the converted .wav file will be saved (default is the current directory).

    Returns:
    - The path to the converted .wav file, or None if an error occurred.
    """
    try:
        # Use output_path for wav_output_path if it is not provided
        if wav_output_path is None:
            wav_output_path = output_path

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

        # Construct the file name using the sanitized title and format
        file_name = f"{sanitized_title}.{file_format}"
        audio_file_path = os.path.join(output_path, file_name)
        
        # Check if the file already exists to avoid re-downloading
        if os.path.exists(audio_file_path):
            print(f"File already exists: {audio_file_path}")
        else:
            # Download the audio in the correct format
            audio_stream.download(output_path=output_path, filename=file_name)
            print(f"Downloaded audio file: {audio_file_path} in {file_format} format")
        
        # Convert the .webm file to .wav
        wav_file_name = f"{sanitized_title}.wav"
        wav_file_path = os.path.join(wav_output_path, wav_file_name)

        # Perform the conversion if the .wav file doesn't exist
        if not os.path.exists(wav_file_path):
            convert_webm_to_wav(audio_file_path, wav_file_path)
        else:
            print(f"Converted .wav file already exists: {wav_file_path}")

        return wav_file_path

    except Exception as e:
        # Print an error message if the download or conversion fails
        print(f"Error downloading or converting audio: {str(e)}")
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
