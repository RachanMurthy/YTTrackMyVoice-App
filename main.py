from yttrackmyvoice import Yyt

if __name__ == "__main__":
    # Initialize the Yyt2 class with your project name
    manager = Yyt("school")
    manager.add_urls(["https://www.youtube.com/watch?v=Ir0eO9H8P7k&pp=ygUOc2lkZW1lbiByZWFjdHM%3D"])
    manager.download_all_audio()
    manager.segment_all_audio(segment_length_ms=3 * 60 * 1000)
    manager.embed_all_audio()
    manager.cluster_and_label_embeddings(distance_threshold=1.0)
    manager.segment_audio_using_embeddings_timestamps()
    manager.transcribe_final_segments()
    manager.list_labels()
    manager.play_segments_by_label("Speaker 1")