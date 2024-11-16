from yttrackmyvoice.services.project.project_service import ProjectService
from yttrackmyvoice.utils import create_directory_if_not_exists, get_key

class ProjectManager:
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


    def initialize_project(self):
        """
        Create a new project if it doesn't exist, or continue with the existing project.
        This method is called during initialization.
        """
        project_service = ProjectService()
        self.project = project_service.create_or_get_project(self.project_name)

        return self.project