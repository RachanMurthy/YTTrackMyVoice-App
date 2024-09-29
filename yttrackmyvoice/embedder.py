import os
import time
import pandas as pd
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from pyannote.audio import Pipeline

from .utils import get_key
from .database.models import Segment, Embedding, EmbeddingTimestamp
from .database import SessionLocal
import numpy as np



def store_embedding_and_timestamp(segment_id):
    """
    Processes a given audio segment to extract its embedding and timestamp,
    then stores them in the Embedding and EmbeddingTimestamp models.

    Parameters:
    - segment_id (int): The ID of the segment to process.
    - session (Session): An active SQLAlchemy session.

    Returns:
    - None
    """
    try:
        # 1. Retrieve the Segment from the database
        session = SessionLocal()
        segment = session.query(Segment).filter_by(segment_id=segment_id).first()
        if not segment:
            print(f"Segment with ID {segment_id} not found.")
            return
        
        embeddings = session.query(Embedding).filter_by(segment_id=segment_id).all()
        if embeddings:
            print(f"embeddings found for Segment ID {segment_id}.")
            return 

        audio_file_path = segment.file_path
        print(f"Processing Segment ID: {segment_id}")
        print(f"Audio File Path: {audio_file_path}")

        # 2. Verify the existence of the audio file
        if not os.path.isfile(audio_file_path):
            print(f"Audio file not found at path: {audio_file_path}")
            return

        # 3. Initialize the diarization pipeline
        pipeline = Pipeline.from_pretrained(
            'pyannote/speaker-diarization-3.1',
            use_auth_token=get_key('SECRET_KEY_PYANNOTE')
        )

        # 4. Apply diarization to the audio file
        print("\n\nApplying diarization pipeline...\n")
        diarization, embeddings = pipeline(audio_file_path, return_embeddings=True)

        # 5. Get the list of unique speakers from the diarization labels
        speakers = diarization.labels()

        # 6. Iterate through each speaker and store their embedding and timestamps
        for idx, speaker in enumerate(speakers):
            print(f"\nSpeaker {speaker}'s embedding:\n{embeddings[idx]}\n")
            embedding_vector = embeddings[idx]

            # Convert the embedding vector to bytes for storage
            # Assuming embeddings[idx] is a NumPy array or similar
            embedding_bytes = embedding_vector.tobytes()

            # Create a new Embedding instance
            new_embedding = Embedding(
                segment_id=segment.segment_id,
                vector=embedding_bytes,
                created_at=datetime.now(timezone.utc)
            )
            session.add(new_embedding)
            session.flush()  # Assign embedding_id

            print(f"Created Embedding with ID: {new_embedding.embedding_id}")

            # Iterate through the speech segments of this speaker
            for segment_obj, track, spkr in diarization.itertracks(yield_label=True):
                if spkr == speaker:
                    segment_start = segment_obj.start
                    segment_end = segment_obj.end
                    print(f"Speaker {speaker} speaks from {segment_start:.1f}s to {segment_end:.1f}s")

                    # Create a new EmbeddingTimestamp instance
                    new_timestamp = EmbeddingTimestamp(
                        embedding_id=new_embedding.embedding_id,
                        start_time=segment_start,
                        end_time=segment_end,
                        created_at=datetime.now(timezone.utc)
                    )
                    session.add(new_timestamp)

        # 7. Commit all changes
        try:
            session.commit()
            print(f"Successfully stored embeddings and timestamps for segment_id {segment_id}.")
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error occurred: {e}")
        except Exception as e:
            session.rollback()
            print(f"An unexpected error occurred: {e}")

    except Exception as e:
        print(f"An error occurred while processing segment {segment_id}: {e}")


