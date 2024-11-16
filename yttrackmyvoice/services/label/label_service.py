from yttrackmyvoice.database import SessionLocal
from yttrackmyvoice.database.models import LabelName, EmbeddingLabel, EmbeddingTimestamp
from sqlalchemy.exc import SQLAlchemyError

class LabelService:
    def list_labels(self):
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
        session = SessionLocal()
        try:
            label = session.query(LabelName).filter_by(label_name=old_label_name).first()
            if not label:
                print(f"Label '{old_label_name}' does not exist.")
                return

            existing_label = session.query(LabelName).filter_by(label_name=new_label_name).first()
            if existing_label:
                print(f"Label name '{new_label_name}' is already in use.")
                return

            label.label_name = new_label_name
            session.commit()
            print(f"Label name updated from '{old_label_name}' to '{new_label_name}'.")
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error occurred while updating label name: {e}")
        finally:
            session.close()

    def get_label_info(self, label_name):
        session = SessionLocal()
        try:
            label = session.query(LabelName).filter_by(label_name=label_name).first()
            if not label:
                print(f"Label '{label_name}' does not exist.")
                return

            embedding_labels = session.query(EmbeddingLabel).filter_by(label_id=label.label_id).all()
            if not embedding_labels:
                print(f"No embeddings found for label '{label_name}'.")
                return

            embedding_ids = [el.embedding_id for el in embedding_labels]
            embedding_timestamps = session.query(EmbeddingTimestamp).filter(
                EmbeddingTimestamp.embedding_id.in_(embedding_ids)
            ).all()

            if not embedding_timestamps:
                print(f"No timestamps found for label '{label.label_name}'.")
                return

            for info in embedding_timestamps:
                print(f"Title: {info.embedding.audio_file.title}")
                print(f"Audio ID: {info.embedding.audio_file.audio_id}")
                print(f"Segment ID: {info.embedding.segment_id}")
                print(f"Start Time: {info.start_time:.2f}s")
                print(f"End Time: {info.end_time:.2f}s")
                print("-" * 60)

        except SQLAlchemyError as e:
            print(f"Database error occurred while retrieving label info: {e}")
        finally:
            session.close() 