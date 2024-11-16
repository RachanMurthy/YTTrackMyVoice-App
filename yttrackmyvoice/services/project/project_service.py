from yttrackmyvoice.database import SessionLocal
from yttrackmyvoice.database.models import Project
from yttrackmyvoice.utils import create_directory_if_not_exists, get_key
import os

class ProjectService:
    def __init__(self):
        self.session = SessionLocal()

    def create_or_get_project(self, project_name):
        try:
            # Check if the project already exists
            project = self.session.query(Project).filter_by(project_name=project_name).first()

            if project:
                print(f"\nContinuing with the existing project: {project.project_name}\n")
                return project
            else:
                # Create a new project
                project_path = os.path.join(get_key('DATA_DIRECTORY'), project_name)
                new_project = Project(
                    project_name=project_name,
                    description="",
                    project_path=project_path
                )
                create_directory_if_not_exists(project_path)
                print(f"Project Folder ready: {project_path}")

                self.session.add(new_project)
                self.session.commit()
                self.session.refresh(new_project)
                print(f"\nGreat! A new project '{new_project.project_name}' has been created with ID {new_project.project_id}.\n")
                return new_project
        except Exception as e:
            self.session.rollback()
            print(f"\nAn error occurred during project creation: {str(e)}")
            return None
        finally:
            self.session.close()