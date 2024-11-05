import numpy as np
from sqlalchemy.orm import Session
from scipy.cluster.hierarchy import linkage, fcluster
from yttrackmyvoice.database import SessionLocal
from yttrackmyvoice.database.models import Embedding, EmbeddingLabel, LabelName

class EmbeddingLabeler:
    def __init__(self, distance_threshold=1):
        """
        Initialize the EmbeddingLabeler with a specified distance threshold for clustering.

        Parameters:
        - distance_threshold (float): The distance threshold for hierarchical clustering.
        """
        self.distance_threshold = distance_threshold

    def cluster_and_label_embeddings(self):
        """
        Clusters embeddings using hierarchical clustering and labels them in the database.
        """
        session = SessionLocal()
        try:
            # Retrieve all embeddings from the database
            embeddings = session.query(Embedding).all()
            if not embeddings:
                print("No embeddings found in the database.")
                return
            
            # Convert embeddings to a NumPy array
            embedding_vectors = np.array([np.frombuffer(embedding.vector, dtype=np.float32) for embedding in embeddings])
            
            # Perform hierarchical clustering using Ward's method
            Z = linkage(embedding_vectors, method='ward')
            
            # Assign cluster labels based on the distance threshold
            clusters = fcluster(Z, self.distance_threshold, criterion='distance')
            
            # Map each unique cluster to a label name
            cluster_to_label = {}
            for cluster_num in np.unique(clusters):
                label_name = f"Speaker {cluster_num}"
                label = session.query(LabelName).filter_by(label_name=label_name).first()
                if not label:
                    label = LabelName(label_name=label_name)
                    session.add(label)
                    session.commit()  # Commit to assign a label_id
                cluster_to_label[cluster_num] = label.label_id
            
            # Update the EmbeddingLabel table with the assigned labels
            for embedding, cluster_label in zip(embeddings, clusters):
                label_id = cluster_to_label[cluster_label]
                
                # Check if the embedding already has this label
                existing_label = session.query(EmbeddingLabel).filter_by(
                    embedding_id=embedding.embedding_id,
                    label_id=label_id
                ).first()
                
                if not existing_label:
                    embedding_label = EmbeddingLabel(
                        embedding_id=embedding.embedding_id,
                        label_id=label_id
                    )
                    session.add(embedding_label)
            
            # Commit all changes to the database
            session.commit()
            print("Embeddings have been successfully clustered and labeled.")
            
        except Exception as e:
            session.rollback()
            print(f"An error occurred during clustering and labeling: {e}")
        finally:
            session.close()