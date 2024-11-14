from yttrackmyvoice.label_embeddings import EmbeddingLabeler
from yttrackmyvoice.database import SessionLocal
from yttrackmyvoice.database.models import LabelName, EmbeddingLabel

class LabelManager:
    def __init__(self):
        self.labeler = EmbeddingLabeler()

    def cluster_and_label_embeddings(self, distance_threshold=1):
        try:
            self.labeler.cluster_and_label_embeddings(distance_threshold=distance_threshold)
        except Exception as e:
            print(f"An error occurred during clustering and labeling: {e}") 