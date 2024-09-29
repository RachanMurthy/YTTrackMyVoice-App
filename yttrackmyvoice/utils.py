from pytubefix import Playlist
from dotenv import load_dotenv
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
