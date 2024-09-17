import os
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .utils import create_directory_if_not_exists, get_urls, split_audio_file
from .download_audio import download_youtube_audio
from .database import SessionLocal  # Import the session
from .database.models import Project, URL, AudioFile, Segment  # Import the Project model

def new_project(data_directory='data'):
    """
    Handles the creation of a new project and stores the project in the database.

    Parameters:
    - data_directory: Directory where the project data will be stored (default is 'data').

    Returns:
    - The name of the newly created project.
    """
    # Ensure the data directory exists
    create_directory_if_not_exists(data_directory)

    # Create a new database session
    session: Session = SessionLocal()

    try:
        project_name = None

        while True:
            # Prompt user for a project name
            project_name = input("\nPlease enter a name for your new project: ").strip()

            # Replace spaces with underscores
            project_name = project_name.replace(" ", "_")

            if not project_name:
                print("Project name cannot be empty. Please try again.")
                continue

            # Check if the project name already exists in the database
            existing_project = session.query(Project).filter_by(project_name=project_name).first()

            if existing_project:
                print(f"\nA project with the name '{project_name}' already exists.")

                # Optionally, display existing projects
                print("\nHere are the available projects:")
                all_projects = session.query(Project).all()
                for project in all_projects:
                    print(f"{project.project_id}. {project.project_name}")

                continue  # Loop again to get a new project name
            else:
                # Define the project path
                project_path = os.path.join(data_directory, project_name)

                # Create the project directory
                create_directory_if_not_exists(project_path)

                # Create a new Project instance
                new_project = Project(
                    project_name=project_name,
                    description="",  # You can modify this to collect a description if needed
                    project_path=project_path
                )

                # Add the new project to the session
                session.add(new_project)

                try:
                    # Commit the transaction to save the project in the database
                    session.commit()
                    session.refresh(new_project)  # Refresh to get the generated project_id
                    print(f"\nGreat! A new project '{new_project.project_name}' has been created with ID {new_project.project_id}.\n")
                    break  # Exit the loop once a valid project is created
                except IntegrityError:
                    # Handle the case where the project name is not unique
                    session.rollback()
                    print(f"\nA project with the name '{project_name}' already exists. Please choose a different name.")
                    continue

        return new_project.project_name

    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        # Close the session to free up resources
        session.close()


def continue_project(data_directory='data'):
    """
    Handles continuing an existing project by displaying the available projects 
    and allowing the user to select one by name.

    Parameters:
    - data_directory: Directory where the project data is stored (default is 'data').

    Returns:
    - The name of the project to continue, or None if no valid project is found.
    """
    # Ensure the data directory exists
    create_directory_if_not_exists(data_directory)

    # Create a new database session
    session: Session = SessionLocal()

    try:
        # Query all existing projects from the database
        projects = session.query(Project).all()

        # Check if any projects exist
        if not projects:
            print("\nNo projects found. Please start a new project first.")
            return None

        while True:
            # Display the available projects
            print("\nHere are the available projects:")
            for project in projects:
                print(f"- {project.project_name}")

            # Prompt the user for the project name
            project_name = input("\nPlease enter the name of the project you want to continue: ").strip()

            # Check if the entered project exists (case-sensitive)
            selected_project = session.query(Project).filter_by(project_name=project_name).first()

            if selected_project:
                print(f"\nContinuing with the existing project: {selected_project.project_name}\n")
                return selected_project.project_name
            else:
                print(f"\nNo project found with the name '{project_name}'. Please enter a valid project name.")
                # Optionally, you can ask the user to try again or exit
                retry = input("Would you like to try again? (y/n): ").strip().lower()
                if retry != 'y':
                    print("Exiting project continuation.")
                    return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        # Close the session to free up resources
        session.close()


def start_project(project_name, data_directory='data'):
    """
    Starts the project by managing folder creation, downloading YouTube audio,
    splitting audio into segments, and updating the database with segments.

    Parameters:
    - project_name (str): The name of the project.
    - data_directory (str): Directory where the project data is stored (default is 'data').

    Returns:
    - None
    """
    # Define the main project folder path
    project_folder_path = os.path.join(data_directory, project_name)

    # Ensure the main project folder exists
    create_directory_if_not_exists(project_folder_path)
    print(f"Project directory ensured at: {project_folder_path}")

    # Create a new database session
    session: Session = SessionLocal()

    try:
        # Retrieve the project from the database
        project = session.query(Project).filter_by(project_name=project_name).first()
        if not project:
            print(f"Project '{project_name}' does not exist in the database.")
            return

        # Retrieve all URLs associated with the project
        get_urls(project_name)
        urls = project.urls

        if not urls:
            print(f"No URLs found for project '{project_name}'. Please add URLs first.")
            return

        # Iterate through each URL and process it
        for url_entry in urls:
            url = url_entry.url
            url_type = url_entry.url_type

            # Generate a unique folder name based on URL ID
            folder_name = f"url_{url_entry.id}"

            # Define the folder path for this URL
            folder_path_video = os.path.join(project_folder_path, folder_name)

            # Ensure the folder exists
            create_directory_if_not_exists(folder_path_video)
            print(f"Folder ready: {folder_path_video}")

            # Download the audio from the YouTube URL
            audio_file_path, duration = download_youtube_audio(url, folder_path_video)

            if not audio_file_path:
                print(f"Failed to download audio for URL: {url}")
                continue  # Skip to the next URL

            # Split the audio into segments and get segment information
            folder_path_video = os.path.join(folder_path_video, "segments")
            segments_info = split_audio_file(audio_file_path, folder_path_video, format="wav")

            # Create a new AudioFile record
            audio_file = AudioFile(
                project_id=project.project_id,
                url_id=url_entry.id,  # Associate with the specific URL
                url_name=folder_name,
                file_name=os.path.basename(audio_file_path),
                audio_path=audio_file_path,
                duration_seconds=duration
            )

            # Add the AudioFile to the session
            session.add(audio_file)
            session.flush()  # Flush to assign an audio_id to audio_file

            # Create Segment records
            for segment in segments_info:
                segment_file_name = f"{os.path.splitext(audio_file.file_name)[0]}_{segment['segment_number']}.{os.path.splitext(segment['file_name'])[1].lstrip('.')}"
                segment_file_path = os.path.join(folder_path_video, segment_file_name)

                # Rename the segment file to match the desired naming convention if necessary
                if os.path.exists(segment['file_path']):
                    os.rename(segment['file_path'], segment_file_path)
                else:
                    print(f"Segment file not found: {segment['file_path']}")
                    continue  # Skip this segment

                # Create a new Segment instance
                new_segment = Segment(
                    audio_id=audio_file.audio_id,
                    start_time=segment['start_time'],
                    end_time=segment['end_time'],
                    duration=segment['duration'],
                    file_path=segment_file_path,
                    file_name=segment_file_name
                )

                # Add the Segment to the session
                session.add(new_segment)
                print(f"Segment '{segment_file_name}' added to the database.")

            print(f"Audio file '{audio_file.file_name}' and its segments have been added to the database.")

        # Commit all new records to the database
        session.commit()
        print(f"Project '{project_name}' has been started successfully.")

    except Exception as e:
        session.rollback()
        print(f"An error occurred while starting the project: {e}")
    finally:
        session.close()