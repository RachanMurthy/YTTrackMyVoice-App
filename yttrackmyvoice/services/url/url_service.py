from pytubefix import YouTube, Playlist
from yttrackmyvoice.database import SessionLocal
from yttrackmyvoice.database.models import URL
from yttrackmyvoice.utils import extract_video_urls_from_playlist

class URLService:
    def __init__(self, project):
        self.project = project

    def add_urls(self, url_list):
        """
        Add new URLs to the project and display existing ones.

        Parameters:
        - url_list: A list of YouTube URLs to add to the project.
        """
        session = SessionLocal()
        try:
            # Ensure the project is attached to the session
            session.add(self.project)
            session.refresh(self.project)

            # Display existing URLs
            urls = session.query(URL).filter_by(project_id=self.project.project_id).all()
            if urls:
                print(f"The project '{self.project.project_name}' contains the following URLs:\n")
                for url_entry in urls:
                    print(f"- {url_entry.url}")
            else:
                print(f"The project '{self.project.project_name}' has no saved URLs.")

            # Add new URLs
            for url in url_list:
                existing_url = session.query(URL).filter_by(url=url, project_id=self.project.project_id).first()
                if existing_url:
                    print(f"URL already exists: {url}")
                    continue

                try:
                    yt = YouTube(url)
                except Exception as e:
                    print(f"Failed to process the YouTube URL '{url}'. Error details: {e}.")
                    continue

                new_url = URL(
                    project_id=self.project.project_id,
                    url=url,
                    title=yt.title,
                    author=yt.author,
                    views=yt.views
                )
                session.add(new_url)
                print(f"Added new URL: {url}")

            session.commit()
            print(f"URLs successfully updated for project '{self.project.project_name}'.")
        except Exception as e:
            session.rollback()
            print(f"An error occurred while managing URLs: {e}")
        finally:
            session.close()

    def add_playlists(self, playlist_list):
        """
        Extracts video URLs from YouTube playlists and adds them to the project.

        Parameters:
        - playlist_list: A list of playlist URLs.
        """
        playlist_urls = []
        for playlist in playlist_list:
            playlist_urls.extend(extract_video_urls_from_playlist(playlist))

        self.add_urls(playlist_urls)

    @staticmethod
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