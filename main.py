from yttrackmyvoice import Yyt

if __name__ == "__main__":
    # Initialize the Yyt facade with your project name
    manager = Yyt("school")  
    
    # Example Usage:
    # Add URLs
    # manager.add_urls(["https://www.youtube.com/watch?v=Ir0eO9H8P7k&pp=ygUOc2lkZW1lbiByZWFjdHM%3D"])
    
    # Download Audio
    # manager.download_all_audio()
    
    # Segment Audio with segments of 30 minutes
    manager.segment_all_audio(segment_length_ms=30 * 60 * 1000)
    
    # Generate Embeddings
    manager.embed_all_audio()
    
    # Cluster and Label Embeddings
    # manager.cluster_and_label_embeddings(distance_threshold=1)
    
    # Transcribe Final Segments
    # manager.transcribe_final_segments()
    
    # Play Segments by Label
    # speaker_label = input("Enter the speaker label you want to listen to (e.g., 'Speaker 1'): ")
    # manager.play_segments_by_label(speaker_label)
    
    # List Labels
    # manager.list_labels()
    
    # Update Label Name
    # manager.update_label_name("Old Label", "New Label")
