import os
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .utils import create_directory_if_not_exists, split_audio_file, get_key, extract_video_urls_from_playlist
from .download_audio import download_youtube_audio
from .database import SessionLocal  # Import the session to interact with the database
from .database.models import Project, URL, AudioFile, Segment  # Import models
from pytubefix import YouTube

def yyt(project_name):
    """
    Create a new project if it doesn't exist, or continue with the existing project.

    Parameters:
    - project_name: The name of the project to create or retrieve.

    Returns:
    - The project instance.
    """
    # Ensure the data directory exists
    create_directory_if_not_exists(get_key('DATA_DIRECTORY'))

    # Replace spaces in the project name with underscores to ensure valid folder names
    project_name = project_name.replace(" ", "_")

    # Start a new session to interact with the database
    session = SessionLocal()
    
    try:
        # Check if a project with the given name already exists
        project = session.query(Project).filter_by(project_name=project_name).first()

        if project:
            # If the project exists, return it and notify the user
            print(f"\nContinuing with the existing project: {project.project_name}\n")
            return project
        else:
            # If the project doesn't exist, create a new one
            project_path = os.path.join(get_key('DATA_DIRECTORY'), project_name)
            new_project = Project(
                project_name=project_name,
                description="",  # You can modify this to accept descriptions if needed
                project_path=project_path
            )
            
            # Ensure the project folder exists on the file system
            create_directory_if_not_exists(project_path)
            print(f"Project Folder ready: {project_path}")
            
            # Add the new project to the session and commit to the database
            session.add(new_project)
            session.commit()

            # Refresh the project object to retrieve the generated project ID
            session.refresh(new_project)
            print(f"\nGreat! A new project '{new_project.project_name}' has been created with ID {new_project.project_id}.\n")
    
    except Exception as e:
        # Rollback changes if any error occurs
        session.rollback()
        print(f"\nAn error occurred: {str(e)}")
    
    finally:
        # Close the session to free resources
        session.close()

    return new_project


def urls(project_name, url_list):
    """
    Add new URLs to the project and display existing ones.

    Parameters:
    - project_name: The name of the project to associate URLs with.
    - url_list: A list of YouTube URLs to add to the project.
    """
    session = SessionLocal()

    try:
        # Retrieve the project by its name
        project = session.query(Project).filter_by(project_name=project_name).first()
        if not project:
            print(f"Project '{project_name}' does not exist in the database.")
            return

        # Display all existing URLs for the project
        if project.urls:
            print(f"The project '{project_name}' contains the following URLs:\n")
            for url_entry in project.urls:
                print(f"- {url_entry.url}")
        else:
            print(f"The project '{project_name}' has no saved URLs.")

        # Loop through the provided URLs
        for url in url_list:
            # Check if the URL already exists for this project
            existing_url = session.query(URL).filter_by(url=url, project_id=project.project_id).first()
            if existing_url:
                print(f"URL already exists: {url}")
                continue

            try:
                # Create a YouTube object to extract video metadata
                yt = YouTube(url)
            except Exception as e:
                print(f"""Failed to process the YouTube URL '{url}'. Error details: {e}.
                    Please check if the URL is valid and your internet connection is stable.""")
                continue

            # Create and add the new URL to the project
            new_url = URL(
                project_id=project.project_id,
                url=url,
                title=yt.title,
                author=yt.author,
                views=yt.views,
                description=yt.description
            )
            session.add(new_url)
            print(f"Added new URL : {url}")

        # Commit the new URLs to the database
        session.commit()
        print(f"URLs successfully updated for project '{project_name}'.")

    except Exception as e:
        # Rollback in case of an error
        session.rollback()
        print(f"An error occurred while managing URLs: {e}")
    finally:
        # Close the session
        session.close()


def playlist(project_name, playlist_list):
    """
    Extracts video URLs from YouTube playlists and adds them to a project.

    Parameters:
    - project_name: The name of the project to add URLs to.
    - playlist_list: A list of playlist URLs.
    """
    playlist_urls = []
    for playlist in playlist_list:
        # Extract video URLs from each playlist
        playlist_urls.extend(extract_video_urls_from_playlist(playlist))
    
    # Add the extracted URLs to the project
    urls(project_name, playlist_urls)


def download_audio(project_name):
    """
    Downloads audio for all URLs associated with a project.

    Parameters:
    - project_name: The name of the project whose audio needs to be downloaded.
    """
    session = SessionLocal()
    
    # Retrieve the project by name
    project = session.query(Project).filter_by(project_name=project_name).first()
    urls = project.urls  # Fetch associated URLs

    if not project:
        print(f"Project '{project_name}' does not exist in the database.")
        return

    if not urls:
        print(f"No URLs found for project '{project_name}'. Please add URLs first.")
        return
        
    # Download audio for each URL in the project
    for url_record in urls:
        url_id = url_record.url_id
        # Use the download_youtube_audio function to process the audio
        download_youtube_audio(url_id)


def segment_audio(project_name, segment_length_ms=10 * 60 * 1000):
    """
    Splits audio files associated with a project into segments.

    Parameters:
    - project_name: The name of the project whose audio needs to be segmented.
    - segment_length_ms: The length of each segment in milliseconds (default is 10 minutes).
    """
    session = SessionLocal()
    
    # Retrieve the project by name
    project = session.query(Project).filter_by(project_name=project_name).first()
    audio_files = project.audio_files  # Fetch associated audio files

    if not project:
        print(f"Project '{project_name}' does not exist in the database.")
        return

    if not audio_files:
        print(f"No Audio Files found for project '{project_name}'. Please add Audio Files first.")
        return
    
    # Segment each audio file in the project
    for audio_file in audio_files:
        audio_file_id = audio_file.audio_id
        audio_file_path = audio_file.audio_path
        audio_segments = session.query(Segment).filter_by(audio_id=audio_file_id).first()

        if audio_segments:
            print(f"Audio segments already exist for '{audio_file_path}'")
            continue

        # Call the split_audio_file function to create segments
        split_audio_file(audio_file_id, segment_length_ms)
