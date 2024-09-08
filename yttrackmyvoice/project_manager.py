import os
from yttrackmyvoice.utils import save_list_to_csv, load_list_from_csv, create_directory_if_not_exists,extract_video_urls_from_playlist
from yttrackmyvoice.download_audio import download_youtube_audio

def start_new_project(data_directory='data'):
    """Handles the creation of a new project and stores the project name in a CSV file."""
    
    create_directory_if_not_exists(data_directory)

    # Path to the CSV file that will store all project names
    project_csv = os.path.join(data_directory, 'projects.csv')
    
    # Check if the CSV file exists, if not create it
    if not os.path.exists(project_csv):
        # Create an empty CSV file if it doesn't exist
        with open(project_csv, 'w', newline='') as file:
            pass  # Just creating the file, no data written yet

    # Load all project names from the CSV file
    project_names = load_list_from_csv(project_csv)

    project_name = None

    while True:
        # Prompt user for a project name
        project_name = input("\nPlease enter a name for your new project: ").strip()

        # Replace spaces with underscores
        project_name = project_name.replace(" ", "_")
    
        # Check if any projects exist
        if project_name in project_names.values():
            print(f"\nA project with the name '{project_name}' already exists.")

            print("\nHere are the available projects:")
            for index, project in project_names.items():
                print(f"{index}. {project}")

            continue
        else:
            # If the project name doesn't exist, proceed with creating the new project
            print(f"\nGreat! A new project folder will be created as: {project_name}\n")

            # Append the project name to the CSV file
            save_list_to_csv([project_name], project_csv, "a")
            break  # Exit the loop when a valid new project name is provided

    return project_name


def continue_existing_project(data_directory='data'):
    """Handles continuing an existing project by displaying all project names."""
    
    # Path to the CSV file storing project names
    project_csv = os.path.join(data_directory, 'projects.csv')
    
    # Load all project names from the CSV file
    project_names = load_list_from_csv(project_csv)
    
    # Check if any projects exist
    if not project_names:
        print("\nNo projects found. Please start a new project first.")
        return None
    
    while True:
        # Display the available projects
        print("\nHere are the available projects:")
        for index, project in project_names.items():
            print(f"{index+1}. {project}")
        
        # Prompt the user for the project name
        project_name = input("\nPlease enter the name of the project you want to continue: ").strip()
        
        # Check if the entered project exists
        if project_name in project_names.values():
            print(f"\nContinuing with the existing project: {project_name}\n")
            return project_name
        else:
            print(f"\nNo project found with the name '{project_name}'. Please make sure to enter a valid project name.")
            return None  # Return None if the project doesn't exist


def get_urls(project_name, folder_path):
    urls = []

    # Path to the CSV file storing project URLs
    urls_csv = os.path.join(folder_path, 'urls.csv')

    urls_dict = load_list_from_csv(urls_csv)

    if urls_dict:
        urls = list(urls_dict.values())
        print(f"The project '{project_name}' contains the following URLs:\n")
        for url in urls:
            print(url)
    else:
        print(f"The project '{project_name}' has no saved URLs.")

    print("Would you like to submit a single video URL or a playlist URL?")
    print("Enter '1' for a single video, '2' for a playlist, or type 'STOP' to exit.")
    
    while True:
        choice = input("Enter your choice (1 for URL, 2 for playlist, 'STOP' to end): ")
        
        if choice.upper() == 'STOP':
            break
        
        if choice == '1':
            user_input = input("Enter the single URL (or type 'STOP' to end): ")
            if user_input.upper() == 'STOP':
                break
            if user_input in urls:
                print(f"Url already exists: {user_input}")
                continue
            urls.append(user_input)
        elif choice == '2':
            user_input = input("Enter the playlist URL (or type 'STOP' to end): ")
            if user_input.upper() == 'STOP':
                break
            playlist_urls = extract_video_urls_from_playlist(user_input)
            
            playlist_urls_updated = []
            for playlist_url in playlist_urls:
                if playlist_url in urls:
                    print(f"Url already exists: {playlist_url}")
                    continue
                playlist_urls_updated.append(playlist_url)
            urls.extend(playlist_urls_updated)
        else:
            print("Invalid input. Please type '1' for URL, '2' for playlist, or 'STOP' to end.")
    print(f"url equal to {urls}")
    save_list_to_csv(urls, urls_csv)
    return urls_csv


def start_project(project_name, data_directory='data'):

    folder_path = os.path.join(data_directory, project_name)
    create_directory_if_not_exists(folder_path)

    urls_csv = get_urls(project_name, folder_path)

    urls_dict = load_list_from_csv(urls_csv)

    for key, value in urls_dict.items():
        url = value
        
        # Generate a folder name for each URL, based on its index
        folder_name = f'{key}'
        
        # Create the folder path inside the main folder
        folder_path_video = os.path.join(folder_path, folder_name)
        
        # Check if the folder already exists
        if not os.path.exists(folder_path_video):
            os.makedirs(folder_path_video, exist_ok=True)
            print(f'Folder created: {folder_path_video}')
        else:
            print(f'Folder already exists: {folder_path_video}')

        download_youtube_audio(url, folder_path_video)