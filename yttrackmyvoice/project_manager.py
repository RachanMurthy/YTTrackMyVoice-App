import os
from .utils import save_list_to_csv, load_list_from_csv, create_directory_if_not_exists, get_urls
from .download_audio import download_youtube_audio

def new_project(data_directory='data'):
    """
    Handles the creation of a new project and stores the project name in a CSV file.
    
    Parameters:
    - data_directory: Directory where the project data will be stored (default is 'data').
    
    Returns:
    - The name of the newly created project.
    """
    
    # Ensure the data directory exists
    create_directory_if_not_exists(data_directory)

    # Path to the CSV file that will store all project names
    project_csv = os.path.join(data_directory, 'projects.csv')
    
    # Check if the CSV file exists, if not create it
    if not os.path.exists(project_csv):
        # Create an empty CSV file if it doesn't exist
        with open(project_csv, 'w', newline='') as file:
            pass  # Just creating the file, no data written yet

    # Load all existing project names from the CSV file
    project_names = load_list_from_csv(project_csv)

    project_name = None

    # Loop to get a valid project name
    while True:
        # Prompt user for a project name
        project_name = input("\nPlease enter a name for your new project: ").strip()

        # Replace spaces with underscores
        project_name = project_name.replace(" ", "_")
    
        # Check if the project name already exists
        if project_name in project_names.values():
            print(f"\nA project with the name '{project_name}' already exists.")

            # Display existing projects
            print("\nHere are the available projects:")
            for index, project in project_names.items():
                print(f"{index}. {project}")

            continue  # Loop again to get a new project name
        else:
            # If the project name doesn't exist, proceed with creating the new project
            print(f"\nGreat! A new project folder will be created as: {project_name}\n")

            # Append the project name to the CSV file
            save_list_to_csv([project_name], project_csv, "a")
            break  # Exit the loop once a valid project name is provided

    return project_name


def continue_project(data_directory='data'):
    """
    Handles continuing an existing project by displaying the available projects 
    and allowing the user to select one.
    
    Parameters:
    - data_directory: Directory where the project data is stored (default is 'data').
    
    Returns:
    - The name of the project to continue, or None if no valid project is found.
    """
    
    # Ensure the data directory exists
    create_directory_if_not_exists(data_directory)

    # Path to the CSV file containing project names
    project_csv = os.path.join(data_directory, 'projects.csv')
    
    # Load all existing project names from the CSV file
    project_names = load_list_from_csv(project_csv)
    
    # Check if any projects exist
    if not project_names:
        print("\nNo projects found. Please start a new project first.")
        return None
    
    # Loop to get a valid project name
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


def start_project(project_name, data_directory='data'):
    """
    Starts the project by managing folder creation and downloading YouTube audio
    for the specified project.

    Parameters:
    - project_name: The name of the project.
    - data_directory: Directory where the project data is stored (default is 'data').
    """
    
    # Path to the project folder
    folder_path = os.path.join(data_directory, project_name)
    
    # Ensure the project folder exists
    create_directory_if_not_exists(folder_path)

    # Get the URLs CSV for the project
    urls_csv = get_urls(project_name, folder_path)

    # Load URLs from the CSV
    urls_dict = load_list_from_csv(urls_csv)

    # Loop through all URLs and process them
    for key, value in urls_dict.items():
        url = value
        
        # Generate a folder name for each URL, based on its index
        folder_name = f'{key}'
        
        # Create the folder path inside the main project folder
        folder_path_video = os.path.join(folder_path, folder_name)
        
        # Check if the folder already exists
        if not os.path.exists(folder_path_video):
            os.makedirs(folder_path_video, exist_ok=True)
            print(f'Folder created: {folder_path_video}')
        else:
            print(f'Folder already exists: {folder_path_video}')

        # Download the audio from the YouTube URL
        download_youtube_audio(url, folder_path_video)


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