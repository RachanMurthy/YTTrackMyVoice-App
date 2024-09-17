from pytubefix import Playlist
from pydub import AudioSegment
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from .database import SessionLocal
from .database.models import Project, URL
from math import ceil
import csv
import os

def save_list_to_csv(data_list, file_path, mode='w'):
    """
    Saves a list of items to a CSV file.
    
    Args:
        data_list (list): A list of items to be saved.
        file_path (str): The path to the CSV file where the data will be saved.
        mode (str): File open mode, 'w' for overwrite, 'a' for append. Defaults to 'w'.
    
    Behavior:
        - Opens the file at the specified path in either write mode ('w') or append mode ('a').
        - Iterates over the list of items and writes each item to a new row in the CSV file.
        - Prints a confirmation message once the data has been saved.
    """
    # Open the CSV file in the specified mode, with 'newline' to prevent extra blank lines in the output.
    with open(file_path, mode=mode, newline='') as file:
        writer = csv.writer(file)
        # Write each item from the list as a new row in the CSV
        for item in data_list:
            writer.writerow([item])
    
    # Message indicating saving was successful
    action = "Appended" if mode == 'a' else "Saved"
    print(f"Items {action} to {file_path}")


def load_list_from_csv(file_path):
    """
    Loads a list of items from a CSV file and returns them in a dictionary with index as the key.
    
    Args:
        file_path (str): The path to the CSV file from which items will be loaded.
    
    Returns:
        dict: A dictionary with index as the key and items as the values.
    
    Behavior:
        - Opens the file in read mode ('r') if the file exists.
        - Reads the CSV file and stores each item in a dictionary with an index.
        - If the file does not exist, an empty dictionary is returned.
    """
    data_dict = {}
    
    # Check if the file exists to avoid FileNotFoundError.
    if os.path.exists(file_path):
        # Open the file in read mode.
        with open(file_path, mode='r') as file:
            reader = csv.reader(file)
            # Initialize a counter for the index
            count = 0
            # Loop through each row and store the item in the dictionary with the index
            for row in reader:
                data_dict[count] = row[0]
                count += 1
    
    # Return the dictionary of indexed items. If the file doesn't exist, it will return an empty dictionary.
    return data_dict


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


def create_folders_for_urls(url_list, main_folder):
    """
    Creates a directory for all videos and then creates a directory for each URL inside the main folder.
    
    Args:
        url_list (dict): A dictionary of URLs with index as the key.
        main_folder (str): The main folder where all video-specific folders will be created.
    
    Behavior:
        - Creates a main folder (if it doesn't exist) to store all video-specific folders.
        - For each URL, creates a folder named 'Video_<index>' inside the main folder.
        - Uses 'create_directory_if_not_exists' to check if the folder already exists before creating.
    """
    # First, create the main folder that will contain all video-specific folders
    create_directory_if_not_exists(main_folder)
    
    # Loop through each URL in the list
    for key, value in url_list.items():
        # Generate a folder name for each URL, based on its index
        folder_name = f'Video_{key}'
        
        # Create the folder path inside the main folder
        folder_path = os.path.join(main_folder, folder_name)
        
        # Use the function to create the folder if it does not exist
        create_directory_if_not_exists(folder_path)
        
        # Additional logic can be placed here after the folder is created
        print(f'Processing folder: {folder_path}')


