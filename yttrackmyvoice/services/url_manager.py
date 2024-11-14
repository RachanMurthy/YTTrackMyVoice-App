import os
from yttrackmyvoice.utils import create_directory_if_not_exists, extract_video_urls_from_playlist, get_key, get_url_title
from yttrackmyvoice.database import SessionLocal
from yttrackmyvoice.database.models import Project, URL, AudioFile
from pytubefix import YouTube

class URLManager:
    def __init__(self, project):
        self.project = project
        self.session = SessionLocal()

    def add_urls(self, url_list):
        try:
            self.session.add(self.project)
            self.session.refresh(self.project)

            urls = self.session.query(URL).filter_by(project_id=self.project.project_id).all()
            if urls:
                print(f"The project '{self.project.project_name}' contains the following URLs:\n")
                for url_entry in urls:
                    print(f"- {url_entry.url}")
            else:
                print(f"The project '{self.project.project_name}' has no saved URLs.")

            for url in url_list:
                existing_url = self.session.query(URL).filter_by(url=url, project_id=self.project.project_id).first()
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
                self.session.add(new_url)
                print(f"Added new URL: {url}")

            self.session.commit()
            print(f"URLs successfully updated for project '{self.project.project_name}'.")
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred while managing URLs: {e}")
        finally:
            self.session.close()

    def add_playlists(self, playlist_list):
        try:
            playlist_urls = []
            for playlist in playlist_list:
                playlist_urls.extend(extract_video_urls_from_playlist(playlist))
            self.add_urls(playlist_urls)
        except Exception as e:
            print(f"An error occurred while adding playlists: {e}") 