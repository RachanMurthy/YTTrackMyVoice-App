import os
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .utils import create_directory_if_not_exists, split_audio_file, get_key, extract_video_urls_from_playlist
from .download_audio import download_youtube_audio
from .database import SessionLocal  # Import the session
from .database.models import Project, URL, AudioFile, Segment  # Import the Project model
from pytubefix import YouTube

def yyt(project_name):

    # Ensure the data directory exists
    create_directory_if_not_exists(get_key('DATA_DIRECTORY'))

    # Replace spaces with underscores
    project_name = project_name.replace(" ", "_")

    # Create a session
    session = SessionLocal()
    
    try:
        # Check if the project already exists
        project = session.query(Project).filter_by(project_name=project_name).first()

        if project:
            # If the project already exists, return and print a message
            print(f"\nContinuing with the existing project: {project.project_name}\n")
            return project
        else:
            # If project doesn't exist, create a new one
            project_path = os.path.join(get_key('DATA_DIRECTORY'), project_name)
            new_project = Project(
                        project_name=project_name,
                        description="",  # Modify this if you need to collect a description
                        project_path=project_path
            )
            
            # Ensure the folder exists
            create_directory_if_not_exists(project_path)
            print(f"Project Folder ready: {project_path}")
            
            # Add the new project to the session and commit the changes
            session.add(new_project)
            session.commit()

            # Refresh the object to get the new project ID
            session.refresh(new_project)  
            print(f"\nGreat! A new project '{new_project.project_name}' has been created with ID {new_project.project_id}.\n")
    
    except Exception as e:
        # Catch any unforeseen errors and roll back the session
        session.rollback()
        print(f"\nAn error occurred: {str(e)}")

    finally:
        # Close the session to free resources
        session.close()

    return new_project


def urls(project_name, url_list):

    session = SessionLocal()

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
                print(f"- {url_entry.url}")
        else:
            print(f"The project '{project_name}' has no saved URLs.")

        # Iterate through playlist URLs
        for url in url_list:
            existing_url = session.query(URL).filter_by(url=url, project_id=project.project_id).first()
            if existing_url:
                print(f"URL already exists: {url}")
                continue

            try:
                yt = YouTube(url)
            except Exception as e:
                print(f"""Failed to process the YouTube URL '{url}'. Error details: {e}.
                    Please check if the URL is valid and your internet connection is stable.""")

            # Append the new URL
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

        # Commit all new URLs to the database
        session.commit()

        # Optionally, update the folder structure or perform other operations here
        print(f"URLs successfully updated for project '{project_name}'.")

    except Exception as e:
        session.rollback()
        print(f"An error occurred while managing URLs: {e}")
    finally:
        session.close()


def playlist(project_name, playlist_list):
    playlist_urls = []
    for playlist in playlist_list:
        playlist_urls.extend(extract_video_urls_from_playlist(playlist))
    
    urls(project_name, playlist_urls)


def download_audio(project_name):
        
    session = SessionLocal()
    # Retrieve the project from the database
    project = session.query(Project).filter_by(project_name=project_name).first()
    urls = project.urls

    if not project:
        print(f"Project '{project_name}' does not exist in the database.")
        return

    if not urls:
        print(f"No URLs found for project '{project_name}'. Please add URLs first.")
        return
        
    # Iterate through each URL and process it
    for url_record in urls:
        url_id = url_record.url_id
        # Download the audio from the YouTube URL
        download_youtube_audio(url_id)


def segment_audio(project_name, segment_length_ms=10 * 60 * 1000):
    session = SessionLocal()
    # Retrieve the project from the database
    project = session.query(Project).filter_by(project_name=project_name).first()
    audio_files = project.audio_files

    if not project:
        print(f"Project '{project_name}' does not exist in the database.")
        return

    if not audio_files:
        print(f"No Audio Files found for project '{project_name}'. Please add Audio File first.")
        return
    
    for audio_file in audio_files:
        audio_file_id = audio_file.audio_id
        audio_file_path = audio_file.audio_path
        audio_segments = session.query(Segment).filter_by(audio_id=audio_file_id).first()

        if audio_segments:
            print(f"audio segments exist for '{audio_file_path}'")
            continue

        # Split the audio into segments and get segment information
        split_audio_file(audio_file_id, segment_length_ms)