def extract_video_urls_from_playlist(playlist_url):
    """
    Given a YouTube playlist URL, this function returns a list of video URLs.

    Args:
        playlist_url (str): The URL of the YouTube playlist.

    Returns:
        list: A list of video URLs from the playlist.
    """
    try:
        # Create a Playlist object
        playlist = Playlist(playlist_url)

        # Extract all video URLs from the playlist
        video_urls = [video.watch_url for video in playlist.videos]

        return video_urls
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def get_urls(project_name):
    """
    Manages the URLs for a given project, allowing the user to add new video or playlist URLs.

    Args:
    - project_name (str): The name of the project.
    - folder_path (str): The path to the project folder where URLs will be saved.

    Returns:
    - None
    """
    session: Session = SessionLocal()

    try:
        # Retrieve the project from the database
        project = session.query(Project).filter_by(project_name=project_name).first()
        if not project:
            print(f"Project '{project_name}' does not exist in the database.")
            return

        # Display existing URLs
        if project.urls:
            print(f"The project '{project_name}' contains the following URLs:\n")
            for url_entry in project.urls:
                print(f"- {url_entry.url} ({url_entry.url_type})")
        else:
            print(f"The project '{project_name}' has no saved URLs.")

        print("\nWould you like to submit a single video URL or a playlist URL?")
        print("Enter '1' for a single video, '2' for a playlist, or type 'STOP' to exit.")

        while True:
            # Get user input for a single URL or playlist, or stop
            choice = input("Enter your choice (1 for URL, 2 for playlist, 'STOP' to end): ").strip()

            if choice.upper() == 'STOP':
                break

            if choice == '1':
                # Handle single video URL input
                user_input = input("Enter the single URL (or type 'STOP' to end): ").strip()
                if user_input.upper() == 'STOP':
                    break
                
                # Check if the URL already exists in the database (query-based)
                existing_url = session.query(URL).filter_by(url=user_input, project_id=project.project_id).first()
                if existing_url:
                    print(f"URL already exists: {user_input}")
                    continue

                # Append the new URL
                new_url = URL(project_id=project.project_id, url=user_input, url_type='single')
                session.add(new_url)
                print(f"Added new URL: {user_input}")

            elif choice == '2':
                # Handle playlist URL input
                user_input = input("Enter the playlist URL (or type 'STOP' to end): ").strip()
                if user_input.upper() == 'STOP':
                    break
                
                # Extract all video URLs from the playlist
                playlist_urls = extract_video_urls_from_playlist(user_input)  # Ensure this function is defined

                # Check if each playlist URL already exists in the database (query-based)
                for playlist_url in playlist_urls:
                    existing_url = session.query(URL).filter_by(url=playlist_url, project_id=project.project_id).first()
                    if existing_url:
                        print(f"URL already exists: {playlist_url}")
                        continue
                    
                    # Append the new URL
                    new_url = URL(project_id=project.project_id, url=playlist_url, url_type='playlist')
                    session.add(new_url)
                    print(f"Added new URL from playlist: {playlist_url}")

            else:
                # Handle invalid input
                print("Invalid input. Please type '1' for URL, '2' for playlist, or 'STOP' to end.")

        # Commit all new URLs to the database
        session.commit()

        # Optionally, update the folder structure or perform other operations here
        print(f"URLs successfully updated for project '{project_name}'.")

    except Exception as e:
        session.rollback()
        print(f"An error occurred while managing URLs: {e}")
    finally:
        session.close()


def get_key(secret_key):
    # Load the .env file
    load_dotenv()

    # Access the variables
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
        audio = AudioSegment.from_file(input_file)
        segment = audio[start_ms:end_ms]
        segment.export(output_file, format=format)
        print(f"Exported segment to {output_file} from {start_ms / 1000}s to {end_ms / 1000}s")
    except Exception as e:
        print(f"Error exporting segment: {e}")


def split_audio_file(input_file, output_dir, segment_length_ms=10 * 60 * 1000, format="wav"):
    """
    Split an audio file into fixed-length segments and return segment details.

    Parameters:
    - input_file (str): Path to the input audio file.
    - output_dir (str): Directory where the output segments will be saved.
    - segment_length_ms (int): Length of each segment in milliseconds (default is 10 minutes).
    - format (str): Audio format for the output files (default is "wav").

    Returns:
    - List[dict]: A list of dictionaries containing segment details.
    """
    segments_info = []
    try:
        # Create a subdirectory for segments
        segments_dir = os.path.join(output_dir, "segments")
        create_directory_if_not_exists(segments_dir)

        # Load the audio file
        audio = AudioSegment.from_file(input_file)
        total_length_ms = len(audio)

        # Calculate the number of segments
        num_segments = ceil(total_length_ms / segment_length_ms)

        # Split and export segments
        for i in range(num_segments):
            start_ms = i * segment_length_ms
            end_ms = min((i + 1) * segment_length_ms, total_length_ms)
            segment = audio[start_ms:end_ms]
            segment_filename = f"segment_{i + 1}.{format}"
            segment_path = os.path.join(segments_dir, segment_filename)
            segment.export(segment_path, format=format)
            print(f"Exported: {segment_path}")

            # Calculate duration
            duration_seconds = (end_ms - start_ms) / 1000  # Convert ms to seconds

            # Store segment details
            segments_info.append({
                'segment_number': i + 1,
                'file_name': segment_filename,
                'file_path': segment_path,
                'start_time': start_ms / 1000,  # Convert ms to seconds
                'end_time': end_ms / 1000,      # Convert ms to seconds
                'duration': duration_seconds
            })

        print(f"Audio file '{input_file}' has been split into {num_segments} segments.")
        return segments_info

    except Exception as e:
        print(f"Error splitting audio file: {e}")
        return []