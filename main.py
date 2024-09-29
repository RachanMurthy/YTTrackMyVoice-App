from yttrackmyvoice import Yyt

if __name__ == "__main__":
    # Initialize the Yyt class with your project name
    manager = Yyt("My Project")  # This will create or retrieve the project

    # You no longer need to call create_or_get_project()

    # Add URLs to the project
    manager.add_urls(["https://www.youtube.com/watch?v=OXLD2KWbdbA"])

    # # Add playlists to the project
    # manager.add_playlists(["https://www.youtube.com/playlist?list=example"])

    # Download all audio files for the project
    manager.download_all_audio()

    # Segment all audio files
    manager.segment_all_audio(segment_length_ms=2 * 60 * 1000)  # Segments of 2 minutes

    # Generate embeddings for all audio segments
    manager.embed_all_audio()

    # Retrieve all embeddings
    embeddings, labels = Yyt.retrieve_all_embeddings()

    print(embeddings, labels)