from yttrackmyvoice.download_audio import Downloader
from yttrackmyvoice.database import SessionLocal
from yttrackmyvoice.database.models import URL, AudioFile

class AudioManager:
    def __init__(self, project):
        self.project = project
        self.session = SessionLocal()
        self.downloader = Downloader()

    def download_all_audio(self):
        try:
            self.session.add(self.project)
            self.session.refresh(self.project)

            urls = self.session.query(URL).filter_by(project_id=self.project.project_id).all()

            if not urls:
                print(f"No URLs found for project '{self.project.project_name}'. Please add URLs first.")
                return

            for url_record in urls:
                url_id = url_record.url_id
                self.downloader.download_youtube_audio(url_id)
        finally:
            self.session.close()

    def segment_all_audio(self, segment_length_ms=2 * 60 * 1000):
        from math import ceil
        from yttrackmyvoice.segment_audio import Segmenter

        segmenter = Segmenter()
        try:
            self.session.add(self.project)
            self.session.refresh(self.project)

            audio_files = self.session.query(AudioFile).filter_by(project_id=self.project.project_id).all()

            if not audio_files:
                print(f"No audio files found for project '{self.project.project_name}'. Please add audio files first.")
                return

            for audio_file in audio_files:
                audio_file_id = audio_file.audio_id
                audio_file_path = audio_file.audio_path
                audio_segments = self.session.query(AudioFile).filter_by(audio_id=audio_file_id).first()

                if audio_segments:
                    print(f"Audio segments already exist for '{audio_file_path}'")
                    continue

                segmenter.split_audio_file(audio_file_id, segment_length_ms)
        finally:
            self.session.close() 