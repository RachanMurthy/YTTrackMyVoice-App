from yttrackmyvoice import Yyt

if __name__ == "__main__":
    # Initialize the Yyt class with your project name
    manager = Yyt("My Project")  # This will create or retrieve the project

    # # Add URLs to the project
    # manager.add_urls(["https://www.youtube.com/watch?v=u_2H_9pyiEY"])

    # # Download all audio files for the project
    # manager.download_all_audio()

    # # Segment all audio files
    # manager.segment_all_audio(segment_length_ms=2 * 60 * 1000)  # Segments of 2 minutes

    # # Generate embeddings for all audio segments
    # manager.embed_all_audio()

    # # Retrieve all embeddings
    # embeddings, labels = Yyt.retrieve_all_embeddings()

    # print(embeddings, labels)

    # # Perform clustering and labeling using the Yyt instance
    # manager.cluster_and_label_embeddings()

     # Specify the label name you want to retrieve information for
    target_label = "Speaker 19"  # Replace with your desired label name

    # Retrieve and display detailed information for the specified label
    manager.get_label_info(target_label)

    # List all existing labels
    manager.list_labels()

