from yttrackmyvoice import Yyt

if __name__ == "__main__":
    # Initialize the Yyt class with your project name
    manager = Yyt("school")  
    # manager.add_urls(["https://www.youtube.com/watch?v=Ir0eO9H8P7k&pp=ygUOc2lkZW1lbiByZWFjdHM%3D"])
    # manager.download_all_audio()
    manager.segment_all_audio(segment_length_ms=30 * 60 * 1000)
    manager.embed_all_audio()

    # Existing features (uncomment as needed)
    # manager.add_urls(["https://www.youtube.com/watch?v=cO8-_Eedjfk&pp=ygUJam9lIHJvZ2Fu"])
    # manager.download_all_audio()
    # manager.segment_all_audio(segment_length_ms=30 * 60 * 1000)  # Segments of 30 minutes
    # manager.embed_all_audio()
    # embeddings, labels = Yyt.retrieve_all_embeddings()
    # print(embeddings, labels)
    # manager.cluster_and_label_embeddings()
    # target_label = "Speaker 19"  # Replace with your desired label name
    # manager.get_label_info(target_label)
    # manager.list_labels()
    # manager.segment_audio_using_embeddings_timestamps()
    # manager.transcribe_final_segments()

    # New Feature: Listen to all segments of a specific speaker
    # speaker_label = input("Enter the speaker label you want to listen to (e.g., 'Speaker 1'): ")
    # manager.play_segments_by_label(speaker_label)
