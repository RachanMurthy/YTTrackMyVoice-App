from yttrackmyvoice.services.url.url_service import URLService

class URLManager:
    def __init__(self, project):
        self.project = project
        self.url_service = URLService(self.project)

    def add_urls(self, url_list):
        self.url_service.add_urls(url_list)

    def add_playlists(self, playlist_list):
        self.url_service.add_playlists(playlist_list)