def retrieve_embeddings(segment_id):
    """
    Retrieves all embeddings and their corresponding timestamps for a given segment_id.

    Parameters:
    - segment_id (int): The ID of the segment to retrieve embeddings for.
    - session (Session): An active SQLAlchemy session.

    Returns:
    - List[Dict]: A list of dictionaries, each containing:
        - 'embedding_id' (int): The ID of the embedding.
        - 'vector' (np.ndarray): The embedding vector as a NumPy array.
        - 'timestamps' (List[Dict]): A list of timestamps with 'start_time' and 'end_time'.
    """
    try:
        print(f"Retrieving embeddings for Segment ID: {segment_id}")

        # 1. Retrieve the Segment from the database
        session = SessionLocal()
        segment = session.query(Segment).filter_by(segment_id=segment_id).first()
        if not segment:
            print(f"Segment with ID {segment_id} not found.")
            return []

        # 2. Retrieve all Embeddings associated with the segment
        embeddings = session.query(Embedding).filter_by(segment_id=segment_id).all()
        if not embeddings:
            print(f"No embeddings found for Segment ID {segment_id}.")
            return []

        # 3. Prepare the list to hold embedding data
        embedding_data = []

        for embedding in embeddings:
            print(f"\nProcessing Embedding ID: {embedding.embedding_id}")

            # 3.1. Convert the binary vector back to a NumPy array
            embedding_vector = np.frombuffer(embedding.vector, dtype=np.float32)  # Adjust dtype if necessary
            print(f"Embedding vector shape: {embedding_vector.shape}")

            # 3.2. Retrieve associated timestamps
            timestamps = session.query(EmbeddingTimestamp).filter_by(embedding_id=embedding.embedding_id).all()

            timestamp_list = []
            for ts in timestamps:
                timestamp_info = {
                    'start_time': ts.start_time,
                    'end_time': ts.end_time,
                    'created_at': ts.created_at
                }
                timestamp_list.append(timestamp_info)
                print(f" - Timestamp: {ts.start_time:.1f}s to {ts.end_time:.1f}s")

            # 3.3. Append the embedding and its timestamps to the list
            embedding_entry = {
                'embedding_id': embedding.embedding_id,
                'vector': embedding_vector,
                'timestamps': timestamp_list,
                'created_at': embedding.created_at
            }
            embedding_data.append(embedding_entry)

        print(f"\nTotal embeddings retrieved: {len(embedding_data)}")
        return embedding_data

    except SQLAlchemyError as e:
        print(f"Database error occurred: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
    

def retrieve_embeddings_df(segment_id):
    """
    Retrieves all embeddings and their corresponding timestamps for a given segment_id
    and returns them as a pandas DataFrame.

    Parameters:
    - segment_id (int): The ID of the segment to retrieve embeddings for.

    Returns:
    - pd.DataFrame: A DataFrame containing embeddings and their timestamps.
    """
    try:
        print(f"Retrieving embeddings for Segment ID: {segment_id}")

        # 1. Retrieve the Segment from the database
        session = SessionLocal()
        segment = session.query(Segment).filter_by(segment_id=segment_id).first()
        if not segment:
            print(f"Segment with ID {segment_id} not found.")
            return pd.DataFrame()

        # 2. Retrieve all Embeddings associated with the segment
        embeddings = session.query(Embedding).filter_by(segment_id=segment_id).all()
        if not embeddings:
            print(f"No embeddings found for Segment ID {segment_id}.")
            return pd.DataFrame()

        # 3. Prepare lists to hold data for the DataFrame
        data = []

        for embedding in embeddings:
            print(f"\nProcessing Embedding ID: {embedding.embedding_id}")

            # 3.1. Convert the binary vector back to a NumPy array
            embedding_vector = np.frombuffer(embedding.vector, dtype=np.float32)  # Adjust dtype if necessary
            print(f"Embedding vector shape: {embedding_vector.shape}")

            # 3.2. Retrieve associated timestamps
            timestamps = session.query(EmbeddingTimestamp).filter_by(embedding_id=embedding.embedding_id).all()

            for ts in timestamps:
                data.append({
                    'embedding_id': embedding.embedding_id,
                    'segment_id': segment_id,
                    'vector': embedding_vector,
                    'start_time': ts.start_time,
                    'end_time': ts.end_time,
                    'embedding_created_at': embedding.created_at,
                    'timestamp_created_at': ts.created_at
                })
                print(f" - Timestamp: {ts.start_time:.1f}s to {ts.end_time:.1f}s")

        # 4. Create a pandas DataFrame from the data
        df = pd.DataFrame(data)
        print(f"\nTotal embeddings retrieved: {len(df)}")
        return df

    except SQLAlchemyError as e:
        print(f"Database error occurred: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return pd.DataFrame()
