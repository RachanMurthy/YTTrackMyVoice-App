import os
from sqlalchemy.exc import SQLAlchemyError
from .utils import (
    create_directory_if_not_exists,
    get_key,
    extract_video_urls_from_playlist,
    get_url_title
)
from .database import SessionLocal
from .database.models import Project, URL, AudioFile, Segment, Embedding, EmbeddingTimestamp, LabelName, EmbeddingLabel
from pytubefix import YouTube
import numpy as np
from .download_audio import Downloader
from .segment_audio import Segmenter
from .embed_audio import Embedder  
from .label_embeddings import EmbeddingLabeler

class Yyt:
    def __init__(self, project_name):
        """
        Initializes the Yyt class by creating or retrieving a project.

        Parameters:
        - project_name: The name of the project to create or retrieve.
        """
        # Ensure the data directory exists
        create_directory_if_not_exists(get_key('DATA_DIRECTORY'))

        # Replace spaces in the project name with underscores
        self.project_name = project_name.replace(" ", "_")
        self.project = None  # Will hold the Project instance

        # Create or get the project upon initialization
        self._create_or_get_project()

    def _create_or_get_project(self):
        """
        Create a new project if it doesn't exist, or continue with the existing project.
        This method is called during initialization.
        """
        session = SessionLocal()
        try:
            # Check if the project already exists
            project = session.query(Project).filter_by(project_name=self.project_name).first()

            if project:
                print(f"\nContinuing with the existing project: {project.project_name}\n")
                self.project = project
            else:
                # Create a new project
                project_path = os.path.join(get_key('DATA_DIRECTORY'), self.project_name)
                new_project = Project(
                    project_name=self.project_name,
                    description="",
                    project_path=project_path
                )
                create_directory_if_not_exists(project_path)
                print(f"Project Folder ready: {project_path}")

                session.add(new_project)
                session.commit()
                session.refresh(new_project)
                self.project = new_project
                print(f"\nGreat! A new project '{new_project.project_name}' has been created with ID {new_project.project_id}.\n")
        except Exception as e:
            session.rollback()
            print(f"\nAn error occurred during project creation: {str(e)}")
            # Optionally, re-raise the exception or handle it appropriately
        finally:
            session.close()

    def add_urls(self, url_list):
        """
        Add new URLs to the project and display existing ones.

        Parameters:
        - url_list: A list of YouTube URLs to add to the project.
        """
        session = SessionLocal()
        try:
            # Ensure the project is attached to the session
            session.add(self.project)
            session.refresh(self.project)

            # Display existing URLs
            urls = session.query(URL).filter_by(project_id=self.project.project_id).all()
            if urls:
                print(f"The project '{self.project_name}' contains the following URLs:\n")
                for url_entry in urls:
                    print(f"- {url_entry.url}")
            else:
                print(f"The project '{self.project_name}' has no saved URLs.")

            # Add new URLs
            for url in url_list:
                existing_url = session.query(URL).filter_by(url=url, project_id=self.project.project_id).first()
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
                session.add(new_url)
                print(f"Added new URL: {url}")

            session.commit()
            print(f"URLs successfully updated for project '{self.project_name}'.")
        except Exception as e:
            session.rollback()
            print(f"An error occurred while managing URLs: {e}")
        finally:
            session.close()

    def add_playlists(self, playlist_list):
        """
        Extracts video URLs from YouTube playlists and adds them to the project.

        Parameters:
        - playlist_list: A list of playlist URLs.
        """
        playlist_urls = []
        for playlist in playlist_list:
            playlist_urls.extend(extract_video_urls_from_playlist(playlist))

        self.add_urls(playlist_urls)

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

    def segment_all_audio(self, segment_length_ms=2 * 60 * 1000):
        """
        Splits audio files associated with the project into segments.

        Parameters:
        - segment_length_ms: The length of each segment in milliseconds.
        """
        session = SessionLocal()
        try:
            # Ensure the project is attached to the session
            session.add(self.project)
            session.refresh(self.project)

            audio_files = session.query(AudioFile).filter_by(project_id=self.project.project_id).all()

            if not audio_files:
                print(f"No audio files found for project '{self.project_name}'. Please add audio files first.")
                return

            segmenter = Segmenter()  # Create an instance of the Segmenter class

            for audio_file in audio_files:
                audio_file_id = audio_file.audio_id
                audio_file_path = audio_file.audio_path
                audio_segments = session.query(Segment).filter_by(audio_id=audio_file_id).first()

                if audio_segments:
                    print(f"Audio segments already exist for '{audio_file_path}'")
                    continue

                segmenter.split_audio_file(audio_file_id, segment_length_ms)
        finally:
            session.close()

    def embed_all_audio(self):
        """
        Generates embeddings for all audio segments associated with the project.
        """
        session = SessionLocal()
        try:
            # Ensure the project is attached to the session
            session.add(self.project)
            session.refresh(self.project)

            audio_files = session.query(AudioFile).filter_by(project_id=self.project.project_id).all()

            if not audio_files:
                print(f"No audio files found for project '{self.project_name}'. Please add audio files first.")
                return

            embedder = Embedder()  # Create an instance of the Embedder class

            for audio_file in audio_files:
                segment_files = session.query(Segment).filter_by(audio_id=audio_file.audio_id).all()
                for segment_file in segment_files:
                    segment_id = segment_file.segment_id
                    segment_file_path = segment_file.file_path
                    segment_embeddings = session.query(Embedding).filter_by(segment_id=segment_id).first()

                    if segment_embeddings:
                        print(f"Embeddings already exist for '{segment_file_path}'")
                        continue

                    embedder.store_embedding_and_timestamp(segment_id)
        finally:
            session.close()

    @staticmethod
    def retrieve_all_embeddings(segment_ids=None):
        """
        Retrieves all embeddings and their corresponding timestamps from the database.
        If segment_ids is provided, retrieves embeddings only for those segments.

        Args:
        - segment_ids (List[int], optional): A list of segment IDs to retrieve embeddings for.

        Returns:
        - embeddings_list (List[np.ndarray]): A list of embedding vectors.
        - labels_list (List[Dict]): A list of dictionaries containing metadata.
        """
        session = SessionLocal()
        try:
            print("Retrieving embeddings from the database.")

            query = session.query(Embedding)
            if segment_ids:
                query = query.filter(Embedding.segment_id.in_(segment_ids))
            
            embeddings = query.all()
            if not embeddings:
                print("No embeddings found in the database.")
                return [], []

            embeddings_list = []
            labels_list = []

            for embedding in embeddings:
                embedding_vector = np.frombuffer(embedding.vector, dtype=np.float32)

                timestamps = session.query(EmbeddingTimestamp).filter_by(embedding_id=embedding.embedding_id).all()

                timestamp_list = []
                for ts in timestamps:
                    timestamp_info = { 
                        'start_time': ts.start_time,
                        'end_time': ts.end_time,
                        'created_at': ts.created_at
                    }
                    timestamp_list.append(timestamp_info)

                embedding_info = {
                    'embedding_id': embedding.embedding_id,
                    'segment_id': embedding.segment_id,
                    'timestamps': timestamp_list,
                    'created_at': embedding.created_at
                }

                embeddings_list.append(embedding_vector)
                labels_list.append(embedding_info)

            print(f"Total embeddings retrieved: {len(embeddings_list)}")
            return embeddings_list, labels_list
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            return [], []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return [], []
        finally:
            session.close()

    def cluster_and_label_embeddings(self, distance_threshold=1):
        """
        Clusters and labels embeddings for the project.

        Parameters:
        - distance_threshold: The distance threshold for clustering (default is 5).
        """
        labeler = EmbeddingLabeler(distance_threshold=distance_threshold)
        labeler.cluster_and_label_embeddings()

    def list_labels(self):
        """
        Lists all existing labels along with the number of embeddings associated with each label.
        """
        session = SessionLocal()
        try:
            labels = session.query(LabelName).all()
            if not labels:
                print("No labels found in the database.")
                return

            print("Existing Labels:")
            for label in labels:
                count = session.query(EmbeddingLabel).filter_by(label_id=label.label_id).count()
                print(f"- {label.label_name} (Total Embeddings: {count})")
        except SQLAlchemyError as e:
            print(f"Database error occurred while listing labels: {e}")
        finally:
            session.close()

    def update_label_name(self, old_label_name, new_label_name):
        """
        Updates the name of a label after verifying its existence.

        Parameters:
        - old_label_name (str): The current name of the label.
        - new_label_name (str): The new name for the label.
        """
        session = SessionLocal()
        try:
            # Check if the old label exists
            label = session.query(LabelName).filter_by(label_name=old_label_name).first()
            if not label:
                print(f"Label '{old_label_name}' does not exist.")
                return

            # Check if the new label name already exists
            existing_label = session.query(LabelName).filter_by(label_name=new_label_name).first()
            if existing_label:
                print(f"Label name '{new_label_name}' is already in use.")
                return

            # Update the label name
            label.label_name = new_label_name
            session.commit()
            print(f"Label name updated from '{old_label_name}' to '{new_label_name}'.")
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error occurred while updating label name: {e}")
        finally:
            session.close()

    def get_label_info(self, label_name):
        """
        Retrieves detailed information for a specific label, including title from URL, audio ID, segment ID,
        start time, and end time.

        Parameters:
        - label_name (str): The name of the label to retrieve information for.

        Returns:
        - None
        """
        session = SessionLocal()
        try:
            # Retrieve the specified label
            label = session.query(LabelName).filter_by(label_name=label_name).first()
            if not label:
                print(f"Label '{label_name}' does not exist.")
                return

            print(f"\nRetrieving information for Label: {label.label_name}\n")

            # Fetch all EmbeddingLabels associated with the label
            embedding_labels = session.query(EmbeddingLabel).filter_by(label_id=label.label_id).all()

            # Collect detailed information
            detailed_info = []
            for embedding_label in embedding_labels:
                embedding = embedding_label.embedding
                for ts in embedding.timestamps:
                    segment = embedding.segment
                    if not segment:
                        continue  # Skip if segment is not found

                    # Retrieve the title from the associated URL via AudioFile
                    title = get_url_title(segment.audio_id, session)

                    detailed_info.append({
                        'title': title,
                        'audio_id': segment.audio_id,
                        'segment_id': segment.segment_id,
                        'start_time': ts.start_time,
                        'end_time': ts.end_time
                    })

            if not detailed_info:
                print(f"No timestamps found for label '{label.label_name}'.")
                return

            # Display the collected detailed information
            for info in detailed_info:
                print(f"Title: {info['title']}")
                print(f"Audio ID: {info['audio_id']}")
                print(f"Segment ID: {info['segment_id']}")
                print(f"Start Time: {info['start_time']:.2f}s")
                print(f"End Time: {info['end_time']:.2f}s")
                print("-" * 60)

        except SQLAlchemyError as e:
            print(f"Database error occurred while retrieving label info: {e}")
        finally:
            session.close()

    def retrieve_embeddings_for_audio_files(self, audio_file_ids):
        """
        Retrieves embeddings associated with the specified audio file IDs.

        Args:
        - audio_file_ids (List[int]): A list of audio file IDs.

        Returns:
        - embeddings_list (List[np.ndarray]): A list of embedding vectors.
        - labels_list (List[Dict]): A list of dictionaries containing metadata, including audio_file_id.
        """
        session = SessionLocal()
        try:
            print("Retrieving embeddings for specified audio files from the database.")

            # Retrieve segments associated with the specified audio files
            segments = session.query(Segment).filter(Segment.audio_id.in_(audio_file_ids)).all()

            if not segments:
                print("No segments found for the specified audio files.")
                return [], []

            # Create a mapping from segment_id to audio_file_id for quick lookup
            segment_id_map = {segment.segment_id: segment.audio_id for segment in segments}

            segment_ids = [segment.segment_id for segment in segments]

            # Now retrieve embeddings for these segments
            embeddings = session.query(Embedding).filter(Embedding.segment_id.in_(segment_ids)).all()

            if not embeddings:
                print("No embeddings found for the specified segments.")
                return [], []

            embeddings_list = []
            labels_list = []

            for embedding in embeddings:
                # Deserialize the embedding vector
                embedding_vector = np.frombuffer(embedding.vector, dtype=np.float32)

                # Retrieve timestamps associated with the embedding
                timestamps = session.query(EmbeddingTimestamp).filter_by(embedding_id=embedding.embedding_id).all()

                timestamp_list = []
                for ts in timestamps:
                    timestamp_info = { 
                        'start_time': ts.start_time,
                        'end_time': ts.end_time,
                        'created_at': ts.created_at
                    }
                    timestamp_list.append(timestamp_info)

                # Get the audio_file_id from the segment_id_map
                audio_file_id = segment_id_map.get(embedding.segment_id, None)

                embedding_info = {
                    'embedding_id': embedding.embedding_id,
                    'segment_id': embedding.segment_id,
                    'audio_file_id': audio_file_id,
                    'timestamps': timestamp_list,
                    'created_at': embedding.created_at
                }

                embeddings_list.append(embedding_vector)
                labels_list.append(embedding_info)

            print(f"Total embeddings retrieved: {len(embeddings_list)}")
            return embeddings_list, labels_list
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            return [], []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return [], []
        finally:
            session.close()

    def segment_audio_using_embeddings_timestamps(self):
        """
        Segments audio files based on the EmbeddingTimestamps table.
        Each segment is saved with a filename corresponding to its timestamp ID.
        """
        session = SessionLocal()
        try:
            print("Starting audio segmentation using EmbeddingTimestamps.")

            # Retrieve all EmbeddingTimestamps
            embedding_timestamps = session.query(EmbeddingTimestamp).all()
            if not embedding_timestamps:
                print("No EmbeddingTimestamps found in the database.")
                return

            segmenter = Segmenter()  # Utilize the existing Segmenter class

            for et in embedding_timestamps:
                embedding_id = et.embedding_id
                timestamp_id = et.timestamp_id
                start_time = et.start_time
                end_time = et.end_time

                # Retrieve the associated segment to get the audio file path
                embedding = session.query(Embedding).filter_by(embedding_id=embedding_id).first()
                if not embedding:
                    print(f"Embedding with ID {embedding_id} not found.")
                    continue

                segment = embedding.segment
                if not segment:
                    print(f"Segment associated with Embedding ID {embedding_id} not found.")
                    continue

                audio_file_path = segment.file_path
                audio_folder_path = segment.audio_file.audio_folder_path

                # Define output file path using timestamp_id
                output_filename = f"segment_{timestamp_id}.wav"
                output_file_path = os.path.join(audio_folder_path, "embeddings_segments", output_filename)

                # Ensure the output directory exists
                embeddings_segments_dir = os.path.join(audio_folder_path, "embeddings_segments")
                create_directory_if_not_exists(embeddings_segments_dir)

                # Convert start_time and end_time from seconds to milliseconds
                start_ms = int(start_time * 1000)
                end_ms = int(end_time * 1000)

                # Export the segment
                segmenter.export_segment(
                    input_file=audio_file_path,
                    start_ms=start_ms,
                    end_ms=end_ms,
                    output_file=output_file_path,
                    format="wav"
                )

                print(f"Segmented audio saved as {output_file_path}")

        except Exception as e:
            session.rollback()
            print(f"An error occurred during audio segmentation: {e}")
        finally:
            session.close()