import os
from pytubefix import YouTube
from pytubefix.cli import on_progress

def download_youtube_audio(url, output_path='.'):
    try:
        # Create YouTube object
        yt = YouTube(url, on_progress_callback=on_progress)

        # Print the title of the video
        print(f'Downloading: {yt.title}')
        
        # Try to filter for a webm audio stream first
        # Only webm for now
        audio_stream = yt.streams.filter(only_audio=True, file_extension='webm').first()

        # Get the file format/subtype (e.g., 'webm', 'm4a')
        file_format = audio_stream.subtype

        # Construct the expected file name
        file_name = f"{yt.title}.{file_format}"
        audio_file_path = os.path.join(output_path, file_name)
        
        # Check if the file already exists
        if os.path.exists(audio_file_path):
            print(f"File already exists: {audio_file_path}")
            return audio_file_path
        
        # Download the audio in its correct format
        audio_file = audio_stream.download(output_path=output_path, filename=f"{yt.title}.{file_format}")

        print(f"Downloaded audio file: {audio_file} in {file_format} format")
        return audio_file
    
    except Exception as e:
        print(f"Error downloading audio: {str(e)}")
        return None

