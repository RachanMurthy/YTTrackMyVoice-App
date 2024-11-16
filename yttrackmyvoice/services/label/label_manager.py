from yttrackmyvoice.services.label.label_service import LabelService
from yttrackmyvoice.services.label.clustering_service import ClusteringService

class LabelManager:
    def __init__(self):
        self.label_service = LabelService()
        self.clustering_service = ClusteringService()

    def list_labels(self):
        self.label_service.list_labels()

    def update_label_name(self, old_label_name, new_label_name):
        self.label_service.update_label_name(old_label_name, new_label_name)

    def get_label_info(self, label_name):
        self.label_service.get_label_info(label_name)

    def cluster_and_label_embeddings(self, distance_threshold=1.0):
        self.clustering_service.cluster_and_label_embeddings(distance_threshold)