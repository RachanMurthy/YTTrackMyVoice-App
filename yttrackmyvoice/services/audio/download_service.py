import os
from yttrackmyvoice.database import SessionLocal
from yttrackmyvoice.database.models import URL
from yttrackmyvoice.services.audio.downloader import Downloader  # Import the Downloader class

class AudioDownloadService:
    def __init__(self, project):
        self.project = project

    def download_all_audio(self):
        """
        Downloads audio for all URLs associated with the project.
        """
        session = SessionLocal()
        try:
            # Ensure the project is attached to the session
            session.add(self.project)
            session.refresh(self.project)

            urls = session.query(URL).filter_by(project_id=self.project.project_id).all()

            if not urls:
                print(f"No URLs found for project '{self.project_name}'. Please add URLs first.")
                return

            downloader = Downloader()

            for url_record in urls:
                url_id = url_record.url_id
                downloader.download_youtube_audio(url_id)
        finally:
            session.close()
