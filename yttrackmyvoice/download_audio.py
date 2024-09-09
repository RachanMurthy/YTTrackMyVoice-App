import os
from pytubefix import YouTube
from pytubefix.cli import on_progress

def download_youtube_audio(url, output_path='.'):
    """
    Downloads the audio stream from a YouTube video given its URL.

    Parameters:
    - url: The YouTube video URL.
    - output_path: The directory where the audio file will be saved (default is the current directory).

    Returns:
    - The path to the downloaded audio file, or None if an error occurred.
    """
    try:
        # Create a YouTube object with a progress callback
        yt = YouTube(url, on_progress_callback=on_progress)

        # Print the title of the video being downloaded
        print(f'Downloading: {yt.title}')
        
        # Attempt to filter for an audio-only stream (webm format)
        audio_stream = yt.streams.filter(only_audio=True, file_extension='webm').first()

        # Get the file format (e.g., 'webm', 'm4a')
        file_format = audio_stream.subtype

        # Construct the file name using the video's title and format
        file_name = f"{yt.title}.{file_format}"
        audio_file_path = os.path.join(output_path, file_name)
        
        # Check if the file already exists to avoid re-downloading
        if os.path.exists(audio_file_path):
            print(f"File already exists: {audio_file_path}")
            return audio_file_path
        
        # Download the audio in the correct format
        audio_file = audio_stream.download(output_path=output_path, filename=file_name)

        print(f"Downloaded audio file: {audio_file} in {file_format} format")
        return audio_file

    except Exception as e:
        # Print an error message if the download fails
        print(f"Error downloading audio: {str(e)}")
        return None