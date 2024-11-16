from yttrackmyvoice.services.playback.playback_service import PlaybackService

class PlaybackManager:
    def __init__(self):
        self.playback_service = PlaybackService()

    def play_segments_by_label(self, label_name):
        self.playback_service.play_segments_by_label(label_name)