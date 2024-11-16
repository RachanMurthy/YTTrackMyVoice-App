import os
import re
from pytubefix import YouTube
from pytubefix.cli import on_progress
from pydub import AudioSegment
from yttrackmyvoice.database import SessionLocal
from yttrackmyvoice.database.models import URL, AudioFile
from yttrackmyvoice.utils import create_directory_if_not_exists
import subprocess

class Downloader:
    def __init__(self):
        pass

    @staticmethod
    def sanitize_filename(filename):
        """
        Sanitizes a string to be a valid filename by removing or replacing invalid characters.
        """
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', filename)
        sanitized = sanitized.rstrip('. ')
        return sanitized

    def download_youtube_audio(self, url_id):
        """
        Downloads the audio stream from a YouTube video given its URL, converts it to a .wav file,
        and returns the path to the .wav file along with the duration of the audio.
        """
        session = SessionLocal()
        try:
            # Retrieve the URL record from the database
            url_record = session.query(URL).filter_by(url_id=url_id).first()
            url = url_record.url

            # Create a YouTube object
            yt = YouTube(url, on_progress_callback=on_progress)
            print(f'Downloading: {yt.title}')

            # Filter for an audio-only stream in the .webm format
            audio_stream = yt.streams.filter(only_audio=True, file_extension='webm').first()
            file_format = audio_stream.subtype
            sanitized_title = self.sanitize_filename(yt.title)

            # Retrieve the associated project and its file path from the URL record
            project = url_record.project
            project_path = project.project_path

            # Generate a unique folder name based on the URL ID
            url_id_str = f"{url_record.url_id}"
            audio_folder_path = os.path.join(project_path, url_id_str)

            # Ensure the folder exists
            create_directory_if_not_exists(audio_folder_path)
            print(f"Audio Folder ready: {audio_folder_path}")

            # Construct the audio file name
            audio_file_name = f"{sanitized_title}.{file_format}"
            audio_file_path = os.path.join(audio_folder_path, audio_file_name)

            # Download the audio if it doesn't already exist
            if os.path.exists(audio_file_path):
                print(f"File already exists: {audio_file_path}")
            else:
                audio_stream.download(output_path=audio_folder_path, filename=audio_file_name)
                print(f"Downloaded audio file: {audio_file_path} in {file_format} format")

            # Convert to .wav format
            wav_file_name = f"{sanitized_title}.wav"
            wav_file_path = os.path.join(audio_folder_path, wav_file_name)

            if not os.path.exists(wav_file_path):
                self.convert_webm_to_wav(audio_file_path, wav_file_path)
                # Load the .wav file to get its duration
                audio_segment = AudioSegment.from_wav(wav_file_path)
                duration = audio_segment.duration_seconds  # Duration in seconds

                # Create a new AudioFile record
                audio_file = AudioFile(
                    project_id=project.project_id,
                    url_id=url_record.url_id,
                    audio_path=wav_file_path,
                    audio_folder_path=audio_folder_path,
                    duration_seconds=duration
                )
                session.add(audio_file)
                session.commit()
                print(f"Audio file record created for '{wav_file_path}'")
            else:
                print(f"Converted .wav file already exists: {wav_file_path}")

        except Exception as e:
            session.rollback()
            print(f"An error occurred: {e}")
        finally:
            session.close()

    @staticmethod
    def convert_webm_to_wav(input_filepath, output_filepath):
        """
        Converts a .webm audio file to a .wav file using ffmpeg to handle large files.
        """
        try:
            # Use ffmpeg to convert the file
            command = [
                'ffmpeg', '-i', input_filepath, '-acodec', 'pcm_s16le', '-ar', '44100', output_filepath
            ]
            subprocess.run(command, check=True)
            print(f"Converted {input_filepath} to {output_filepath}")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred during conversion: {e}")
