from pytubefix import Playlist
from dotenv import load_dotenv
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


def get_urls(project_name, folder_path):
    """
    Manages the URLs for a given project, allowing the user to add new video or playlist URLs.

    Args:
    - project_name (str): The name of the project.
    - folder_path (str): The path to the project folder where URLs will be saved.

    Returns:
    - str: The path to the CSV file storing the project's URLs.
    """
    urls = []

    # Path to the CSV file storing project URLs
    urls_csv = os.path.join(folder_path, 'urls.csv')

    # Load existing URLs from the CSV file
    urls_dict = load_list_from_csv(urls_csv)

    # Check if any URLs are already stored for the project
    if urls_dict:
        # If URLs exist, load them into the 'urls' list and print them
        urls = list(urls_dict.values())
        print(f"The project '{project_name}' contains the following URLs:\n")
        for url in urls:
            print(url)
    else:
        # If no URLs are found, inform the user
        print(f"The project '{project_name}' has no saved URLs.")

    # Ask the user for new URLs to add to the project
    print("Would you like to submit a single video URL or a playlist URL?")
    print("Enter '1' for a single video, '2' for a playlist, or type 'STOP' to exit.")
    
    while True:
        # Get user input for a single URL or playlist, or stop
        choice = input("Enter your choice (1 for URL, 2 for playlist, 'STOP' to end): ")
        
        if choice.upper() == 'STOP':
            break
        
        if choice == '1':
            # Handle single video URL input
            user_input = input("Enter the single URL (or type 'STOP' to end): ")
            if user_input.upper() == 'STOP':
                break
            # Check if the URL already exists
            if user_input in urls:
                print(f"URL already exists: {user_input}")
                continue
            # Append the new URL
            urls.append(user_input)

        elif choice == '2':
            # Handle playlist URL input
            user_input = input("Enter the playlist URL (or type 'STOP' to end): ")
            if user_input.upper() == 'STOP':
                break
            # Extract all video URLs from the playlist
            playlist_urls = extract_video_urls_from_playlist(user_input)
            
            # Check if the playlist URLs already exist and append new ones
            playlist_urls_updated = []
            for playlist_url in playlist_urls:
                if playlist_url in urls:
                    print(f"URL already exists: {playlist_url}")
                    continue
                playlist_urls_updated.append(playlist_url)
            urls.extend(playlist_urls_updated)

        else:
            # Handle invalid input
            print("Invalid input. Please type '1' for URL, '2' for playlist, or 'STOP' to end.")

    # Print all URLs collected
    print(f"URLs collected: {urls}")

    # Save the updated list of URLs to the CSV file
    save_list_to_csv(urls, urls_csv)
    
    return urls_csv

def get_key(secret_key):
    # Load the .env file
    load_dotenv()

    # Access the variables
    key = os.getenv(secret_key)

    return key
    